#!/usr/bin/env python3

from ..apis.base_api import BaseApi, DEFAULT_TIMEOUT
from ..apis.cmdid import _PCProgramCmdId
from ..pb2.codemao_revertorigin_pb2 import RevertOriginRequest, RevertOriginResponse
from ..pb2.pccodemao_disconnection_pb2 import DisconnectionRequest, DisconnectionResponse
from ..pb2.pccodemao_getappversion_pb2 import GetAppVersionRequest, GetAppVersionResponse
from ..pb2.pccodemao_message_pb2 import Message


class StartRunProgram(BaseApi):
    """进入编程模式api

    机器人进入编程模式

    Args:
        is_serial (bool): 是否等待回复,默认True

    #GetAppVersionResponse.isSuccess : 是否成功

    #GetAppVersionResponse.resultCode : 返回码

    #GetAppVersionResponse.version
    """

    def __init__(self, is_serial: bool = True):
        self.__is_serial = is_serial

    async def execute(self):
        """
        执行进入编程模式指令

        Returns:
            GetAppVersionResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = GetAppVersionRequest()

        cmd_id = _PCProgramCmdId.GET_ROBOT_VERSION_REQUEST.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            GetAppVersionResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = GetAppVersionResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class StopRunProgram(BaseApi):
    """退出编程模式api

    机器人退出编程模式

    Args:
        is_serial (bool): 是否等待回复,默认True
    """

    def __init__(self, is_serial: bool = True, ):
        self.__is_serial = is_serial

    async def execute(self):
        """
        执行退出编程模式指令

        Returns:
            DisconnectionResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = DisconnectionRequest()

        cmd_id = _PCProgramCmdId.DISCONNECTION_REQUEST.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        if isinstance(message, Message):
            data = message.bodyData
            response = DisconnectionResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class RevertOrigin(BaseApi):
    """复位api

    机器人复位

    Args:
        is_serial (bool): 是否等待回复,默认True

    #RevertOriginResponse.isSuccess : 是否成功

    #RevertOriginResponse.resultCode : 返回码
    """

    def __init__(self, is_serial: bool = True):
        self.__is_serial = is_serial

    async def execute(self):
        """
        执行机器人复位指令

        Returns:
            RevertOriginResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = RevertOriginRequest()

        cmd_id = _PCProgramCmdId.REVERT_ORIGIN_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            RevertOriginResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = RevertOriginResponse()
            response.ParseFromString(data)
            return response
        else:
            return None
