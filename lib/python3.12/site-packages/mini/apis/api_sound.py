#!/usr/bin/env python3

import enum

from mini.pb2.codemao_speechrecognise_pb2 import SpeechRecogniseRequest, SpeechRecogniseResponse

from ..apis.api_config import ServicePlatform
from ..apis.base_api import BaseApi, DEFAULT_TIMEOUT
from ..apis.cmdid import _PCProgramCmdId
from ..pb2 import cloudstorageurls_pb2
from ..pb2.codemao_changerobotvolume_pb2 import ChangeRobotVolumeRequest, ChangeRobotVolumeResponse
from ..pb2.codemao_controlrobotrecord_pb2 import ControlRobotRecordRequest, ControlRobotRecordResponse
from ..pb2.codemao_controltts_pb2 import ControlTTSRequest, ControlTTSResponse
from ..pb2.codemao_getaudiolist_pb2 import GetAudioListRequest, GetAudioListResponse
from ..pb2.codemao_playaudio_pb2 import PlayAudioRequest, PlayAudioResponse
from ..pb2.codemao_playonlinemusic_pb2 import MusicRequest, MusicResponse
from ..pb2.codemao_stopaudio_pb2 import StopAudioRequest, StopAudioResponse
from ..pb2.pccodemao_message_pb2 import Message


@enum.unique
class TTSControlType(enum.Enum):
    """
    TTS控制类型

    START : 开始播放tts

    STOP : 停止播放tts
    """
    START = 1  # 播放
    STOP = 0  # 停止


class StartPlayTTS(BaseApi):
    """开始播放TTS api

    机器人播放合成的TTS语音

    Args:
        is_serial (bool): 是否等待回复,默认True
        text (str): 播放的文本,不能为空或者None

    #ControlTTSResponse.isSuccess : 是否成功

    #ControlTTSResponse.resultCode : 返回码
    """

    def __init__(self, is_serial: bool = True, text: str = None):
        assert isinstance(text, str) and len(text), 'StartPlayTTS : tts text should be available'
        self.__is_serial = is_serial
        self.__text = text
        self.__type = TTSControlType.START.value

    async def execute(self):
        """
        执行开始播放TTS指令

        Returns:
            ControlTTSResponse

        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = ControlTTSRequest()
        request.text = self.__text
        request.type = self.__type

        cmd_id = _PCProgramCmdId.PLAY_TTS_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ControlTTSResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ControlTTSResponse()
            response.ParseFromString(data)
            return response
        else:
            return None



class StopPlayTTS(BaseApi):
    """停止播放TTS api

    机器人停止播放TTS语音

    Args:
        is_serial (bool): 是否等待回复,默认True

    #ControlTTSResponse.isSuccess : 是否成功

    #ControlTTSResponse.resultCode : 返回码
    """

    def __init__(self, is_serial: bool = True):
        self.__isSerial = is_serial
        self.__type = TTSControlType.STOP.value

    async def execute(self):
        """
        执行停止播放TTS指令

        Returns:
            ControlTTSResponse

        """
        timeout = 0
        if self.__isSerial:
            timeout = DEFAULT_TIMEOUT

        request = ControlTTSRequest()
        request.type = self.__type

        cmd_id = _PCProgramCmdId.PLAY_TTS_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ControlTTSResponse

        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ControlTTSResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class _PlayTTS(BaseApi):
    """播放/停止TTS api

    机器人播放合成的TTS语音

    control_type为STOP时,表示停止所有正在播放的TTS

    Args:
        is_serial (bool): 是否等待回复,默认True
        text (str): 播放的文本,不能为空或者None
        control_type (TTSControlType): 控制类型,默认START,开始播放

    #ControlTTSResponse.isSuccess : 是否成功

    #ControlTTSResponse.resultCode : 返回码
    """

    def __init__(self, is_serial: bool = True, text: str = None, control_type: TTSControlType = TTSControlType.START):
        assert text is not None and len(text), 'tts text should be available'
        self.__isSerial = is_serial
        self.__text = text
        self.__type = control_type.value

    async def execute(self):
        """
        执行控制TTS指令

        Returns:
            ControlTTSResponse
        """
        timeout = 0
        if self.__isSerial:
            timeout = DEFAULT_TIMEOUT

        request = ControlTTSRequest()
        request.text = self.__text
        request.type = self.__type

        cmd_id = _PCProgramCmdId.PLAY_TTS_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ControlTTSResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ControlTTSResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


@enum.unique
class AudioStorageType(enum.Enum):
    """
    音频存储类型

    NET_PUBLIC : 公网

    PRESET_LOCAL : 机器人本地内置

    CUSTOMIZE_LOCAL : 机器人本地自定义

    """
    # ALIYUN_PRIVATE = 1  # 阿里私有云
    NET_PUBLIC = 2  # 公网
    PRESET_LOCAL = 3  # 本地内置
    CUSTOMIZE_LOCAL = 4  # 本地自定义


class PlayAudio(BaseApi):
    """播放音频api

    机器人播放指定的音频, 支持mp3,wav,amr等

    Args:
        is_serial (bool): 是否等待回复,默认True
        url (str): 音频地址,当storage_type为NET_PUBLIC,url为音频文件网址；当storage_type为PRESET_LOCAL/CUSTOMIZE_LOCAL时,
                    url为本地音频名称（本地音频名称可通过FetchAudioList接口获取）
        storage_type (AudioStorageType): 音频存储类型,默认NET_PUBLIC,公网
        volume (float): 音量大小,范围[0.0,1.0],默认1.0

    #PlayAudioResponse.isSuccess : 是否成功

    #PlayAudioResponse.resultCode : 返回码

    """

    def __init__(self, is_serial: bool = True, url: str = None,
                 storage_type: AudioStorageType = AudioStorageType.NET_PUBLIC, volume: float = 1.0):

        assert isinstance(url, str) and len(url), 'PlayAudio : url should be available'
        assert isinstance(volume, float) and 0 <= volume <= 1.0, 'PlayAudio : volume should be in range[0,1]'
        assert isinstance(storage_type, AudioStorageType), 'PlayAudio : storage_type shoule be AudioStorageType ' \
                                                           'instance '
        self.__is_serial = is_serial
        self.__url = url
        self.__volume = volume
        self.__cloudStorageType = storage_type.value

    async def execute(self):
        """
        执行播放音频指令

        Returns:
            PlayAudioResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        cloud = cloudstorageurls_pb2.CloudStorage()
        cloud.type = self.__cloudStorageType
        cloud.url.extend([self.__url])

        request = PlayAudioRequest()

        request.cloud.CopyFrom(cloud)
        request.volume = self.__volume

        cmd_id = _PCProgramCmdId.PLAY_AUDIO_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            PlayAudioResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = PlayAudioResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class StopAllAudio(BaseApi):
    """停止所有音频api

    机器人停止所有正在播放的音频

    Args:
        is_serial (bool): 是否等待回复,默认True

    #StopAudioResponse.isSuccess : 是否成功　

    #StopAudioResponse.resultCode : 返回码

    """

    def __init__(self, is_serial: bool = True):
        self.__is_serial = is_serial

    async def execute(self):
        """
        执行停止所有音频指令

        Returns:
            StopAudioResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = StopAudioRequest()

        cmd_id = _PCProgramCmdId.STOP_AUDIO_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            StopAudioResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = StopAudioResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


@enum.unique
class AudioSearchType(enum.Enum):
    """
    音频查询类型

    INNER(内置) : 机器人内置的不可修改的音效,

    CUSTOM(自定义) : 放置在sdcard/customize/music目录下可被开发者修改的音效
    """
    INNER = 0  # 内置
    CUSTOM = 1  # 自定义


class FetchAudioList(BaseApi):
    """获取机器人的音频列表api

    获取存储在机器人rom或者sdcard中的音频列表

    Args:
        is_serial (bool): 是否等待回复,默认True
        search_type (AudioSearchType): 查询类型,默认INNER,机器人内置

    #GetAudioListResponse.audio ([Audio]) : 音效列表

    #Audio.name : 音效名

    #Audio.suffix : 音效后缀

    #GetAudioListResponse.isSuccess : 是否成功

    #GetAudioListResponse.resultCode : 返回码

    """

    def __init__(self, is_serial: bool = True, search_type: AudioSearchType = AudioSearchType.INNER):
        assert isinstance(search_type, AudioSearchType), 'FetchAudioList : search_type should be AudioSearchType ' \
                                                         'instance '
        self.__is_serial = is_serial
        self.__search_type = search_type.value

    async def execute(self):
        """
        执行获取音频列表指令

        Returns:
            GetAudioListResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = GetAudioListRequest()

        request.searchType = self.__search_type

        cmd_id = _PCProgramCmdId.GET_AUDIO_LIST_REQUEST.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            GetAudioListResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = GetAudioListResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class __PlayOnlineMusic(BaseApi):
    """播放在线歌曲api

    机器人播放QQ音乐在线歌曲,需在app绑定机器人并授权

    Args:
        is_serial (bool): 是否等待回复,默认True
        name (str): 歌曲名称,不能为空或者None

    #MusicResponse.isSuccess : 是否成功

    #MusicResponse.resultCode : 返回码

    """

    def __init__(self, is_serial: bool = True, name: str = None):
        assert name is not None and len(name), 'PlayOnlineMusic name should be available'
        self.__is_serial = is_serial
        self.__name = name
        self.__platform = ServicePlatform.TENCENT.value

    async def execute(self):
        """
        执行播放在线歌曲指令

        Returns:
            MusicResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = MusicRequest()

        request.platform = self.__platform
        request.name = self.__name

        cmd_id = _PCProgramCmdId.PLAY_ONLINE_MUSIC_REQUEST.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            MusicResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = MusicResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class ChangeRobotVolume(BaseApi):
    """设置机器人音量api

    调整机器人音量

    Args:
        is_serial (bool): 是否等待回复,默认True
        volume (float): 音量,范围[0.0,1.0],默认0.5

    #ChangeRobotVolumeResponse.isSuccess : 是否成功

    #ChangeRobotVolumeResponse.resultCode : 返回码

    """

    def __init__(self, is_serial: bool = True, volume: float = 0.5):
        assert isinstance(volume, float) and 0.0 <= volume <= 1.0, 'ChangeRobotVolume : volume should be in range[' \
                                                                   '0.0,1.0] '
        self.__is_serial = is_serial
        self.__volume = volume

    async def execute(self):
        """发送设置机器人音量指令

        Returns:
            ChangeRobotVolumeResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = ChangeRobotVolumeRequest()
        request.volume = self.__volume

        cmd_id = _PCProgramCmdId.CHANGE_ROBOT_VOLUME_REQUEST.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ChangeRobotVolumeResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ChangeRobotVolumeResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


@enum.unique
class RobotAudioRecordControlType(enum.Enum):
    """
    机器人录音控制类型
    """
    START_RECORD = 0  # 开始录音
    STOP_RECORD = 1  # 停止录音
    START_PLAY = 2  # 开始播放
    STOP_PLAY = 3  # 停止播放
    PAUSE_PLAY = 4  # 暂停播放
    CONTINUE_PLAY = 5  # 继续播放
    RENAME_FILE = 6  # 重命名文件


class ControlRobotAudioRecord(BaseApi):
    """控制机器人录音/播放api

    Args:
        is_serial (bool): 是否等待回复,默认True
        control_type (RobotAudioRecordControlType): 控制类型,默认START_RECORD,开始录音
        time_limit (int): 录音时长,单位ms,默认60000ms,即60s
        file_name (str): 录音文件存储名称
        new_file_name (str): 重命名录音文件的名称

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True,
                 control_type: RobotAudioRecordControlType = RobotAudioRecordControlType.START_RECORD,
                 time_limit: int = 60000, file_name: str = None,
                 new_file_name: str = None):
        assert isinstance(control_type, RobotAudioRecordControlType), 'ControlRobotAudioRecord : control_type should ' \
                                                                      'be RobotAudioRecordControlType instance '
        self.__is_serial = is_serial
        self.__control_type = control_type.value
        self.__timeLimit = time_limit
        self.__id = file_name
        self.__newId = new_file_name

    async def execute(self):
        """发送控制录音指令

        Returns:
            ControlRobotRecordResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT
        request = ControlRobotRecordRequest()
        request.type = self.__control_type
        request.timeLimit = self.__timeLimit

        if isinstance(self.__id, str):
            request.id = self.__id

        if isinstance(self.__newId, str):
            request.newId = self.__newId

        cmd_id = _PCProgramCmdId.CONTROL_ROBOT_AUDIO_RECORD.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ControlRobotRecordResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ControlRobotRecordResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class RobotAudioStartRecord(ControlRobotAudioRecord):
    """机器人开始录音api

    控制机器人开始录音

    Args:
        is_serial (bool): 是否等待回复,默认True
        time_limit (int): 录音时长,单位ms,默认60000ms,即60s

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True, time_limit: int = 60000):
        assert isinstance(time_limit, int) and time_limit > 0, f'{self.__class__.__name__}  : time_limit should be ' \
                                                               f'positive '
        ControlRobotAudioRecord.__init__(self, is_serial=is_serial, time_limit=time_limit,
                                         control_type=RobotAudioRecordControlType.START_RECORD)


class RobotAudioStopRecord(ControlRobotAudioRecord):
    """机器人停止录音api

    控制机器人停止录音

    Args:
        is_serial (bool): 是否等待回复,默认True

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True):
        ControlRobotAudioRecord.__init__(self, is_serial=is_serial,
                                         control_type=RobotAudioRecordControlType.STOP_RECORD)


class RobotAudioStartPlay(ControlRobotAudioRecord):
    """机器人开始播放录音api

    控制机器人开始播放录音

    Args:
        is_serial (bool): 是否等待回复,默认True
        file_name (str): 录音文件名,不可为空或None

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True, file_name: str = None):
        assert isinstance(file_name, str) and len(file_name), f'{self.__class__.__name__}  : file_name should be ' \
                                                              f'available '
        ControlRobotAudioRecord.__init__(self, is_serial=is_serial, file_name=file_name,
                                         control_type=RobotAudioRecordControlType.START_PLAY)


class RobotAudioStopPlay(ControlRobotAudioRecord):
    """机器人停止播放录音api

    控制机器人停止播放录音

    Args:
        is_serial (bool): 是否等待回复,默认True

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True):
        ControlRobotAudioRecord.__init__(self, is_serial=is_serial, control_type=RobotAudioRecordControlType.STOP_PLAY)


class RobotAudioPausePlay(ControlRobotAudioRecord):
    """机器人暂停播放录音api

    控制机器人暂停播放录音

    Args:
        is_serial (bool): 是否等待回复,默认True

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True):
        ControlRobotAudioRecord.__init__(self, is_serial=is_serial, control_type=RobotAudioRecordControlType.PAUSE_PLAY)


class RobotAudioContinuePlay(ControlRobotAudioRecord):
    """机器人继续播放录音api

    控制机器人继续播放录音

    Args:
        is_serial (bool): 是否等待回复,默认True

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True):
        ControlRobotAudioRecord.__init__(self, is_serial=is_serial,
                                         control_type=RobotAudioRecordControlType.CONTINUE_PLAY)


class RobotAudioRenameFile(ControlRobotAudioRecord):
    """机器人重命名录音文件api

    控制机器人重命名录音文件

    Args:
        is_serial (bool): 是否等待回复,默认True
        file_name (str): 录音文件名,不可为空或None

    #ControlRobotRecordResponse.isSuccess : 是否成功

    #ControlRobotRecordResponse.resultCode : 返回码

    #ControlRobotRecordResponse.id : 生成的录音文件名

    """

    def __init__(self, is_serial: bool = True, file_name: str = None, new_file_name: str = None):
        assert isinstance(file_name, str) and len(file_name), f'{self.__class__.__name__} : file_name should be ' \
                                                              f'available '
        assert isinstance(new_file_name, str) and len(new_file_name), f'{self.__class__.__name__} : new_file_name ' \
                                                                      f'should be available '
        ControlRobotAudioRecord.__init__(self, is_serial=is_serial, file_name=file_name, new_file_name=new_file_name,
                                         control_type=RobotAudioRecordControlType.RENAME_FILE)
