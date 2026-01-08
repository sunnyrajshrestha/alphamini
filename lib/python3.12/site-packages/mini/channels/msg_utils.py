import base64
import logging
from functools import wraps

from google.protobuf import message as _message

from ..pb2.pccodemao_message_pb2 import Message
from ..pb2.pccodemao_messageheader_pb2 import MessageHeader

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
if log.level == logging.NOTSET:
    log.setLevel(logging.WARN)


def build_request_msg(cmd: int, send_serial: int, request: _message.Message) -> Message:
    msg = Message()
    msg.bodyData = request.SerializeToString()
    msg_header: MessageHeader = MessageHeader()
    msg_header.command = cmd
    msg_header.id = str(send_serial)
    # msg_header.responseSerial = 0
    msg.header.CopyFrom(msg_header)
    return msg


def build_response_msg(cmd: int, send_serial: int, response: _message.Message) -> Message:
    msg = Message()
    msg.bodyData = response.SerializeToString()
    msg_header = MessageHeader()
    msg_header.command = cmd
    msg_header.id = send_serial
    # msg_header.responseSerial = response_serial
    msg.header.CopyFrom(msg_header)
    return msg


def parse_msg(recv: str) -> Message:
    msg = Message()
    msg.ParseFromString(recv)
    return msg


def parse_body_msg(recv: bytes, clazz: type(_message.Message)) -> _message.Message:
    return clazz().ParseFromString(recv)
    # clazz.ParseFromString(recv)


def base64_encode(b: bytes) -> str:
    log.debug("{0} -----> {1}".format(str(b), str(base64.b64encode(b))))
    return "{0}&".format(str(base64.b64encode(b))[2:-1])


def base64_decode(b: str) -> str:
    log.debug("{0}".format(str(b)))
    return base64.b64decode(b[:-1])


def coroutine(func):
    @wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen

    return primer


@coroutine
def id_generator():
    identify = 0
    while True:
        yield identify
        identify += 1
