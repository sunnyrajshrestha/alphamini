import asyncio
import logging
from asyncio.futures import Future

import enum
from google.protobuf import message as _message
from typing import Any, Set, Optional

from mini import MoveRobotDirection, MiniApiResultType, MouthLampMode, \
    MouthLampColor, ServicePlatform, LanType
from mini.pb2.codemao_faceanalyze_pb2 import FaceAnalyzeResponse
from mini.pb2.codemao_facedetect_pb2 import FaceDetectResponse
from mini.pb2.codemao_facerecognise_pb2 import FaceRecogniseResponse
from mini.pb2.codemao_getaudiolist_pb2 import GetAudioListResponse
from mini.pb2.codemao_getinfrareddistance_pb2 import GetInfraredDistanceResponse
from mini.pb2.codemao_getregisterfaces_pb2 import GetRegisterFacesResponse
from mini.pb2.codemao_recogniseobject_pb2 import RecogniseObjectResponse
from mini.pb2.codemao_speechrecognise_pb2 import SpeechRecogniseResponse
from mini.pb2.codemao_takepicture_pb2 import TakePictureResponse
from .channels.websocket_client import AbstractMsgHandler as _AbstractMsgHandler
from .channels.websocket_client import ubt_websocket as _websocket
from .dns.dns_browser import WiFiDeviceListener, WiFiDevice
from .dns.dns_browser import browser as _browser

_log = logging.getLogger(__name__)
_log.addHandler(logging.StreamHandler())
if _log.level == logging.NOTSET:
    _log.setLevel(logging.INFO)

browser = _browser()
websocket = _websocket()


def set_log_level(level: int, save_file: str = None):
    """设置sdk日志级别

    Args:
        level: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
        save_file: 需要保存到文件的, 填写日志文件路径

    """
    _log.setLevel(level)

    from .dns.dns_browser import log as log1
    log1.setLevel(level)

    from .channels.websocket_client import log as log2
    log2.setLevel(level)

    from .dns.zeroconf import log as log3
    log3.setLevel(level)
    log3.addHandler(logging.StreamHandler())

    if save_file is not None:
        file_handler = logging.FileHandler(save_file)
        _log.addHandler(file_handler)
        log1.addHandler(file_handler)
        log2.addHandler(file_handler)


@enum.unique
class RobotType(enum.Enum):
    """
    机器人产品类型
    """
    DEDU = 1
    """
    悟空国内教育版
    """
    MINI = 2
    """
    悟空标准版
    """
    EDU = 3
    """悟空海外教育版
    """
    KOR = 4
    """悟空韩国版
    """


def set_robot_type(robot: RobotType):
    """设置要链接的机器人产品类型

    Args:
        robot: 取值为: RobotType.DEDU , RobotType.MINI, RobotType.EDU, RobotType.KOR

    """
    if robot == RobotType.MINI:
        from .dns import dns_browser
        dns_browser.service_type = "_Mini_mini_channel_server._tcp.local."
    elif robot == RobotType.DEDU:
        from .dns import dns_browser
        dns_browser.service_type = "_Dedu_mini_channel_server._tcp.local."
    elif robot == RobotType.EDU:
        from .dns import dns_browser
        dns_browser.service_type = "_Edu_mini_channel_server._tcp.local."
    elif robot == RobotType.KOR:
        from .dns import dns_browser
        dns_browser.service_type = "_Kor_mini_channel_server._tcp.local."
    else:
        print(f"不支持的机器人产品类型")


class _GetWiFiDeviceListListener(WiFiDeviceListener):
    """批量获取机器人设备监听类

    Args:
        devices: Set[WiFiDevice] or None
    """
    devices: Set[WiFiDevice]

    def __init__(self, devices):
        self.devices: Set[WiFiDevice] = devices or set()

    def on_device_updated(self, device: WiFiDevice) -> None:
        """
        机器人设备更新了
        Args:
            device: WiFiDevice
        """
        self.devices.update([device])

    def on_device_removed(self, device: WiFiDevice) -> None:
        """
        机器人设备从局域网中移除了
        Args:
            device: WFiDevice
        """
        self.devices.remove(device)

    def on_device_found(self, device: WiFiDevice) -> None:
        """
        扫描到一个机器人设备
        Args:
            device: WFiDevice
        """
        self.devices.add(device)


async def _get_user_input(devices: tuple) -> int:
    try:
        i: int = 0
        for device in devices:
            print('{0}.{1}'.format(i, device))
            i += 1
        num_text = input(f'请输入选择连接的机器人序号:')
    except Exception as e:
        raise e
    else:
        return int(num_text)


def _start_scan(loop: asyncio.AbstractEventLoop, name: str) -> Future:
    """
    开启一个扫描机器人设备的Future
    Args:
        loop: 当前事件loop
        name: 指定设备名称

    Returns:
        asyncio.Future
    """
    fut = loop.create_future()

    class _InnerLister(WiFiDeviceListener):

        @staticmethod
        def set_result(future: Future, device: WiFiDevice):
            if future.cancelled() or future.done():
                return
            _log.info(f"found device : {device}")
            future.set_result(device)

        def on_device_found(self, device: WiFiDevice) -> None:
            if device.name.endswith(name):
                if fut.cancelled() or fut.done():
                    return
                loop.run_in_executor(None, browser.stop_scan)
                loop.call_soon(_InnerLister.set_result, fut, device)

        def on_device_updated(self, device: WiFiDevice) -> None:
            if device.name.endswith(name):
                if fut.cancelled() or fut.done():
                    return
                loop.run_in_executor(None, browser.stop_scan)
                loop.call_soon(_InnerLister.set_result, fut, device)

        def on_device_removed(self, device: WiFiDevice) -> None:
            if device.name.endswith(name):
                if fut.cancelled() or fut.done():
                    return
                loop.call_soon(_InnerLister.set_result, fut, device)

    _log.info("start scanning...")
    browser.add_listener(_InnerLister())
    browser.start_scan(0)

    return fut


async def _get_device_by_name(name: str, timeout: int) -> Optional[WiFiDevice]:
    """
    获取当前局域网内，指定名字的机器人设备信息
    Args:
        name: 设备序列号
        timeout: 扫描超时时间

    Returns:
        Optional[WiFiDevice]
    """

    async def start_scan_async():
        return await _start_scan(asyncio.get_running_loop(), name)

    try:
        device: WiFiDevice = await asyncio.wait_for(start_scan_async(), timeout)
        return device
    except asyncio.TimeoutError:
        _log.warning(f'scan device timeout')
        return None
    finally:
        browser.stop_scan()
        _log.info("stop scan finished.")


async def _get_device_list(timeout: int) -> tuple:
    """
    获取当前局域网内所有机器人设备信息
    Args:
        timeout: 超时时间

    Returns:
        Optional[WiFiDevice]
    """
    devices: Set[WiFiDevice] = set()
    browser.add_listener(_GetWiFiDeviceListListener(devices))
    browser.start_scan(0)
    await asyncio.sleep(timeout)
    browser.remove_all_listener()
    browser.stop_scan()
    return tuple(devices)


async def _connect(device: WiFiDevice) -> bool:
    """
    连接机器人设备

    Args:
        device (WiFiDevice): 指定机器人设备对象

    Returns:
        bool: 是否连接设备成功

    """
    return await websocket.connect(device.address)


def _register_msg_handler(cmd: int, handler: _AbstractMsgHandler):
    """
    注册命令监听器

    Args:
        cmd: 支持的命令请查看: mini.apis.cmdid
        handler: 命令处理器

    """
    websocket.register_msg_handler(cmd, handler)


def _unregister_msg_handler(cmd: int, handler: _AbstractMsgHandler):
    """
    反注册命令监听器

    Args:
        cmd: 支持的命令请查看: mini.apis.cmdid
        handler: 命令处理器
    """
    websocket.unregister_msg_handler(cmd, handler)


async def _send_msg(cmd: int, message: _message.Message, timeout: int) -> Any:
    """
    发送一个消息给机器人

    Args:
        cmd:支持的命令请查看: mini.apis.cmdid
        message:  消息类在: mini.pb2 包内
        timeout: 超时时间
    """
    return await websocket.send_msg(cmd, message, timeout)


async def _release():
    """
    断开链接，释放资源
    """
    await websocket.shutdown()


# -----------------------------------------------------------------#
async def get_device_by_name(name: str, timeout: int) -> Optional[WiFiDevice]:
    """
    获取当前局域网内，指定名字的机器人设备信息

    Args:
        name: 设备序列号
        timeout: 扫描超时时间

    Returns:
        Optional[WiFiDevice]
    """
    return await _get_device_by_name(name, timeout)


async def get_device_list(timeout: int) -> tuple:
    """获取当前局域网内所有机器人设备信息

    Args:
        timeout: 超时时间

    Returns:
        Optional[WiFiDevice]
    """
    return await _get_device_list(timeout)


async def connect(device: WiFiDevice) -> bool:
    """连接机器人设备

    Args:
        device (WiFiDevice): 指定机器人设备对象

    Returns:
        bool: 是否连接设备成功
    """
    return await _connect(device)


async def release():
    """
    断开链接，释放资源
    """
    await _release()


async def enter_program() -> bool:
    """进入编程模式api

        机器人进入编程模式

    Returns:
        bool
    """

    from mini.apis.api_setup import StartRunProgram
    (resultType, response) = await StartRunProgram().execute()
    await asyncio.sleep(6)
    return resultType == MiniApiResultType.Success and response.isSuccess


async def quit_program() -> bool:
    """退出编程模式api

            机器人退出编程模式

        Returns:
            bool
        """

    from mini.apis.api_setup import StopRunProgram
    return await StopRunProgram(is_serial=False).execute()


async def play_action(action_name: str = None) -> bool:
    """执行内置动作api

        机器人执行一个指定名称的内置动作

        动作名称可用get_action_list获取

    Args:
        action_name (str): 动作名称

    Returns:
        bool
    """
    from mini.apis.api_action import PlayAction
    block: PlayAction = PlayAction(True, action_name)
    (resultType, response) = await block.execute()
    _log.info(f'play_action result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def stop_action() -> bool:
    """停止动作

        如果动作是一个不可打断的动作, stop_action返回False

        Returns:
            bool
    """
    from mini.apis.api_action import StopAllAction
    block: StopAllAction = StopAllAction()
    (resultType, response) = await block.execute()
    _log.info(f'stop_action result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def play_custom_action(action_name: str = None) -> bool:
    """执行自定义动作api

    让机器人执行一个指定名称的自定义动作, 并等待结果

    动作名称可用get_custom_action_list获取

    Args:
        action_name (str): 自定义动作名称

    Returns:
        bool
    """
    from mini.apis.api_action import PlayCustomAction
    block: PlayCustomAction = PlayCustomAction(True, action_name)
    (resultType, response) = await block.execute()
    _log.info(f'play_custom_action result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def stop_custom_action() -> bool:
    """停止自定义动作

        如果动作是一个不可打断的动作, stop_action返回False

    Returns:
        bool
    """

    from mini.apis.api_action import StopCustomAction
    block: StopCustomAction = StopCustomAction()
    (resultType, response) = await block.execute()
    _log.info(f'stop_custom_action result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def move(direction: MoveRobotDirection = MoveRobotDirection.FORWARD,
               step: int = 1) -> bool:
    """控制机器人移动

        控制机器人往左(LEFTWARD)移动10步，并等待执行结果

    Args:
        direction (MoveRobotDirection): 方向
        step (int): 步数

    Returns:
        bool
    """

    from mini.apis.api_action import MoveRobot
    block: MoveRobot = MoveRobot(True, direction, step)
    (resultType, response) = await block.execute()
    _log.info(f'move result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def get_action_list() -> list:
    """获取取动作列表

        获取机器人系统内置的动作列表，等待回复结果

    Returns:
        [] : 动作列表
    """
    from mini.apis.api_action import GetActionList
    from mini import RobotActionType
    block: GetActionList = GetActionList(True, RobotActionType.INNER)
    (resultType, response) = await block.execute()
    if resultType == MiniApiResultType.Success and response.isSuccess:
        return response.actionList
    else:
        return []


async def get_custom_action_list() -> list:
    """获取自定义动作列表

        获取机器人/sdcard/customize/actions下的动作列表，等待回复结果

    Returns:
        [] : 自定义动作列表
    """

    from mini.apis.api_action import GetActionList
    from mini import RobotActionType
    block: GetActionList = GetActionList(True, RobotActionType.INNER)
    (resultType, response) = await block.execute()
    if resultType == MiniApiResultType.Success and response.isSuccess:
        return response.actionList
    else:
        return []


async def wiki(query: str) -> bool:
    """查询百科demo

        查询百科，例如：查询内容"优必选"，并等待结果，机器人播报查询结果

    Args:
        query (str): 查询关键字

    Returns:
        bool
    """

    from mini.apis.api_content import QueryWiKi
    block: QueryWiKi = QueryWiKi(True, query)
    (resultType, response) = await block.execute()
    _log.info(f'wiki result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def translate(query: str,
                    from_lan: LanType = None, to_lan: LanType = None,
                    platform: ServicePlatform = ServicePlatform.BAIDU) -> bool:
    """翻译

        例如:使用百度翻译，把"张学友"，从中文翻译成英文，并等待结果，机器人播报翻译结果:

        translate(query="张学友",from_lan=CN,to_lan=EN,platform=BAIDU )

    Args:
        query (str): 关键字
        from_lan (LanType): 源语言
        to_lan (LanType): 目标语言
        platform (ServicePlatform): BAIDU, GOOGLE, TENCENT

    Returns:
        bool
    """

    from mini.apis.api_content import StartTranslate
    block: StartTranslate = StartTranslate(True, query, from_lan=from_lan, to_lan=to_lan, platform=platform)
    (resultType, response) = await block.execute()
    _log.info(f'translate result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def play_expression(express_name: str) -> bool:
    """播放表情

        让机器人播放一个express_name的内置表情，并等待回复结果

    Args:
        express_name (str): 表情文件名,如:"codemao1"
    Returns:
        bool
    """

    from mini.apis.api_expression import PlayExpression
    block: PlayExpression = PlayExpression(True, express_name)
    (resultType, response) = await block.execute()
    _log.info(f'play expression result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def play_behavior(behavior_name: str) -> bool:
    """播放舞蹈

        让机器人开始跳一个名为behavior_name的舞蹈，并等待回复结果

    Args:
        behavior_name (str): 例如"dance_0004"

    Returns:
        bool
    """

    from mini.apis.api_behavior import StartBehavior
    block: StartBehavior = StartBehavior(True, behavior_name)
    (resultType, response) = await block.execute()
    _log.info(f'play behavior result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def stop_behavior() -> bool:
    """停止正在播放的舞蹈

    Returns:
        bool
    """
    from mini.apis.api_behavior import StopBehavior
    block: StopBehavior = StopBehavior(True)
    (resultType, response) = await block.execute()
    _log.info(f'stop behavior result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def set_MouthLamp_NormalMode(color: MouthLampColor = MouthLampColor.RED, duration: int = 1000) -> bool:
    """
    设置嘴巴灯常亮模式，并等待结果

    Args:
        color (MouthLampColor): 嘴巴灯颜色，默认RED
        duration (int): 单位ms，持续时间

    Returns:
        bool

    """
    return await _set_mouthlamp_mode(mode=MouthLampMode.NORMAL, color=color, duration=duration)


async def set_MouthLamp_BreathMode(breath_duration: int = 1000,
                                   color: MouthLampColor = MouthLampColor.RED, duration: int = 1000) -> bool:
    """
    设置嘴巴灯呼吸模式，并等待结果

    Args:
        breath_duration (int): 单位ms，呼吸一次的时长
        color (MouthLampColor): 嘴巴灯颜色，默认RED
        duration (int): 单位ms，持续时间


    Returns:
        bool
    """
    return await _set_mouthlamp_mode(mode=MouthLampMode.BREATH, breath_duration=breath_duration, color=color,
                                     duration=duration)


async def _set_mouthlamp_mode(mode: MouthLampMode = MouthLampMode.NORMAL, color: MouthLampColor = MouthLampColor.RED,
                              duration: int = 1000, breath_duration: int = 1000) -> bool:
    """设置嘴巴灯模式

        设置机器人嘴巴灯正常模式、绿色、常亮3s，并等待回复结果

        当mode=NORMAL时，duration参数起作用，表示常亮多久时间

        当mode=BREATH，breath_duration参数表示多久呼吸一次

        设置生效后，机器人会立即返回设置结果(与设置的duration参数无关)

    Args:
        mode: 嘴巴灯模式，0：普通模式，1：呼吸模式
        color: 嘴巴灯颜色，1：红色，2：绿色，3：蓝色
        duration: 持续时间，单位为毫秒，-1表示常亮
        breath_duration: 闪烁一次时长，单位为毫秒

    Returns:
        bool
    """

    from mini.apis.api_expression import SetMouthLamp
    block: SetMouthLamp = SetMouthLamp(True, mode, color, duration, breath_duration)
    (resultType, response) = await block.execute()
    _log.info(f'set MouthLamp mode result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def switch_MouthLamp(is_open: bool = True) -> bool:
    """开关嘴巴灯

        开关机器人嘴巴灯，并等待结果

    Args:
        is_open: bool

    Returns:
        bool
    """

    from mini.apis.api_expression import ControlMouthLamp
    block: ControlMouthLamp = ControlMouthLamp(True, is_open)
    (resultType, response) = await block.execute()
    _log.info(f'switch MouthLamp result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def play_tts(text: str) -> bool:
    """播放tts

        使机器人开始播放一段tts，并等待结果

    Args:
        text: str, 例如:"你好， 我是悟空， 啦啦啦"，

    Returns:
        bool
    """

    from mini.apis.api_sound import StartPlayTTS
    block: StartPlayTTS = StartPlayTTS(True, text)
    (resultType, response) = await block.execute()
    _log.info(f'play tts result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def stop_tts() -> bool:
    """停止语音合成播报, 并等待结果

    Returns:
        bool
    """

    from mini.apis.api_sound import StopPlayTTS
    block: StopPlayTTS = StopPlayTTS(True)
    (resultType, response) = await block.execute()
    _log.info(f'stop tts result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def play_online_audio(url: str) -> bool:
    """播放在线音效

        使机器人播放一段在线音效，

        并等待结果

    Args:
        url: str, 例如:http://yun.lnpan.com/music/download/ring/000/075/5653bae83917a892589b372782175dd8.amr
             支持格式有mp3,amr,wav 等
    Returns:
        bool
    """

    from mini import AudioStorageType
    from mini.apis.api_sound import PlayAudio
    block: PlayAudio = PlayAudio(True,
                                 url,
                                 AudioStorageType.NET_PUBLIC)
    (resultType, response) = await block.execute()
    _log.info(f'play online audio result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def play_local_audio(local_file: str) -> bool:
    """播放本地音效

        使机器人播放一段本地内置音效，音效名称为"read_016"，并等待结果

    Args:
        local_file:

    Returns:
        bool
    """

    from mini.apis.api_sound import PlayAudio
    from mini import AudioStorageType
    block: PlayAudio = PlayAudio(True,
                                 local_file,
                                 AudioStorageType.PRESET_LOCAL)
    (resultType, response) = await block.execute()
    _log.info(f'play local audio result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def stop_audio() -> bool:
    """停止所有正在播放的音频

        停止所有所有音效，并等待结果

    Returns:
        bool
    """

    from mini.apis.api_sound import StopAllAudio
    block: StopAllAudio = StopAllAudio(True)
    (resultType, response) = await block.execute()
    _log.info(f'stop audio result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def get_system_audio_list() -> GetAudioListResponse:
    """获取音效列表

        获取机器人内置的音效列表，并等待结果

        #GetAudioListResponse.audio ([Audio]) : 音效列表

            #Audio.name : 音效名

            #Audio.suffix : 音效后缀

        #GetAudioListResponse.isSuccess : 是否成功

        #GetAudioListResponse.resultCode : 返回码

    Returns:
        GetAudioListResponse
    """

    from mini.apis.api_sound import FetchAudioList
    from mini import AudioSearchType
    block: FetchAudioList = FetchAudioList(True, search_type=AudioSearchType.INNER)
    (resultType, response) = await block.execute()
    _log.info(f'stop audio result:{response}')
    return response


async def get_custom_audio_list() -> GetAudioListResponse:
    """获取音效列表

        获取机器人开发者放置在/sdcard/customize/music/下的音效列表，并等待结果

        #GetAudioListResponse.audio ([Audio]) : 音效列表

            #Audio.name : 音效名

            #Audio.suffix : 音效后缀

        #GetAudioListResponse.isSuccess : 是否成功

        #GetAudioListResponse.resultCode : 返回码

    Returns:
        GetAudioListResponse
    """

    from mini.apis.api_sound import FetchAudioList
    from mini import AudioSearchType
    block: FetchAudioList = FetchAudioList(True, search_type=AudioSearchType.CUSTOM)
    (resultType, response) = await block.execute()
    _log.info(f'stop audio result:{response}')
    return response


async def change_volume(volume: float = 0.5) -> bool:
    """调整机器人音量demo

        设置机器人音量为0~1，等待回复结果

    Args:
        volume: float 默认0.5

    Returns:
        bool
    """

    from mini.apis.api_sound import ChangeRobotVolume
    block: ChangeRobotVolume = ChangeRobotVolume(True, volume)
    (resultType, response) = await block.execute()
    _log.info(f'change volume result:{response}')
    return resultType == MiniApiResultType.Success and response.isSuccess


async def face_detect() -> FaceDetectResponse:
    """人脸个数侦测

        做一次人脸个数侦测，并等待回复结果

        #FaceDetectResponse.count : 人脸个数

        #FaceDetectResponse.isSuccess : 是否成功

        #FaceDetectResponse.resultCode : 返回码

    Returns:
        FaceDetectResponse
    """

    from mini.apis.api_sence import FaceDetect
    block: FaceDetect = FaceDetect(True, 10)
    (resultType, response) = await block.execute()
    _log.info(f'face detect result:{response}')
    return response


async def face_analysis() -> FaceAnalyzeResponse:
    """人脸分析（性别）

        做一次人脸信息(性别、年龄)侦测，并等待回复结果

        当多人存在摄像头前时，返回占画面比例最大的那个人脸信息

        返回值：示例 {"age": 24, "gender": 99, "height": 238, "width": 238}

                age: 年龄

                gender：[1, 100], 小于50为女性，大于50为男性

                height：人脸在摄像头画面中的高度

                width：人脸在摄像头画面中的宽度

        #FaceAnalyzeResponse.faceInfos : 人脸信息数组[FaceInfoResponse]

        #FaceInfoResponse.gender (int) :[1,100],小于50为女性，大于50为男性

        #FaceInfoResponse.age : 年龄

        #FaceInfoResponse.width : 人脸在摄像头画面中的宽度

        #FaceInfoResponse.height : 人脸在摄像头画面中的高度

        #FaceAnalyzeResponse.isSuccess : 是否成功

        #FaceAnalyzeResponse.resultCode : 返回码

    Returns:
        FaceAnalyzeResponse
    """

    from mini.apis.api_sence import FaceAnalysis
    block: FaceAnalysis = FaceAnalysis(True, 10)
    (resultType, response) = await block.execute()
    _log.info(f'face analysis result:{response}')
    return response


async def face_recognise() -> FaceRecogniseResponse:
    """人脸识别

        做一次人脸识别检测，并等待结果

        #FaceRecogniseResponse.faceInfos : [FaceInfoResponse] 人脸信息数组

            #FaceInfoResponse.id : 人脸id

            #FaceInfoResponse.name : 姓名，如果是陌生人，则默认name为"stranger"

            #FaceInfoResponse.gender : 性别

            #FaceInfoResponse.age : 年龄

        #FaceRecogniseResponse.isSuccess : 是否成功

        #FaceRecogniseResponse.resultCode : 返回码

    Returns:
        RecogniseObjectResponse
    """

    from mini.apis.api_sence import FaceRecognise
    (resultType, response) = await FaceRecognise(True, 10).execute()
    _log.info(f'face recognise result:{response}')
    return response


async def flower_recognise() -> RecogniseObjectResponse:
    """花草识别

        让机器人做一次花草识别, (需手动把花或花的照片放到机器人面前)，并等待结果

        #RecogniseObjectResponse.objects : 识别结果数组[str]

        #RecogniseObjectResponse.isSuccess : 是否成功

        #RecogniseObjectResponse.resultCode : 返回码

    Returns:
        RecogniseObjectResponse
    """

    from mini.apis.api_sence import ObjectRecognise
    from mini import ObjectRecogniseType
    block: ObjectRecognise = ObjectRecognise(True, ObjectRecogniseType.FLOWER, 10)
    (resultType, response) = await block.execute()
    _log.info(f'flower_recognise result:{response}')
    return response


async def fruit_recognise() -> RecogniseObjectResponse:
    """水果识别

        让机器人做一次水果识别, (需手动把水果或水果的照片放到机器人面前)，并等待结果

        #RecogniseObjectResponse.objects : 识别结果数组[str]

        #RecogniseObjectResponse.isSuccess : 是否成功

        #RecogniseObjectResponse.resultCode : 返回码

    Returns:
        RecogniseObjectResponse
    """

    from mini.apis.api_sence import ObjectRecognise
    from mini import ObjectRecogniseType
    block: ObjectRecognise = ObjectRecognise(True, ObjectRecogniseType.FRUIT, 10)
    (resultType, response) = await block.execute()
    _log.info(f'fruit_recognize result:{response}')
    return response


async def gesture_recognise() -> RecogniseObjectResponse:
    """手势识别

        让机器人做一次用户手势识别, (需在机器人面前作出手势)，并等待结果

        #RecogniseObjectResponse.objects : 识别结果数组[str]

        #RecogniseObjectResponse.isSuccess : 是否成功

        #RecogniseObjectResponse.resultCode : 返回码

    Returns:
        RecogniseObjectResponse
    """

    from mini.apis.api_sence import ObjectRecognise
    from mini import ObjectRecogniseType
    block: ObjectRecognise = ObjectRecognise(True, ObjectRecogniseType.GESTURE, 10)
    (resultType, response) = await block.execute()
    _log.info(f'gesture_recognize result:{response}')
    return response


async def take_picture_immediately() -> TakePictureResponse:
    """拍照

        让机器人立即拍照，并等待结果

        #TakePictureResponse.isSuccess : 是否成功

        #TakePictureResponse.code : 返回码

        #TakePictureResponse.picPath : 照片在机器人里的存储路径

    Returns:
        TakePictureResponse
    """

    from mini.apis.api_sence import TakePicture
    from mini import TakePictureType
    (resultType, response) = await TakePicture(take_picture_type=TakePictureType.IMMEDIATELY).execute()
    _log.info(f'take picture immediately result:{response}')
    return response


async def take_picture() -> TakePictureResponse:
    """拍照

        让机器人查找人脸后再拍照，并等待结果

        #TakePictureResponse.isSuccess : 是否成功

        #TakePictureResponse.code : 返回码

        #TakePictureResponse.picPath : 照片在机器人里的存储路径

    Returns:
        TakePictureResponse
    """

    from mini.apis.api_sence import TakePicture
    from mini import TakePictureType
    (resultType, response) = await TakePicture(take_picture_type=TakePictureType.FINDFACE).execute()
    _log.info(f'take picture result:{response}')
    return response


async def get_register_faces() -> GetRegisterFacesResponse:
    """获取已注册的人脸信息

        获取在机器人中已注册的所有人脸信息，并等待结果

        #GetRegisterFacesResponse.faceInfos : [FaceInfoResponse] 人脸信息数组

            #FaceInfoResponse.id : 人脸id

            #FaceInfoResponse.name : 姓名

            #FaceInfoResponse.gender : 性别

            #FaceInfoResponse.age : 年龄

        #GetRegisterFacesResponse.isSuccess : 是否成功

        #GetRegisterFacesResponse.resultCode : 返回码

    Returns:
        GetRegisterFacesResponse

    """

    from mini.apis.api_sence import GetRegisterFaces
    (resultType, response) = await GetRegisterFaces().execute()
    _log.info(f'get register faces result:{response}')
    return response


async def get_infrared_distance() -> GetInfraredDistanceResponse:
    """红外距离检测

        获取当前机器人检测到的红外距离，并等待结果

        #GetInfraredDistanceResponse.distance : 红外距离

    Returns:
        GetInfraredDistanceResponse
    """

    from mini.apis.api_sence import GetInfraredDistance
    (resultType, response) = await GetInfraredDistance().execute()
    _log.info(f'get infrared distance result:{response}')
    return response


async def speech_recognise(timeout: int) -> SpeechRecogniseResponse:
    """语音识别api

        机器人在指定时间内，执行语音识别
    Args:
        timeout (int): 超时时间

    Returns:
        bool
    """
    from mini.apis.api_sence import StartSpeechRecognise
    block: StartSpeechRecognise = StartSpeechRecognise(True, timeout)
    (resultType, response) = await block.execute()
    _log.info(f'speech_recognise result:{response}')
    return response
