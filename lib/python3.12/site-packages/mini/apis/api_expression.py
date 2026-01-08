#!/usr/bin/env python3

import enum

from ..apis.base_api import BaseApi, DEFAULT_TIMEOUT
from ..apis.cmdid import _PCProgramCmdId
from ..pb2.codemao_controlmouthlamp_pb2 import ControlMouthRequest, ControlMouthResponse
from ..pb2.codemao_playexpression_pb2 import PlayExpressionRequest, PlayExpressionResponse
from ..pb2.codemao_setmouthlamp_pb2 import SetMouthLampRequest, SetMouthLampResponse
from ..pb2.pccodemao_message_pb2 import Message


@enum.unique
class RobotExpressionType(enum.Enum):
    """
    机器人表情类型

    INNER(内置) : 机器人内置的不可修改的表情文件
    """
    # CUSTOM(自定义) : 放置在sdcard/customize/expresss目录下可被开发者修改的表情文件
    INNER = 0  # 内置表情
    # CUSTOM = 1  # 自定义表情


class PlayExpression(BaseApi):
    """播放内置表情api

    让机器人眼睛演示个表情

    Args:
        is_serial (bool): 是否等待回复,默认True
        express_name (str): 表情名称,不可为空或者None

    #PlayExpressionResponse.isSuccess : 是否成功

    #PlayExpressionResponse.resultCode : 返回码

    """

    def __init__(self, is_serial: bool = True, express_name: str = None):
        assert express_name is not None and len(express_name), 'PlayExpression: expressName should be available'
        self.__is_serial = is_serial
        self.__express_name = express_name
        self.__dir_type = RobotExpressionType.INNER.value

    async def execute(self):
        """
        执行播放表情指令

        Returns:
            PlayExpressionResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = PlayExpressionRequest()
        request.expressName = self.__express_name
        request.dirType = self.__dir_type

        cmd_id: int = _PCProgramCmdId.PLAY_EXPRESSION_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            PlayExpressionResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = PlayExpressionResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


@enum.unique
class MouthLampColor(enum.Enum):
    """
    嘴巴灯颜色

    RED : 红色

    GREEN : 绿色

    WHITE : 白色
    """
    RED = 1  # 红色
    GREEN = 2  # 绿色
    WHITE = 4  # 白色


@enum.unique
class MouthLampMode(enum.Enum):
    """
    嘴巴灯模式

    NORMAL(普通模式) : 常亮模式

    BREATH(呼吸模式) : 呼吸模式
    """
    NORMAL = 0  # 普通模式
    BREATH = 1  # 呼吸模式


class SetMouthLamp(BaseApi):
    """设置嘴巴灯api

    设置嘴巴灯的模式、颜色等参数

    当mode=NORMAL时,duration参数起作用,表示常亮多久时间

    当mode=BREATH,breath_duration参数表示多久呼吸一次

    设置生效后,机器人会立即返回设置结果(与设置的duration参数无关)

    Args:
        is_serial (bool): 是否等待回复,默认True
        mode (MouthLampMode): 嘴巴灯模式,默认NORMAL,普通(常亮)模式
        color (MouthLampColor): 嘴巴灯颜色,默认RED,红色
        duration (int): 持续时间,单位为毫秒,-1表示无限时间,当时长设置超过10s,会在10s内返回结果
        breath_duration (int):闪烁一次时长,单位为毫秒

    #SetMouthLampResponse.isSuccess : 是否成功

    #SetMouthLampResponse.resultCode : 返回码
    """

    def __init__(self, is_serial: bool = True, mode: MouthLampMode = MouthLampMode.NORMAL,
                 color: MouthLampColor = MouthLampColor.RED, duration: int = 1000, breath_duration: int = 1000):
        assert isinstance(mode, MouthLampMode), 'SetMouthLamp: mode should be MouthLampMode instance'
        assert isinstance(color, MouthLampColor), 'SetMouthLamp: color should be MouthLampColor instance'
        self.serial = is_serial
        self.__is_serial = self.serial
        self.__mode = mode.value
        self.__color = color.value
        self.__duration = duration
        self.__breath_duration = breath_duration

    async def execute(self):
        """
        执行设置设置嘴巴灯指令

        Returns:
            SetMouthLampResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = SetMouthLampRequest()
        request.model = self.__mode
        request.color = self.__color
        if request.color == 4:
            request.redValue = 0xff
            request.greenValue = 0xff
            request.blueValue = 0xff

        request.duration = self.__duration
        request.breathDuration = self.__breath_duration

        cmd_id = _PCProgramCmdId.SET_MOUTH_LAMP_REQUEST.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            SetMouthLampResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = SetMouthLampResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class ControlMouthLamp(BaseApi):
    """控制嘴巴灯开关api

    打开/关闭嘴巴灯

    Args:
        is_serial (bool): 是否等待回复,默认True
        is_open (bool): 是否开启嘴巴灯 默认true,开启嘴巴灯

    #ControlMouthResponse.isSuccess : 是否成功

    #ControlMouthResponse.resultCode : 返回码
    """

    def __init__(self, is_serial: bool = True, is_open: bool = True):

        self.__is_serial = is_serial
        self.__is_open = is_open

    async def execute(self):
        """
        执行控制嘴巴灯指令

        Returns:
            ControlMouthResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = ControlMouthRequest()
        request.isOpen = self.__is_open

        cmd_id = _PCProgramCmdId.SWITCH_MOUTH_LAMP_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ControlMouthResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ControlMouthResponse()
            response.ParseFromString(data)
            return response
        else:
            return None
