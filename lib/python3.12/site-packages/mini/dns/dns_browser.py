#!/usr/bin/env python3

import asyncio.events
import logging
import socket
from typing import Optional, Type

from ..dns import zeroconf as r
from ..dns.zeroconf import (
    ServiceBrowser,
    ServiceInfo,
    Zeroconf,
)

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
if log.level == logging.NOTSET:
    log.setLevel(logging.WARNING)

service_type = "_Dedu_mini_channel_server._tcp.local."


class WiFiDevice:
    def __init__(self, name: str = "", address: str = "localhost", port: int = -1, s_type: str = "", server: str = ""):
        super().__init__()
        self.address = address
        self.port = port
        self.type = s_type
        self.server = server

        if name.endswith(s_type):
            self.name = name[: -(len(s_type) + 1)]
        else:
            self.name = name

    def __repr__(self):
        return str(self.__class__) + " name:" + self.name + " address:" + self.address + " port:" + str(
            self.port) + " type:" + self.type + " server:" + self.server


class WiFiDeviceListener:
    def on_device_found(self, device: WiFiDevice) -> None:
        raise NotImplementedError()

    def on_device_updated(self, device: WiFiDevice) -> None:
        raise NotImplementedError()

    def on_device_removed(self, device: WiFiDevice) -> None:
        raise NotImplementedError()


class _InnerServiceListener(r.ServiceListener):
    # ServiceListener

    def __init__(self):
        self._listeners = set()
        self._found_devices = {}

    @property
    def found_devices(self):
        return self._found_devices

    def clear_devices(self):
        self._found_devices.clear()

    def add_listener(self, listener: WiFiDeviceListener):
        if listener is not None:
            self._listeners.add(listener)

    def remove_listener(self, listener: WiFiDeviceListener):
        if listener is not None:
            self._listeners.remove(listener)

    def remove_all_listener(self):
        self._listeners.clear()

    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        device = _WiFiBrowser.device_from_info(info)
        if device:
            log.info(f"Find Device:  {device}")
            self._found_devices[device.name] = device
            for listener in self._listeners:
                listener.on_device_found(device)

    def update_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        device = _WiFiBrowser.device_from_info(info)
        if device:
            log.info(f"Update Device: {device}")
            self._found_devices[device.name] = device
            for listener in self._listeners:
                listener.on_device_updated(device)

    def remove_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        device = _WiFiBrowser.device_from_info(info)
        if device:
            log.info(f"remove Device: {device}")
            del self._found_devices[device.name]
            for listener in self._listeners:
                listener.on_device_removed(device)


class _WiFiBrowser(object):
    __init_flag = False

    # 单例
    def __new__(cls, *args, **kwargs):
        if not hasattr(_WiFiBrowser, '_instance'):
            _WiFiBrowser._instance = object.__new__(cls)
        return _WiFiBrowser._instance

    def __init__(self):
        if not _WiFiBrowser.__init_flag:
            _WiFiBrowser.__init_flag = True
            log.info(f'init _WiFiBrowser')
            self._proxy = _InnerServiceListener()
            self._browser = None
            self._zc = None

    @property
    def found_devices(self):
        return tuple(self._proxy.found_devices)

    @property
    def scanning(self) -> bool:
        return self._browser and self._browser.is_alive()

    @staticmethod
    def device_from_info(info: ServiceInfo) -> Optional[WiFiDevice]:
        if info is None or len(info.addresses) == 0:
            return None
        return WiFiDevice(info.name, socket.inet_ntoa(info.addresses[0]), info.port, info.type, info.server)

    def add_listener(self, listener: WiFiDeviceListener):
        if listener is not None:
            self._proxy.add_listener(listener)

    def remove_listener(self, listener: WiFiDeviceListener):
        if listener is not None:
            self._proxy.remove_listener(listener)

    def remove_all_listener(self):
        self._proxy.remove_all_listener()

    def start_scan(self, timeout: int) -> bool:
        return self._start_scan(service_type, timeout)

    def stop_scan(self) -> bool:
        if self._browser:
            log.debug(f'browser cancel.')
            self._browser.cancel()
            self._browser = None

        if self._zc:
            log.debug(f'zc close.')
            self._zc.close()
            self._zc = None

        return True

    def _start_scan(self, s_type: str, timeout: int = 0) -> bool:
        # 开始扫描前先停止扫描
        self.stop_scan()
        log.debug('start scanner.')
        # 清空数据
        self._proxy.clear_devices()
        self._zc = Zeroconf()
        self._browser = ServiceBrowser(self._zc, s_type, listener=self._proxy)

        if timeout > 0:
            asyncio.get_event_loop().call_later(timeout, lambda: self.stop_scan())

        return True


browser: Type[_WiFiBrowser] = _WiFiBrowser
