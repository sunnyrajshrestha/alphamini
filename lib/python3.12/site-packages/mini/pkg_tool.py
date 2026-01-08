import asyncio
import enum
import os

import websockets

import mini
from mini import WiFiDevice as _WiFiDevice
from mini.channels import msg_utils
from mini.pb2.pccodemao_message_pb2 import Message as _Message
from mini.pb2.pccodemao_messageheader_pb2 import MessageHeader as _MessageHeader

_found_devices = {}


@enum.unique
class _PCPyCmdId(enum.Enum):
    """
    脱机工具命令号
    """
    PYPI_INSTALL_WHEEL_REQUEST = 1
    """
    安装程序包
    """

    PYPI_UNINSTALL_WHEEL_REQUEST = 2
    """
    卸载程序包
    """

    PYPI_GET_WHEEL_INFO_REQUEST = 3
    """
    获取程序包信息
    """

    PYPI_RUN_WHEEL_REQUEST = 4
    """
    执行程序
    """

    PYPI_GET_WHEEL_LIST_REQUEST = 5
    """
    获取安装程序列表
    """

    PYPI_START_RECORD_REQUEST = 6
    """获取录音数据--不支持
    """

    PYPI_SWITCH_ADB_REQUEST = 7
    """开关ADB
    """

    PYPI_UPLOAD_SCRIPT_REQUEST = 8
    """上传python脚本到机器人
    """

    PYPI_CHECK_UPLOAD_SCRIPT_REQUEST = 9
    """检查python脚本是否已上传到机器人
    """

    PYPI_RUN_UPLOAD_SCRIPT_REQUEST = 10
    """执行已上传的某个python脚本
    """

    PYPI_STOP_UPLOAD_SCRIPT_REQUEST = 11
    """停止执行已上传的某个python脚本
    """

    PYPI_LIST_UPLOAD_SCRIPT_REQUEST = 12
    """获取已上传的某个python脚本列表
    """


def _read_into_buffer(filename) -> bytes:
    buf = bytearray(os.path.getsize(filename))
    with open(filename, 'rb') as f:
        f.readinto(buf)
    return bytes(buf)


async def _send_msg1(websocket, message: _Message) -> str:
    await websocket.send(msg_utils.base64_encode(message.SerializeToString()))
    result: str = ""
    while True:
        try:
            _data = await websocket.recv()
            _bytes = msg_utils.base64_decode(_data)
            msg: _Message = msg_utils.parse_msg(_bytes)
            header: _MessageHeader = msg.header
            if header.command == _PCPyCmdId.PYPI_INSTALL_WHEEL_REQUEST.value:
                from mini.tool.pb2.PyPi_InstallWheel_pb2 import InstallWheelResponse
                response: InstallWheelResponse = InstallWheelResponse()
                response.ParseFromString(msg.bodyData)
                print("{0}".format(response.message))
            elif header.command == _PCPyCmdId.PYPI_UNINSTALL_WHEEL_REQUEST.value:
                from mini.tool.pb2.PyPi_UninstallWheel_pb2 import UninstallWheelResponse
                response: UninstallWheelResponse = UninstallWheelResponse()
                response.ParseFromString(msg.bodyData)
                print("{0}".format(response.message))
            elif header.command == _PCPyCmdId.PYPI_RUN_WHEEL_REQUEST.value:
                from mini.tool.pb2.PyPi_RunWheel_pb2 import RunWheelResponse
                response: RunWheelResponse = RunWheelResponse()
                response.ParseFromString(msg.bodyData)
                print("{0}".format(response.message))
            elif header.command == _PCPyCmdId.PYPI_GET_WHEEL_INFO_REQUEST.value:
                from mini.tool.pb2.PyPi_GetWheelInfo_pb2 import GetWheelInfoResponse
                response: GetWheelInfoResponse = GetWheelInfoResponse()
                response.ParseFromString(msg.bodyData)
                return response.message
            elif header.command == _PCPyCmdId.PYPI_GET_WHEEL_LIST_REQUEST.value:
                from mini.tool.pb2.PyPi_GetWheelList_pb2 import GetWheelListResponse
                response: GetWheelListResponse = GetWheelListResponse()
                response.ParseFromString(msg.bodyData)
                if response.resultCode != 0:
                    return response.error
                else:
                    return "\n".join(response.Wheels)
            elif header.command == _PCPyCmdId.PYPI_UPLOAD_SCRIPT_REQUEST.value:
                from mini.tool.pb2.PyPi_UploadScript_pb2 import UploadScriptResponse
                response: UploadScriptResponse = UploadScriptResponse()
                response.ParseFromString(msg.bodyData)
                print("command {0} return <{1}, {2}>".format(header.command, response.resultCode, response.message))
                return response.message
            elif header.command == _PCPyCmdId.PYPI_CHECK_UPLOAD_SCRIPT_REQUEST.value:
                from mini.tool.pb2.PyPi_UploadScript_pb2 import UploadScriptResponse
                response: UploadScriptResponse = UploadScriptResponse()
                response.ParseFromString(msg.bodyData)
                print("command {0} return <{1}, {2}>".format(header.command, response.resultCode, response.message))
                return response.message
            elif header.command == _PCPyCmdId.PYPI_RUN_UPLOAD_SCRIPT_REQUEST.value:
                from mini.tool.pb2.PyPi_UploadScript_pb2 import UploadScriptResponse
                response: UploadScriptResponse = UploadScriptResponse()
                response.ParseFromString(msg.bodyData)
                print("command {0} return <{1}, {2}>".format(header.command, response.resultCode, response.message))
                return response.message
            elif header.command == _PCPyCmdId.PYPI_STOP_UPLOAD_SCRIPT_REQUEST.value:
                from mini.tool.pb2.PyPi_UploadScript_pb2 import UploadScriptResponse
                response: UploadScriptResponse = UploadScriptResponse()
                response.ParseFromString(msg.bodyData)
                print("command {0} return <{1}, {2}>".format(header.command, response.resultCode, response.message))
                return response.message
            elif header.command == _PCPyCmdId.PYPI_LIST_UPLOAD_SCRIPT_REQUEST.value:
                from mini.tool.pb2.PyPi_UploadScript_pb2 import ListUploadScriptResponse
                response: ListUploadScriptResponse = ListUploadScriptResponse()
                response.ParseFromString(msg.bodyData)
                print("command {0} return {1}".format(header.command, response.uploadScripts))
                return "ex"
            elif header.target == -1:
                print(f"Unsupported cmd={header.command}")
            else:
                print(f"Unsupported cmd={header.command}")

        except Exception as e:
            if isinstance(e, websockets.ConnectionClosedOK):
                # print(f"connection closed ok!")
                break
            else:
                raise e
    return result


async def _send_msg0(message: _Message, device: _WiFiDevice) -> str:
    try:
        async with websockets.connect('ws://{}:{!r}'.format(device.address, 8801)) as websocket:
            return await _send_msg1(websocket, message)
    except Exception as e:
        return ""


def _get_eggInfo_path():
    return _get_file('.', 'egg-info', True)


def _get_file(dir_path: str, suffix: str, is_dir: bool = False):
    for temp_path in os.listdir(dir_path):
        temp_path = os.path.join(dir_path, temp_path)
        if is_dir:
            if not os.path.isdir(temp_path):
                continue
        else:
            if not os.path.isfile(temp_path):
                continue

        if temp_path.endswith(suffix):
            result = os.path.abspath(temp_path)
            return result


def _remove_dir(dir_path: str):
    """
    删除目录
    :param dir_path: 需要删除的目录
    """
    if isinstance(dir_path, str) and os.path.exists(dir_path) and os.path.isdir(dir_path):
        import shutil
        shutil.rmtree(dir_path)
    elif dir_path is not None and os.path.exists(dir_path):
        os.remove(dir_path)


def setup_py_pkg(project_dir: str) -> str:
    """
    将一个py工程打包成一个.whl文件。

    Args:
        project_dir: 工程文件根目录

    Returns:
        str : 生成的.whl文件绝对路径
    """
    # 校验目录
    if not os.path.isdir(project_dir):
        print('project_dir must be a directory')
        return ""
    # 将当前进程工作目录切换到工程目录
    os.chdir(project_dir)
    # 清空产物目录
    build_path = 'build'
    egg_info_path = _get_eggInfo_path()
    dist_path = 'dist'
    _remove_dir(build_path)
    _remove_dir(egg_info_path)
    _remove_dir(dist_path)

    os.mkdir(build_path)
    os.mkdir(dist_path)

    # 找到setup文件
    setup_path = 'setup.py'

    if not os.path.isfile(setup_path):
        print('setup.py not exist')
        return ""

    # 打包
    import sys
    if sys.version_info < (3, 0):
        os.system(f"python {setup_path} sdist bdist_wheel")
    else:
        import platform
        if platform.system() == 'Windows':
            os.system(f'python {setup_path} sdist bdist_wheel')
        else:
            os.system(f'python3 {setup_path} sdist bdist_wheel')

    # 删除其他临时文件
    egg_info_path = _get_eggInfo_path()
    _remove_dir(build_path)
    _remove_dir(egg_info_path)

    result = _get_file(dist_path, '.whl')
    print(f'result {result}')
    return result


def _build_install_py_pkg_msg(package_path: str, debug: bool) -> _Message:
    from mini.tool.pb2.PyPi_InstallWheel_pb2 import InstallWheelRequest
    request = InstallWheelRequest()
    # 获取文件路径中的文件名
    request.wheelName = os.path.basename(package_path)
    # 把文件转成字节
    request.serializePacket = _read_into_buffer(package_path)
    request.debug = debug
    cmd_id = _PCPyCmdId.PYPI_INSTALL_WHEEL_REQUEST.value
    # message
    message: _Message = msg_utils.build_request_msg(cmd_id, 0, request)
    return message


def install_py_pkg(package_path: str, robot_id: str, debug: bool = False):
    """
    将一个py程序安装包,安装到指定序列号的机器人上。

    Args:
        package_path: 安装包的绝对路径
        robot_id:机器人序列号
        debug:是否打印在机器人端卸载pkg时的log

    Returns:
        None
    """
    # 校验文件
    if not os.path.isfile(package_path):
        print(f'file is not exist:{package_path}')
        return

    base_name = os.path.basename(package_path)

    if not base_name.endswith('.whl'):
        print(f'Not a PiPy package  ')
        return

    device: _WiFiDevice = _found_devices.get(robot_id)
    # 搜索设备
    if device is None:
        device = asyncio.get_event_loop().run_until_complete(mini.get_device_by_name(robot_id, 10))
        if device is None:
            print(f"Can't find AlphaMini of id (:{robot_id})")
            return
        else:
            _found_devices[robot_id] = device
    # 上传
    asyncio.run(_send_msg0(_build_install_py_pkg_msg(package_path, debug), device))


def _build_uninstall_py_pkg_msg(pkg_name: str, debug: bool) -> _Message:
    from mini.tool.pb2.PyPi_UninstallWheel_pb2 import UninstallWheelRequest
    request = UninstallWheelRequest()
    # pkg name
    request.wheelName = os.path.basename(pkg_name)
    request.debug = debug
    cmd_id = _PCPyCmdId.PYPI_UNINSTALL_WHEEL_REQUEST.value
    # message
    message: _Message = msg_utils.build_request_msg(cmd_id, 0, request)
    return message


def uninstall_py_pkg(pkg_name: str, robot_id: str, debug: bool = False):
    """
    将一个安装的py程序,从指定序列号的机器人上卸载掉,例如有一个py程序,它的setup.py文件, 配置如下:
        setuptools.setup(

            name="tts_demo",

            ...#省略

        ),

    那么,它的pkg_name为"tts_demo"。

    Args:
        pkg_name : 程序名称
        robot_id : 机器人序列号
        debug : 是否打印在机器人端卸载pkg时的log

    Returns:
        None

    """
    device: _WiFiDevice = _found_devices.get(robot_id)
    # 搜索设备
    if device is None:
        device = asyncio.get_event_loop().run_until_complete(mini.get_device_by_name(robot_id, 10))
        if device is None:
            print(f"Can't find AlphaMini of id (:{robot_id})")
            return
        else:
            _found_devices[robot_id] = device
    # 卸载
    asyncio.run(_send_msg0(_build_uninstall_py_pkg_msg(pkg_name, debug), device))


def _build_query_py_pkg_msg(pkg_name: str) -> _Message:
    from mini.tool.pb2.PyPi_GetWheelInfo_pb2 import GetWheelInfoRequest
    request = GetWheelInfoRequest()
    # pkg name
    request.wheelName = os.path.basename(pkg_name)
    cmd_id = _PCPyCmdId.PYPI_GET_WHEEL_INFO_REQUEST.value
    # message
    message: _Message = msg_utils.build_request_msg(cmd_id, 0, request)
    return message


def query_py_pkg(pkg_name: str, robot_id: str) -> str:
    """
    查询机器人上pkg_name指定的py程序, 其详细信息, 例如有一个py程序,它的setup.py文件, 配置如下:

    setuptools.setup(

        name="tts_demo",

        version="0.0.2",

        author='Gino Deng',

        author_email='jingjing.deng@ubtrobot.com',

        description="demo with mini_sdk",

        long_description='demo with mini_sdk,xxxxxxx',

        long_description_content_type="text/markdown",

        license="GPLv3",

        packages=setuptools.find_packages(),

        classifiers=[

            "Programming Language :: Python :: 3",

            "Programming Language :: Python :: 3.6",

            "Programming Language :: Python :: 3.7",

            "Programming Language :: Python :: 3.8",

            "License :: OSI Approved :: MIT License",

            "Operating System :: OS Independent",

        ],

        install_requires=[

            'alphamini',

        ],

    ),

    查询时, 指定pkg_name="tts_demo", 返回信息如下:

        Name: tts-demo

        Version: 0.0.2

        Summary: demo with mini_sdk

        Home-page: UNKNOWN

        Author: Gino Deng

        Author-email: jingjing.deng@ubtrobot.com

        License: GPLv3

        Location: /data/data/com.termux/files/usr/lib/python3.8/site-packages

        Requires: alphamini

        Required-by:

    Args:
        pkg_name : py程序名,
        robot_id : 机器人序列号

    Returns:
        str : 安装包相信信息
    """
    device: _WiFiDevice = _found_devices.get(robot_id)
    # 搜索设备
    if device is None:
        device = asyncio.get_event_loop().run_until_complete(mini.get_device_by_name(robot_id, 10))
        if device is None:
            print(f"Can't find AlphaMini of id (:{robot_id})")
            return ""
        else:
            _found_devices[robot_id] = device
    # 查询
    return asyncio.run(_send_msg0(_build_query_py_pkg_msg(pkg_name), device))


def _build_list_py_pkg_msg():
    from mini.tool.pb2.PyPi_GetWheelList_pb2 import GetWheelListRequest
    request = GetWheelListRequest()
    cmd_id = _PCPyCmdId.PYPI_GET_WHEEL_LIST_REQUEST.value
    # message
    message: _Message = msg_utils.build_request_msg(cmd_id, 0, request)
    return message


def list_py_pkg(robot_id: str) -> str:
    """
    列出机器人上安装的py程序, 例如:

        Package    Version

        ---------- -------

        alphamini  1.1.1

        ifaddr     0.1.7

        pip        20.1.1

        protobuf   3.12.2

        setuptools 47.3.1

        six        1.15.0

        tts-demo   0.0.2

        websockets 8.1

        wheel      0.34.2

    Args:
        robot_id: 机器人序列号

    Returns:
        str : 所有py程序名称-版本号
    """
    device: _WiFiDevice = _found_devices.get(robot_id)
    # 搜索设备
    if device is None:
        device = asyncio.get_event_loop().run_until_complete(mini.get_device_by_name(robot_id, 10))
        if device is None:
            print(f"Can't find AlphaMini of id (:{robot_id})")
            return ""
        else:
            _found_devices[robot_id] = device
    # 查询
    return asyncio.run(_send_msg0(_build_list_py_pkg_msg(), device))


def _build_run_py_pkg_msg(entry_point: str, debug: bool) -> _Message:
    from mini.tool.pb2.PyPi_RunWheel_pb2 import RunWheelRequest
    request = RunWheelRequest()
    # pkg main entry
    request.wheelName = entry_point
    request.debug = debug
    cmd_id = _PCPyCmdId.PYPI_RUN_WHEEL_REQUEST.value
    # message
    message: _Message = msg_utils.build_request_msg(cmd_id, 0, request)
    return message


def run_py_pkg(entry_point: str, robot_id: str, debug: bool = False):
    """
    触发一个指定的py程序, 在指定的机器人上运行。:

    Args:
        entry_point: py程序console scripts名称, 例如在setup.py文件中,如配置 entry_points={

                        'console_scripts': [

                            'XXX = Packages.Modules:XXX'

                        ],

                    }, 程序入口名称为xxx

        robot_id: 机器人序列号
        debug: 是否回传程序执行时日志

    Returns:
        None
    """
    device: _WiFiDevice = _found_devices.get(robot_id)
    # 搜索设备
    if device is None:
        device = asyncio.get_event_loop().run_until_complete(mini.get_device_by_name(robot_id, 10))
        if device is None:
            print(f"Can't find AlphaMini of id (:{robot_id})")
            return
        else:
            _found_devices[robot_id] = device
    # 触发
    asyncio.run(_send_msg0(_build_run_py_pkg_msg(entry_point, debug), device))


def _build_switch_adb_msg(switch: bool):
    from mini.tool.pb2.PyPi_AdbSwitch_pb2 import AdbSwitchRequest
    request = AdbSwitchRequest()
    # pkg main entry
    request.open = switch
    cmd_id = _PCPyCmdId.PYPI_SWITCH_ADB_REQUEST.value
    # message
    message: _Message = msg_utils.build_request_msg(cmd_id, 0, request)
    return message


def switch_adb(robot_id: str, switch: bool = True):
    """
    打开机器人ADB调试开关
    Args:
        switch: bool, True or False
        robot_id: 机器人序列号

    Returns:
        None
    """
    device: _WiFiDevice = _found_devices.get(robot_id)
    # 搜索设备
    if device is None:
        device = asyncio.get_event_loop().run_until_complete(mini.get_device_by_name(robot_id, 10))
        if device is None:
            print(f"Can't find AlphaMini of id (:{robot_id})")
            return
        else:
            _found_devices[robot_id] = device
    # 触发
    asyncio.run(_send_msg0(_build_switch_adb_msg(switch), device))


def _build_upload_script_msg(file_name: str = None, content: bytes = None, cmd_id: int = 1):
    from mini.tool.pb2.PyPi_UploadScript_pb2 import UploadScript
    request = UploadScript()
    if file_name is not None:
        request.fileName = file_name
    if content is not None:
        request.content = content
    # message
    message: _Message = msg_utils.build_request_msg(cmd_id, 0, request)
    return message


# 上传python脚本到机器人
def upload_script(cmd_id: int, robot_id: str, file_name: str = None, content: bytes = None):
    if cmd_id == 1:
        py_cmd_id = _PCPyCmdId.PYPI_UPLOAD_SCRIPT_REQUEST.value
    elif cmd_id == 2:
        py_cmd_id = _PCPyCmdId.PYPI_CHECK_UPLOAD_SCRIPT_REQUEST.value
    elif cmd_id == 3:
        py_cmd_id = _PCPyCmdId.PYPI_RUN_UPLOAD_SCRIPT_REQUEST.value
    elif cmd_id == 4:
        py_cmd_id = _PCPyCmdId.PYPI_STOP_UPLOAD_SCRIPT_REQUEST.value
    elif cmd_id == 5:
        py_cmd_id = _PCPyCmdId.PYPI_LIST_UPLOAD_SCRIPT_REQUEST.value
    else:
        py_cmd_id = _PCPyCmdId.PYPI_LIST_UPLOAD_SCRIPT_REQUEST.value

    device: _WiFiDevice = _found_devices.get(robot_id)
    # 搜索设备
    if device is None:
        device = asyncio.get_event_loop().run_until_complete(mini.get_device_by_name(robot_id, 10))
        if device is None:
            print(f"Can't find AlphaMini of id (:{robot_id})")
            return
        else:
            _found_devices[robot_id] = device
    # 触发
    return asyncio.run(_send_msg0(_build_upload_script_msg(file_name, content, py_cmd_id), device))
