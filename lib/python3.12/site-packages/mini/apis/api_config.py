import enum

from mini.apis.base_api import BaseApi, DEFAULT_TIMEOUT
from mini.apis.cmdid import _PCProgramCmdId
from mini.pb2.pccodemao_getrobotlanguage_pb2 import GetRobotLanguageRequest, GetRobotLanguageResponse
from ..pb2.pccodemao_message_pb2 import Message
from ..pb2.pccodemao_setrobotlanguage_pb2 import SetRobotLanguageRequest, SetRobotLanguageResponse


@enum.unique
class LanType(enum.Enum):
    """
    语言类型

    国家的缩写

    """
    CN = 0
    EN = 1
    TW = 2
    FR = 3
    DE = 4
    EL = 5
    JA = 6
    KO = 7
    RU = 8
    CS = 9
    DA = 10
    NL = 11
    FI = 12
    BN = 13
    AF = 14
    EU = 15
    BG = 16
    BE = 17
    EO = 18
    ID = 19
    IT = 20
    GA = 21
    KY = 22
    LA = 23
    LO = 24
    MS = 25
    NO = 26
    FA = 27
    PT = 28
    SR = 29
    SO = 30
    UZ = 31
    ZU = 32
    YO = 33
    VI = 34
    TH = 35
    TG = 36
    SK = 37
    AR = 38
    MN = 39
    MY = 40
    TL = 41


@enum.unique
class ServicePlatform(enum.Enum):
    """
    服务平台

    BAIDU : 百度

    TENCENT : 腾讯

    GOOGLE : 谷歌

    """
    BAIDU = 0
    TENCENT = 1
    GOOGLE = 2


class GetRobotLanguage(BaseApi):
    """获取机器人语言 api

    Returns:
            GetRobotLanguageResponse

    #GetRobotLanguageResponse.isSuccess

    #GetRobotLanguageResponse.resultCode

    #GetRobotLanguageResponse.language
    """

    def __init__(self, is_serial: bool = True):
        self.__isSerial = is_serial

    async def execute(self):
        """执行获取机器人语言

        Returns:
                GetRobotLanguageResponse

        #GetRobotLanguageResponse.isSuccess

        #GetRobotLanguageResponse.resultCode

        #GetRobotLanguageResponse.language
        """
        timeout = 0
        if self.__isSerial:
            timeout = DEFAULT_TIMEOUT

        request = GetRobotLanguageRequest()

        cmd_id = _PCProgramCmdId.GET_ROBOT_LANGUAGE_MODE.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            GetRobotLanguageResponse

        """
        if isinstance(message, Message):
            data = message.bodyData
            response = GetRobotLanguageResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


@enum.unique
class RobotLanguage(enum.Enum):
    """机器人支持的语言"""
    en_US = 0
    ru_RU = 1


class SetRobotLanguage(BaseApi):
    """设置机器人语言模型 api

    Returns:
            SetRobotLanguageResponse

    #SetRobotLanguageResponse.isSuccess

    #SetRobotLanguageResponse.resultCode

    #SetRobotLanguageResponse.progress

    #SetRobotLanguageResponse.total

    #SetRobotLanguageResponse.state
    """

    def __init__(self, is_serial: bool = True, language: RobotLanguage = RobotLanguage.en_US):
        assert isinstance(language, RobotLanguage), 'SetRobotLanguage : language should be #RobotLanguage# enum type'
        self.__is_serial: bool = is_serial
        self.__language: RobotLanguage = language

    async def execute(self):
        """执行设置机器人语言模型

        Returns:
            SetRobotLanguageResponse

        #SetRobotLanguageResponse.isSuccess

        #SetRobotLanguageResponse.resultCode

        #SetRobotLanguageResponse.progress

        #SetRobotLanguageResponse.total

        #SetRobotLanguageResponse.state
        """
        timeout = 0
        if self.__is_serial:
            timeout = DEFAULT_TIMEOUT

        request = SetRobotLanguageRequest()
        request.language = self.__language.name

        cmd_id = _PCProgramCmdId.SET_ROBOT_LANGUAGE.value

        return await self.send(cmd_id, request, timeout)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            SetRobotLanguageResponse

        """
        if isinstance(message, Message):
            data = message.bodyData
            response = SetRobotLanguageResponse()
            response.ParseFromString(data)
            return response
        else:
            return None
