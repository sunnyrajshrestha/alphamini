#!/usr/bin/env python3
import abc
import asyncio
import enum
from abc import ABC
from typing import Callable, Union

from ..channels.websocket_client import ubt_websocket as _UBTWebSocket, AbstractMsgHandler

DEFAULT_TIMEOUT = 300

socket = _UBTWebSocket()


@enum.unique
class MiniApiResultType(enum.Enum):
    """
    Api的返回结果状态类型

    Success : 收到机器人回复

    Timeout : 在超时时间内为收到机器人回复

    Unsupported : 不支持该指令

    """
    Success = 1  # 成功
    Timeout = 2  # 超时
    Unsupported = 3  # 不支持的命令


class BaseApi(abc.ABC):
    """消息api基类
    """

    async def send(self, cmd_id: int, message, timeout: int) -> Union[object, bool]:
        """发送消息方法

        注意:由子类函数内部调用,子类实例不可调用。

        Args:
            cmd_id (int): 支持的命令id,例如:mini.apis.cmdid.PLAY_ACTION_REQUEST
            message (Message): 支持的消息实体,例如:mini.pb2.PlayActionRequest
            timeout (int): 超时时间,当timeout<=0时,表示不需要等待机器人回复,当timeout>0时,表示需要等待机器人回复,

        Returns:
            如果不支持该指令,返回tuple(MiniApiResultType.Unsupported,None)

            如果支持该指令

            当timeout<=0时,返回bool,表示消息是否发送成功

            当timeout>0时

            如果消息超时或者发送失败,则返回tuple(MiniApiResultType.Timeout,None)

            如果消息有回复,则返回tuple(MiniApiResultType.Success,result),result为相应的回复消息

        """
        assert cmd_id >= 0, 'cmdId should not be negative number in BaseApi'
        assert message is not None, 'message should not be none in BaseApi'
        # 通用的发送消息逻辑
        if timeout <= 0:
            return await socket.send_msg0(cmd_id, message)
        else:
            result = await socket.send_msg(cmd_id, message, timeout)
            if result:
                if result.header.target == -1:
                    import logging
                    log = logging.getLogger(__name__)
                    log.addHandler(logging.StreamHandler())
                    log.setLevel(logging.WARNING)
                    log.warning(f'当前机器人版本不支持命令:cmd={message.header.command}, 请升级机器人系统版本.')
                    return MiniApiResultType.Unsupported, None
                else:
                    return MiniApiResultType.Success, self._parse_msg(result)
            else:
                return MiniApiResultType.Timeout, None

    async def execute(self):
        """发送指令

        将支持的message序列化后,写入socket
        由子类实现
        """
        raise NotImplementedError()

    def _parse_msg(self, message):
        """解析回复指令

        将收到的Message对象包含的消息数据反序列化为相应的response
        由子类实现,仅供子类内部调用
        Args:
            message: Message对象
        """
        raise NotImplementedError()


class BaseApiNeedResponse(BaseApi, abc.ABC):
    """
    需要回复的消息api基类,timeout不能为空
    """

    async def send(self, cmd_id, data, timeout: int):
        """重写父类方法

        校验timeout,必须>0
        """

        assert timeout > 0, 'timeout should be Positive number in BaseApiNeedResponse'
        return await super().send(cmd_id, data, timeout)


class BaseApiNoNeedResponse(BaseApi, ABC):
    """不需要回复的消息api基类
    """

    async def send(self, cmd_id, message, timeout: int = 0):
        """重写父类方法

        将timeout设置为0
        """

        return await super().send(cmd_id, message, 0)


class BaseEventApi(BaseApiNoNeedResponse, AbstractMsgHandler, ABC):
    """事件类消息api基类

    当注册了事件处理器后,由机器人主动推送过来的事件消息

    Args:
        cmd_id (int): 注册的指令id
        message (Message): 向机器人发送的注册消息
        is_repeat (bool): 是否重复监听,默认为True
        timeout (int): 超时时间,默认为0
        handler (Callable): 事件消息处理器,f(message)

    """

    def __init__(self, cmd_id: int, message, is_repeat: bool = True, timeout: int = 0,
                 handler: 'Callable[..., None]' = None):
        """初始化事件类消息
        """
        super().__init__()
        self.__cmd_id = cmd_id
        self.__request = message
        self.__is_repeat = is_repeat
        self.__timeout = timeout
        self.__handler = handler

        if is_repeat:
            self.__repeatCount = -1
        else:
            self.__repeatCount = 1

    def set_handler(self, handler: 'Callable[..., None]' = None):
        """设置事件消息处理器

        Args:
            handler (Callable): 事件消息处理器,f(message)

        """
        self.__handler = handler

    def start(self):
        """启动监听器
        """

        # 发送消息
        asyncio.create_task(self.send(cmd_id=self.__cmd_id, message=self.__request))
        # 注册监听
        socket.register_msg_handler(cmd=self.__cmd_id, handler=self)

    def stop(self):
        """停止监听器

        子类需要通知机器人停止事件上报
        """

        # 移除消息监听
        socket.unregister_msg_handler(cmd=self.__cmd_id, handler=self)

    # AbstractMsgHandler
    def handle_msg(self, message):
        # 处理监听次数
        if self.__repeatCount > 0:
            # 有监听次数
            self.__handle_msg(message)
            self.__repeatCount -= 1
        elif self.__repeatCount == -1:
            # 无限监听
            self.__handle_msg(message)

    def __handle_msg(self, message):
        if message.header.target == -1:
            import logging
            log = logging.getLogger(__name__)
            log.addHandler(logging.StreamHandler())
            log.setLevel(logging.WARNING)
            log.warning(f'当前机器人版本不支持命令:cmd={message.header.command}, 请升级机器人系统版本.')
            return
        if self.__handler is not None:
            self.__handler(self._parse_msg(message))
