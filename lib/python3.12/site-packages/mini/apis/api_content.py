#!/usr/bin/env python3

from ..apis.api_config import LanType, ServicePlatform
from ..apis.base_api import BaseApi, DEFAULT_TIMEOUT
from ..apis.cmdid import _PCProgramCmdId
from ..pb2.cloudtranslate_pb2 import Translate
from ..pb2.cloudwiki_pb2 import WiKi
from ..pb2.codemao_translate_pb2 import TranslateResponse, TranslateRequest
from ..pb2.codemao_wiki_pb2 import WikiRequest, WikiResponse
from ..pb2.pccodemao_message_pb2 import Message


class QueryWiKi(BaseApi):
    """百科api

    默认腾讯百科

    Args:
        is_serial (bool): 是否等待回复,默认True
        query (str): 查询的内容,不能为空或None

    #WikiResponse.isSuccess : 是否成功

    #WikiResponse.resultCode : 返回码
    """

    def __init__(self, is_serial: bool = True, query: str = None):
        assert isinstance(query, str) and len(query), 'QueryWiKi query should be available'
        self.__is_serial = is_serial
        self.__query = query
        self.__platform = ServicePlatform.TENCENT.value

    async def execute(self):
        """
        执行百科指令

        Returns:
            WikiResponse

        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        wiki = WiKi()
        wiki.query = self.__query
        wiki.platform = self.__platform

        request = WikiRequest()
        request.wiki.CopyFrom(wiki)

        cmd_id = _PCProgramCmdId.WIKI_REQUEST.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            WikiResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = WikiResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class StartTranslate(BaseApi):
    """翻译api

    默认百度翻译

    Args:
        is_serial (bool): 是否等待回复,默认True
        query (str): 翻译的内容,不能为空或None
        from_lan (LanType): 翻译的原文语言,默认CN,中文
        to_lan (LanType):  翻译的目标语言,默认EN,英文
        platform (ServicePlatform): 翻译平台,默认BAIDU,使用百度翻译

    #TranslateResponse.isSuccess : 是否成功

    #TranslateResponse.resultCode : 返回码

    """

    def __init__(self, is_serial: bool = True, query: str = None,
                 from_lan: LanType = LanType.CN,
                 to_lan: LanType = LanType.EN,
                 platform: ServicePlatform = ServicePlatform.BAIDU):
        assert isinstance(query, str) and len(query) > 0, 'Translate : query should be available'
        assert isinstance(from_lan, LanType), 'Translate : from_lan should be LanType instance'
        assert isinstance(to_lan, LanType), 'Translate : to_lan should be LanType instance'
        assert isinstance(platform, ServicePlatform), 'Translate : platform should be ServicePlatform instance'
        self.__is_serial = is_serial
        self.__query = query
        # self.__prefix = prefix
        # self.__suffix = suffix
        self.__from_lan = from_lan.value
        self.__to_lan = to_lan.value
        self.__platform = platform.value

    async def execute(self):
        """
        执行翻译指令

        Returns:
            TranslateResponse
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        translate = Translate()
        translate.query = self.__query
        # translate.prefix = self.__prefix
        # translate.suffix = self.__suffix
        translate.platform = self.__platform
        # translate.from = self.__fromLan
        setattr(translate, "from", self.__from_lan)
        translate.to = self.__to_lan
        # setattr(translate, "to", self.__toLan)

        request = TranslateRequest()
        request.translate.CopyFrom(translate)

        cmd_id = _PCProgramCmdId.TRANSLATE_REQUEST.value
        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            TranslateResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = TranslateResponse()
            response.ParseFromString(data)
            return response
        else:
            return None
