#!/usr/bin/env python3

import enum


@enum.unique
class _PCProgramCmdId(enum.Enum):
    """
    pcCodeMao的命令号配置
    """

    RESPONSE_BASE = 1000

    PLAY_ACTION_REQUEST = 1
    """播放动作
    """

    MOVE_ROBOT_REQUEST = 2
    """移动机器人
    """

    STOP_ACTION_REQUEST = 3
    """停止动作
    """

    PLAY_TTS_REQUEST = 4
    """播放tts
    """

    FACE_DETECT_REQUEST = 5
    """人脸个数识别
    """

    FACE_ANALYSIS_REQUEST = 6
    """识别人脸 （男性 女性）
    """

    RECOGNISE_OBJECT_REQUEST = 7
    """物体 手势 花草识别
    """

    FACE_RECOGNISE_REQUEST = 8
    """识别到某人
    """

    TAKE_PICTURE_REQUEST = 9
    """拍照
    """

    PLAY_EXPRESSION_REQUEST = 10
    """播放表情
    """

    SET_MOUTH_LAMP_REQUEST = 11
    """设置嘴巴灯
    """

    SUBSCRIBE_INFRARED_DISTANCE_REQUEST = 12
    """订阅红外检测障碍物距离：监听
    """

    SUBSCRIBE_ROBOT_POSTURE_REQUEST = 13
    """订阅机器人姿态：监听
    """

    SUBSCRIBE_HEAD_RACKET_REQUEST = 14
    """订阅拍头事件：监听
    """

    CONTROL_BEHAVIOR_REQUEST = 15
    """控制行为
    """

    GET_ROBOT_VERSION_REQUEST = 16
    """获取版本号
    """
    GET_ROBOT_VERSION_RESPONSE = RESPONSE_BASE + GET_ROBOT_VERSION_REQUEST

    GET_INFRARED_DISTANCE_REQUEST = 19
    """获取红外距离
    """

    REVERT_ORIGIN_REQUEST = 20
    """停止所有操作
    """

    DISCONNECTION_REQUEST = 21
    """断开tcp
    """

    SWITCH_MOUTH_LAMP_REQUEST = 22
    """开关嘴巴灯
    """

    PLAY_AUDIO_REQUEST = 23
    """播放音效
    """

    STOP_AUDIO_REQUEST = 24
    """停止音效
    """

    GET_AUDIO_LIST_REQUEST = 25
    """获取音效列表
    """

    TRANSLATE_REQUEST = 26
    """翻译
    """

    WIKI_REQUEST = 27
    """百科
    """

    CHANGE_ROBOT_VOLUME_REQUEST = 28
    """改变机器人音量
    """

    PLAY_ONLINE_MUSIC_REQUEST = 29
    """播放在线音乐
    """

    FACE_DETECT_TASK_REQUEST = 30
    """人脸侦测任务(持续侦测)：监听
    """

    GET_REGISTER_FACES_REQUEST = 31
    """获取熟人列表
    """

    FACE_RECOGNISE_TASK_REQUEST = 32
    """人脸识别（持续识别）：监听
    """

    GET_ACTION_LIST = 33
    """获取机器人动作列表
    """

    CONTROL_ROBOT_AUDIO_RECORD = 34
    """控制机器人录音/播放/暂停等
    """

    SPEECH_RECOGNISE = 35
    """语音识别：监听
    """

    GET_SERVER_INFO = 36
    """获取服务器信息
    """

    PLAY_CUSTOM_ACTION_REQUEST = 37
    """播放自定义动作
    """

    STOP_CUSTOM_ACTION_REQUEST = 38
    """停止自定义动作
    """

    STOP_SPEECH_RECOGNISE_REQUEST = 39
    """停止语音识别
    """

    GET_ROBOT_LANGUAGE_MODE = 40
    """获取机器人语言模型
    """

    SET_ROBOT_LANGUAGE = 41
    """设置机器人语言
    """
