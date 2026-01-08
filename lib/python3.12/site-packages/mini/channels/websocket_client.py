import abc
import asyncio
import logging
import threading
from asyncio import Future

import websockets
import websockets.exceptions
from google.protobuf import message as _message
from typing import Type, Any
from websockets.exceptions import ConnectionClosed, ConnectionClosedOK

from ..channels import msg_utils as msg_utils
from ..pb2.pccodemao_message_pb2 import Message

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
if log.level == logging.NOTSET:
    log.setLevel(logging.WARNING)


class AbstractMsgHandler(abc.ABC):

    def __init__(self, identify=0, msg_clazz: type(_message.Message) = Message):
        if issubclass(msg_clazz, _message.Message):
            self.__msg_clazz = msg_clazz or Message
            self.__identify = identify
        else:
            class_name = type(self).__name__
            raise Exception(f'{class_name} is not subclass of {Message.__name__}')

    @abc.abstractmethod
    def handle_msg(self, message: _message.Message):
        pass

    def parse_msg(self, body_data):
        if self.msg_clazz == Message:
            log.info('no need parse body message.')
            return body_data
        return self.msg_clazz().ParseFromString(body_data)

    @property
    def msg_clazz(self):
        return self.__msg_clazz

    @property
    def identify(self):
        return self.__identify

    def __repr__(self):
        class_name = type(self).__name__
        msg_clazz_name = type(self.msg_clazz).__name__
        return '({!r}, {!r}, {!r})'.format(class_name, msg_clazz_name, self.__identify)


class DefaultMsgHandler(AbstractMsgHandler):

    def handle_msg(self, message: _message.Message):
        log.warning(f'handle msg: {message}')


class _CoroutineHandler(AbstractMsgHandler):

    def __init__(self, identify, future: Future):
        super().__init__(identify)
        self.coroutine = None
        self.__future = future

    def handle_msg(self, message: _message.Message):
        log.debug(f'receiver message = {message}')
        if self.__future.cancelled() or self.__future.done():
            return
        self.__future.set_result(message)


class _MessageDispatcher(object):

    def __init__(self):
        self.__handlers = {}

    def add_handler(self, cmd, msg_handler: AbstractMsgHandler = DefaultMsgHandler(Message)):
        if isinstance(msg_handler, AbstractMsgHandler):
            self.handlers.setdefault(cmd, []).append(msg_handler)
        else:
            class_name = type(msg_handler).__name__
            raise Exception(f'{class_name} is not instance of {AbstractMsgHandler.__name__}')

    def remove_handler(self, cmd):
        del self.handlers[cmd]

    def remove_handler0(self, cmd, handler: AbstractMsgHandler):
        self.handlers.get(cmd).remove(handler)

    def __len__(self):
        return len(self.handlers)

    def __iter__(self):
        return tuple(self.handlers)

    @property
    def handlers(self):
        return self.__handlers

    def __repr__(self):
        return '{}({!r})'.format(*self)

    def dispatch(self, message: Message):
        header = message.header
        handler_list = self.handlers.get(header.command)
        if handler_list is not None:
            found: bool = False
            for handler in handler_list:
                if header.id == str(handler.identify):
                    log.debug(f'find handler = {handler}')
                    found = True
                    if header.target == -1:
                        log.warning(f"cmd={header.command} is unsupported by current robot.")
                    else:
                        handler.handle_msg(message)
                    if isinstance(handler, _CoroutineHandler):
                        log.debug(f'remove cmd={header.command} handlers.')
                        self.remove_handler(header.command)
            if not found:
                log.warning(f'1.ignore: cmd={header.command}, cmd no handlers')
        else:
            log.warning(f'2.ignore:cmd={header.command}, cmd no handlers.')


class _UBTWebSocketClient(object):
    __init_flag = False
    _instance_lock = threading.Lock()

    def __init__(self):
        if not _UBTWebSocketClient.__init_flag:
            _UBTWebSocketClient.__init_flag = True
            log.info(f'init {_UBTWebSocketClient.__name__}')
            self._client = None
            self.__ip = 'localhost'
            self.__port = 8800
            self.__dispatcher = _MessageDispatcher()
            self.__generator = msg_utils.id_generator()

    def __new__(cls, *args, **kwargs):
        if not hasattr(_UBTWebSocketClient, "_instance"):
            with _UBTWebSocketClient._instance_lock:
                if not hasattr(_UBTWebSocketClient, "_instance"):
                    _UBTWebSocketClient._instance = object.__new__(cls)
        return _UBTWebSocketClient._instance

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

    @property
    def alive(self):
        return self._client and (not self._client.closed)

    def __format__(self, format_spec=''):
        return 'ip={!r},port={!r}'.format(self.__ip, self.__port)

    def __repr__(self):
        class_name = type(self).__name__
        return '{!r}({!r}, {!r})'.format(class_name, self.__ip, self.__port)

    async def connect(self, ip_address='localhost', port=8800, timeout=15000) -> bool:
        self.__ip = ip_address
        self.__port = port
        return await asyncio.wait_for(self.__connect(), timeout)

    async def __connect(self) -> bool:
        if self.alive:
            await self._client.close(reason='exit for reconnecting.')
        try:
            log.info(f'connect begin')
            self._client = await websockets.connect('ws://{}:{!r}'.format(self.ip, self.port))
            log.info(f'connect success')
            asyncio.create_task(self.__loop())
            # threading.Thread(target=self.__loop()).start()
            return True
        except OSError as error:
            log.error(f'WebSocket server no startUp: error{error}')
            return False

    async def __loop(self):
        log.debug(f'begin loop.')
        try:
            while self.alive:
                _data = None
                # _data = await self._client.recv()
                # _data = asyncio.run(self._client.recv())
                _data = await self._client.recv()
                # do parse
                _bytes = msg_utils.base64_decode(_data)
                msg = msg_utils.parse_msg(_bytes)
                log.info(f"recv msg: {msg}")
                # do dispatch
                self.__dispatch(msg)
        except Exception as e:
            if isinstance(e, ConnectionClosedOK):
                log.warning("connection closed ok!")
                if self._client:
                    asyncio.get_running_loop().call_later(3, asyncio.get_running_loop().stop)
            else:
                log.exception('recv fail : %r', e)
        log.debug(f'end loop.')

    def __dispatch(self, message: Message):
        self.__dispatcher.dispatch(message)

    async def send_msg0(self, cmd, message: _message.Message) -> bool:
        if self.alive:
            client = self._client
            identify = 0
            pccode_mao_message: Message = msg_utils.build_request_msg(cmd, send_serial=identify, request=message)

            async def send0():
                try:
                    await client.send(msg_utils.base64_encode(pccode_mao_message.SerializeToString()))
                    log.info(
                        'send cmd={!r}, identify={!r}, message={!r}'.format(pccode_mao_message.header.command,
                                                                            pccode_mao_message.header.id,
                                                                            message))
                    return True
                except (ConnectionClosed, ConnectionClosedOK) as close:
                    log.warning(f'Waring: connect is closed: {close}')
                    return False
                except (ConnectionError, ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError) as error:
                    log.warning(f'Waring: connect error: {error}')
                    return False

            try:
                await asyncio.create_task(send0())
                return True
            except Exception as e:
                log.warning(f'receiver response failure: {e}')
                return False
        else:
            log.warning(f"Waring: Client not connected!")
            return False

    def register_msg_handler(self, cmd, handler: AbstractMsgHandler):
        self.__dispatcher.add_handler(cmd, handler)

    def unregister_msg_handler(self, cmd, handler: AbstractMsgHandler = None):
        if handler is None:
            self.__dispatcher.remove_handler(cmd)
        else:
            self.__dispatcher.remove_handler0(cmd, handler)

    async def send_msg(self, cmd, message: _message.Message, timeout) -> Any:
        if self.alive:
            client = self._client
            identify = self.generate_id()
            pccode_mao_message: Message = msg_utils.build_request_msg(cmd, send_serial=identify, request=message)
            future = asyncio.get_running_loop().create_future()
            handler = _CoroutineHandler(identify, future)
            log.debug(f'register cmd={pccode_mao_message.header.command} handler={handler}')
            self.register_msg_handler(pccode_mao_message.header.command, handler)

            async def send1():
                try:
                    await client.send(msg_utils.base64_encode(pccode_mao_message.SerializeToString()))
                    log.info(
                        'send cmd={!r}, identify={!r}, message={!r}'.format(pccode_mao_message.header.command,
                                                                            pccode_mao_message.header.id,
                                                                            message))
                    return await future
                except (
                        ConnectionClosed, ConnectionClosedOK, ConnectionError, ConnectionResetError,
                        ConnectionAbortedError,
                        ConnectionRefusedError) as close:
                    log.warning(f'connect close. {close}')
                except Exception as e2:
                    log.warning(f'send message failure: {e2}')

            try:
                return await asyncio.wait_for(send1(), timeout)
            except Exception as e:
                log.warning(f'recv response  failure: {e}')
                return None
        else:
            log.warning(f'client is not alive')
            raise RuntimeError("no connection!")

    def generate_id(self) -> int:
        return self.__generator.send(0)

    async def shutdown(self):
        if self.alive:
            self.__generator.close()
            await self._client.close(reason="client closed")
            self._client = None
        else:
            log.warning(f'client is not alive.')


ubt_websocket: Type[_UBTWebSocketClient] = _UBTWebSocketClient
