#!/usr/bin/env python3

# 每种传感器做一个单例对象进行监听

import asyncio
import enum

from ..apis.base_api import BaseEventApi, BaseApiNoNeedResponse
from ..apis.cmdid import _PCProgramCmdId
from ..pb2.codemao_facedetecttask_pb2 import FaceDetectTaskRequest, FaceDetectTaskResponse
from ..pb2.codemao_facerecognisetask_pb2 import FaceRecogniseTaskRequest, FaceRecogniseTaskResponse
from ..pb2.codemao_observefallclimb_pb2 import ObserveFallClimbRequest, ObserveFallClimbResponse
from ..pb2.codemao_observeheadracket_pb2 import ObserveHeadRacketRequest, ObserveHeadRacketResponse
from ..pb2.codemao_observeinfrareddistance_pb2 import ObserveInfraredDistanceRequest, ObserveInfraredDistanceResponse
from ..pb2.codemao_speechrecognise_pb2 import SpeechRecogniseRequest, SpeechRecogniseResponse
from ..pb2.codemao_stopspeechrecognise_pb2 import StopSpeechRecogniseRequest, StopSpeechRecogniseResponse
from ..pb2.pccodemao_message_pb2 import Message


class ObserveSpeechRecognise(BaseEventApi):
    """监听语音识别api

    监听语音识别事件,机器人上报语音识别后的文字

    #SpeechRecogniseResponse.text : 识别后的文字

    #SpeechRecogniseResponse.isSuccess : 是否成功

    #SpeechRecogniseResponse.resultCode : 返回码

    """

    async def execute(self):
        pass

    def __init__(self):

        cmd_id = _PCProgramCmdId.SPEECH_RECOGNISE.value

        message = SpeechRecogniseRequest()

        BaseEventApi.__init__(self, cmd_id=cmd_id, message=message)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            SpeechRecogniseResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = SpeechRecogniseResponse()
            response.ParseFromString(data)
            return response
        else:
            return None

    def stop(self):
        """
        停止语音识别,停止监听语音识别

        Returns:
            None
        """

        asyncio.create_task(_StopSpeechRecognise().execute())

        super().stop()


class _StopSpeechRecognise(BaseApiNoNeedResponse):
    """停止语音识别api

    #StopSpeechRecogniseResponse.isSuccess : 是否成功

    #StopSpeechRecogniseResponse.resultCode : 返回码
    """

    async def execute(self):
        """
        执行停止语音识别指令

        Returns:
            bool: 是否发送指令成功
        """

        request = StopSpeechRecogniseRequest()

        cmd_id = _PCProgramCmdId.STOP_SPEECH_RECOGNISE_REQUEST.value

        return await self.send(cmd_id, request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            StopSpeechRecogniseResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = StopSpeechRecogniseResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class ObserveFaceDetect(BaseEventApi):
    """监听人脸个数api

    监听人脸个数事件,机器人上报检测到的人脸个数

    单次检测超时时间1s,侦测间隔1s

    # FaceDetectTaskResponse.count(int) : 人脸个数

    # FaceDetectTaskResponse.isSuccess : 是否成功

    # FaceDetectTaskResponse.resultCode : 返回码
    """

    async def execute(self):
        pass

    def __init__(self):

        cmd_id = _PCProgramCmdId.FACE_DETECT_TASK_REQUEST.value

        request = FaceDetectTaskRequest()

        # 单次侦测超时时间
        request.timeout = 1000

        # 侦测间隔时间
        request.period = 1000

        # 任务延时时间
        request.delay = 0

        # 检测开关
        request.switch = True

        BaseEventApi.__init__(self, cmd_id=cmd_id, message=request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            FaceDetectTaskResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = FaceDetectTaskResponse()
            response.ParseFromString(data)
            return response
        else:
            return None

    def stop(self):
        """
        停止人脸个数检测,停止监听人脸个数

        Returns:
            None
        """

        asyncio.create_task(_StopFaceDetect().execute())

        super().stop()


class _StopFaceDetect(BaseApiNoNeedResponse):
    """停止人脸个数检测api

    """

    async def execute(self):
        """
        执行停止人脸个数检测指令

        Returns:
            None
        """

        request = FaceDetectTaskRequest()

        # 检测开关
        request.switch = False

        cmd_id = _PCProgramCmdId.FACE_DETECT_TASK_REQUEST.value

        return await self.send(cmd_id, request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            FaceDetectTaskResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = FaceDetectTaskResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class ObserveFaceRecognise(BaseEventApi):
    """监听人脸识别api

    监听人脸识别事件,机器人上报识别到的人脸信息(数组)

    如果是已注册的人脸,返回人脸详细信息：id,名字,性别,年龄

    如果是陌生人,返回 name: "stranger"

    单次检测超时时间1s,侦测间隔1s

    # FaceRecogniseTaskResponse.faceInfos: [FaceInfoResponse] 人脸信息数组

    # FaceInfoResponse.id, FaceInfoResponse.name,FaceInfoResponse.gender,FaceInfoResponse.age：人脸详细信息

    # FaceRecogniseTaskResponse.isSuccess：是否成功

    # FaceRecogniseTaskResponse.resultCode：返回码

    """

    async def execute(self):
        pass

    def __init__(self):

        cmd_id = _PCProgramCmdId.FACE_RECOGNISE_TASK_REQUEST.value

        request = FaceRecogniseTaskRequest()

        # 单次侦测超时时间
        request.timeout = 1000

        # 侦测间隔时间
        request.period = 1000

        # 任务延时时间
        request.delay = 0

        # 检测开关
        request.switch = True

        BaseEventApi.__init__(self, cmd_id=cmd_id, message=request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            FaceRecogniseTaskResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = FaceRecogniseTaskResponse()
            response.ParseFromString(data)
            return response
        else:
            return None

    def stop(self):
        """
        停止人脸识别,停止监听人脸识别

        Returns:
            None
        """

        asyncio.create_task(_StopFaceRecognise().execute())

        super().stop()


class _StopFaceRecognise(BaseApiNoNeedResponse):
    """停止人脸识别api

    """

    async def execute(self):
        """
        执行停止人脸识别指令

        Returns:
            FaceRecogniseTaskResponse
        """

        request = FaceRecogniseTaskRequest()

        # 检测开关
        request.switch = False

        cmd_id = _PCProgramCmdId.FACE_RECOGNISE_TASK_REQUEST.value

        return await self.send(cmd_id, request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            FaceRecogniseTaskResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = FaceRecogniseTaskResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


class ObserveInfraredDistance(BaseEventApi):
    """监听红外距离api

    监听红外距离事件,机器人上报检测到的与面前最近障碍物的红外距离

    检测周期1s

    # ObserveInfraredDistanceResponse.distance：红外距离

    """

    async def execute(self):
        pass

    def __init__(self):

        cmd_id = _PCProgramCmdId.SUBSCRIBE_INFRARED_DISTANCE_REQUEST.value

        request = ObserveInfraredDistanceRequest()

        # 检测周期
        request.samplingPeriod = 1000

        # 检测开关
        request.isSubscribe = True

        BaseEventApi.__init__(self, cmd_id=cmd_id, message=request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ObserveInfraredDistanceResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ObserveInfraredDistanceResponse()
            response.ParseFromString(data)
            return response
        else:
            return None

    def stop(self):
        """
        停止红外距离检测,停止监听红外距离

        Returns:
            None
        """

        asyncio.create_task(_StopObserveInfraredDistance().execute())

        super().stop()


class _StopObserveInfraredDistance(BaseApiNoNeedResponse):
    """停止红外距离监测api

    """

    async def execute(self):
        """
        执行停止红外监测指令

        Returns:
            ObserveInfraredDistanceResponse
        """

        request = ObserveInfraredDistanceRequest()

        # 检测开关
        request.isSubscribe = False

        cmd_id = _PCProgramCmdId.FACE_RECOGNISE_TASK_REQUEST.value

        return await self.send(cmd_id, request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ObserveInfraredDistanceResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ObserveInfraredDistanceResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


@enum.unique
class RobotPosture(enum.Enum):
    """
    机器人姿势

    STAND : 站立

    SPLITS_LEFT : 左弓步

    SPLITS_RIGHT : 右弓步

    SIT_DOWN : 坐下

    SQUAT_DOWN : 蹲下

    KNEELING : 跪下

    LYING : 侧躺

    LYING_DOWN : 平躺

    SPLITS_LEFT_1 : 左劈叉

    SPLITS_RIGHT_2 : 右劈叉

    BEND : 弯腰
    """
    STAND = 1  # 站立
    SPLITS_LEFT = 2  # 左弓步
    SPLITS_RIGHT = 3  # 右弓步
    SIT_DOWN = 4  # 坐下
    SQUAT_DOWN = 5  # 蹲下
    KNEELING = 6  # 跪下
    LYING = 7  # 侧躺
    LYING_DOWN = 8  # 平躺
    SPLITS_LEFT_1 = 9  # 左劈叉
    SPLITS_RIGHT_2 = 10  # 右劈叉
    BEND = 11  # 弯腰


class ObserveRobotPosture(BaseEventApi):
    """监听机器人姿态api

    监听机器人姿态变化事件,机器上报当前的姿态RobotPosture(当发生姿态发生改变的时候)

    #ObserveFallClimbResponse.status : 机器姿态,数值对应RobotPosture

    """

    async def execute(self):
        pass

    def __init__(self):

        cmd_id = _PCProgramCmdId.SUBSCRIBE_ROBOT_POSTURE_REQUEST.value

        request = ObserveFallClimbRequest()

        # 检测开关
        request.isSubscribe = True

        BaseEventApi.__init__(self, cmd_id=cmd_id, message=request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ObserveFallClimbResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ObserveFallClimbResponse()
            response.ParseFromString(data)
            return response
        else:
            return None

    def stop(self):
        """
        停止机器人姿势检测,停止监听机器人姿势

        Returns:
            None
        """

        asyncio.create_task(_StopObserveRobotPosture().execute())

        super().stop()


class _StopObserveRobotPosture(BaseApiNoNeedResponse):
    """停止监听机器人姿态api

    """

    async def execute(self):
        """
        执行停止机器人姿态监测

        Returns:
            ObserveFallClimbResponse
        """

        request = ObserveFallClimbRequest()

        # 检测开关
        request.isSubscribe = False

        cmd_id = _PCProgramCmdId.SUBSCRIBE_ROBOT_POSTURE_REQUEST.value

        return await self.send(cmd_id, request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ObserveFallClimbResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ObserveFallClimbResponse()
            response.ParseFromString(data)
            return response
        else:
            return None


@enum.unique
class HeadRacketType(enum.Enum):
    """
    拍头方式

    SINGLE_CLICK : 单击

    LONG_PRESS : 长按

    DOUBLE_CLICK : 双击
    """
    SINGLE_CLICK = 1  # 单击
    LONG_PRESS = 2  # 长按
    DOUBLE_CLICK = 3  # 双击


class ObserveHeadRacket(BaseEventApi):
    """监听拍头事件api

    监听拍头事件,当机器人头部被拍击时,上报拍头类型

    # ObserveHeadRacketResponse.type : 拍头类型,HeadRacketType

    """

    async def execute(self):
        pass

    def __init__(self):

        cmd_id = _PCProgramCmdId.SUBSCRIBE_HEAD_RACKET_REQUEST.value

        message = ObserveHeadRacketRequest()

        # 检测开关
        message.isSubscribe = True

        BaseEventApi.__init__(self, cmd_id=cmd_id, message=message)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ObserveHeadRacketResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ObserveHeadRacketResponse()
            response.ParseFromString(data)
            return response
        else:
            return None

    def stop(self):
        """
        停止机器人拍头事件检测,停止监听机器人拍头事件

        Returns:
            None
        """

        asyncio.create_task(_StopObserveHeadRacket().execute())

        super().stop()


class _StopObserveHeadRacket(BaseApiNoNeedResponse):
    """停止拍头事件监测api

    """

    async def execute(self):
        """
        执行停止拍头事件监测指令

        Returns:
            ObserveHeadRacketResponse
        """

        request = ObserveHeadRacketRequest()

        # 检测开关
        request.isSubscribe = False

        cmd_id = _PCProgramCmdId.SUBSCRIBE_ROBOT_POSTURE_REQUEST.value

        return await self.send(cmd_id, request)

    def _parse_msg(self, message):
        """

        Args:
            message (Message):待解析的Message对象

        Returns:
            ObserveHeadRacketResponse
        """
        if isinstance(message, Message):
            data = message.bodyData
            response = ObserveHeadRacketResponse()
            response.ParseFromString(data)
            return response
        else:
            return None
