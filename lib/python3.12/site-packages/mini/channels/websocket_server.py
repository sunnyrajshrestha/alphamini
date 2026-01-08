import asyncio
from typing import Union

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosed, ConnectionClosedError

from ..channels import msg_utils as msg_utils
from ..channels.msg_utils import build_request_msg, parse_msg
from ..pb2 import codemao_playaction_pb2


async def check_permit(_socket: websockets.WebSocketServerProtocol):
    while True:
        recv_str: Union[str, bytes] = await _socket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "1":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await _socket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await _socket.send(response_str)


async def recv_msg(_socket: websockets.WebSocketServerProtocol):
    while True:
        recv_text = await _socket.recv()
        msg = parse_msg(recv_text)
        # response_text = f"your submit content:{request.actionName}"
        if msg.header.commandId == 1:
            request = codemao_playaction_pb2.PlayActionRequest()
            request.ParseFromString(msg.bodyData)
            print(f'your submit content:{request.actionName}')
            response = codemao_playaction_pb2.PlayActionResponse()
            response.isSuccess = True
            response.resultCode = 0
            msg = build_request_msg(msg.header.commandId, generator.send(0), msg.header.responseSerial, response)
        else:
            print(f'unsupported msg={msg}')

        await _socket.send(msg.SerializeToString())


async def main_logic(_socket: websockets.WebSocketServerProtocol, address: str):
    try:
        print(f'new connect:{_socket}, address={address}')
        await check_permit(_socket)
    except (ConnectionClosedOK, ConnectionClosed, ConnectionClosedError) as close:
        print(f'connection by closed')
        asyncio.get_event_loop().stop()
        return True
    except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError) as disconnect:
        asyncio.get_event_loop().stop()
        raise disconnect
    except Exception as close:
        await _socket.close(reason="server quit")
        print(f'{close}')
        asyncio.get_event_loop().stop()
        return True
    else:
        try:
            await recv_msg(_socket)
        except (ConnectionClosedOK, ConnectionClosed, ConnectionClosedError) as close:
            print(f'connection by closed')
            asyncio.get_event_loop().stop()
            return True
        except (ConnectionAbortedError, ConnectionError, ConnectionRefusedError, ConnectionResetError) as disconnect:
            asyncio.get_event_loop().stop()
            raise disconnect
        except Exception as close:
            await _socket.close(reason="server quit")
            print(f'{close}')
            asyncio.get_event_loop().stop()
            return True


generator = msg_utils.id_generator()
start_server = websockets.serve(main_logic, 'localhost', 8800)
asyncio.get_event_loop().run_until_complete(start_server)
try:
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt as e:
    pass
