import io
import json
import os
import random
import re
from pathlib import Path
from typing import (Dict, Literal,
                    Union, Optional, Tuple, Iterable, List, Any)
from urllib.parse import urlencode

import httpx
import nonebot.log
import nonebot.plugin
import tenacity
from qrcode import QRCode
from nonebot.log import logger

try:
    from loguru import Logger
except ImportError:
    Logger = None
    pass

from nonebot import Adapter, Bot, require

from nonebot.adapters.onebot.v11 import MessageEvent as OneBotV11MessageEvent, PrivateMessageEvent, GroupMessageEvent, \
    Adapter as OneBotV11Adapter, Bot as OneBotV11Bot

from ..model import plugin_config, data_path

__all__ = ["GeneralMessageEvent", "GeneralPrivateMessageEvent", "GeneralGroupMessageEvent", "CommandBegin",
           "get_last_command_sep", "COMMAND_BEGIN", "set_logger", "logger", "PLUGIN", "custom_attempt_times",
           "get_async_retry", "generate_seed_id", "get_file", "generate_qr_img", "read_blacklist", "read_whitelist",
           "read_admin_list", "get_wormholes", "get_currency_code", "remove_color", "is_chinese"]

GeneralMessageEvent = OneBotV11MessageEvent
"""消息事件类型"""
GeneralPrivateMessageEvent = PrivateMessageEvent
"""私聊消息事件类型"""
GeneralGroupMessageEvent = GroupMessageEvent
"""群聊消息事件类型"""


class CommandBegin:
    """
    命令开头字段
    （包括例如'/'和插件命令起始字段例如'eve_tool'）
    已重写__str__方法
    """
    string = ""
    '''命令开头字段（包括例如'/'和插件命令起始字段例如'eve_tool'）'''

    @classmethod
    def set_command_begin(cls):
        """
        机器人启动时设置命令开头字段
        """
        if nonebot.get_driver().config.command_start:
            cls.string = list(nonebot.get_driver().config.command_start)[0] + plugin_config.preference.command_start
        else:
            cls.string = plugin_config.preference.command_start

    @classmethod
    def __str__(cls):
        return cls.string


def get_last_command_sep():
    """
    获取第最后一个命令分隔符
    """
    if nonebot.get_driver().config.command_sep:
        return list(nonebot.get_driver().config.command_sep)[-1]


COMMAND_BEGIN = CommandBegin()
'''命令开头字段（包括例如'/'和插件命令起始字段例如'eve_tool'）'''


def set_logger(_logger: "Logger"):
    """
    给日志记录器对象增加输出到文件的Handler
    """
    # 根据"name"筛选日志，如果在 plugins 目录加载，则通过 LOG_HEAD 识别
    # 如果不是插件输出的日志，但是与插件有关，则也进行保存
    logger.add(
        plugin_config.preference.log_path,
        diagnose=False,
        format=nonebot.log.default_format,
        rotation=plugin_config.preference.log_rotation,
        filter=lambda x: True
    )

    return logger


logger = set_logger(logger)
"""本插件所用日志记录器对象（包含输出到文件）"""

PLUGIN = nonebot.plugin.get_plugin(plugin_config.preference.plugin_name)
'''本插件数据'''

if not PLUGIN:
    logger.warning(
        "插件数据(Plugin)获取失败，如果插件是从本地加载的，需要修改配置文件中 PLUGIN_NAME 为插件目录，否则将导致无法获取插件帮助信息等")


def custom_attempt_times(retry: bool):
    """
    自定义的重试机制停止条件\n
    根据是否要重试的bool值，给出相应的`tenacity.stop_after_attempt`对象

    :param retry True - 重试次数达到配置中 MAX_RETRY_TIMES 时停止; False - 执行次数达到1时停止，即不进行重试
    """
    if retry:
        return tenacity.stop_after_attempt(plugin_config.preference.max_retry_times + 1)
    else:
        return tenacity.stop_after_attempt(1)


def get_async_retry(retry: bool):
    """
    获取异步重试装饰器

    :param retry: True - 重试次数达到偏好设置中 max_retry_times 时停止; False - 执行次数达到1时停止，即不进行重试
    """
    return tenacity.AsyncRetrying(
        stop=custom_attempt_times(retry),
        retry=tenacity.retry_if_exception_type(BaseException),
        wait=tenacity.wait_fixed(plugin_config.preference.retry_interval),
    )


def generate_seed_id(length: int = 8) -> str:
    """
    生成随机的 seed_id（即长度为8的十六进制数）

    :param length: 16进制数长度
    """
    max_num = int("FF" * length, 16)
    return hex(random.randint(0, max_num))[2:]


async def get_file(url: str, retry: bool = True):
    """
    下载文件

    :param url: 文件URL
    :param retry: 是否允许重试
    :return: 文件数据
    """
    try:
        async for attempt in get_async_retry(retry):
            with attempt:
                async with httpx.AsyncClient() as client:
                    res = await client.get(url, timeout=plugin_config.preference.timeout, follow_redirects=True)
                return res.content
    except tenacity.RetryError:
        logger.exception(f"{plugin_config.preference.log_head}下载文件 - {url} 失败")


def generate_qr_img(data: str):
    """
    生成二维码图片

    :param data: 二维码数据
    """
    qr_code = QRCode(border=2)
    qr_code.add_data(data)
    qr_code.make()
    image = qr_code.make_image()
    image_bytes = io.BytesIO()
    image.save(image_bytes)
    return image_bytes.getvalue()


def _read_user_list(path: Path) -> List[str]:
    """
    从TEXT读取用户名单

    :return: 名单中的所有用户ID
    """
    if not path:
        return []
    if os.path.isfile(path):
        with open(path, "r", encoding=plugin_config.preference.encoding) as f:
            lines = f.readlines()
        lines = map(lambda x: x.strip(), lines)
        line_filter = filter(lambda x: x and x != "\n", lines)
        return list(line_filter)
    else:
        logger.error(f"{plugin_config.preference.log_head}黑/白名单文件 {path} 不存在")
        return []


def read_blacklist() -> List[str]:
    """
    读取黑名单

    :return: 黑名单中的所有用户ID
    """
    return _read_user_list(plugin_config.preference.blacklist_path) if plugin_config.preference.enable_blacklist else []


def read_whitelist() -> List[str]:
    """
    读取白名单

    :return: 白名单中的所有用户ID
    """
    return _read_user_list(plugin_config.preference.whitelist_path) if plugin_config.preference.enable_whitelist else []


def read_admin_list() -> List[str]:
    """
    读取白名单

    :return: 管理员名单中的所有用户ID
    """
    return _read_user_list(
        plugin_config.preference.admin_list_path) if plugin_config.preference.enable_admin_list else []


def is_chinese(word: str) -> bool:
    """
    判断中文字符

    :param word: 字符
    :return:
    """
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def remove_color(text: str) -> str:
    """
    去除彩色代码

    :param text: 需要去除的字符串
    :return:
    """
    text = re.sub(r'<color=.*?>', "", text)
    text = re.sub(r'</color>', "", text)
    text = re.sub(r'<b>', "", text)
    text = re.sub(r'</b>', "", text)
    return text


async def get_currency_code(currency: str) -> Optional[str]:
    """
    获取货币代码

    :param currency:
    :return:
    """
    # 打开currency_code.json文件
    with open(data_path + '/currency_code.json', 'r', encoding='utf-8') as f:
        currency_code = json.load(f)
    # 获取货币代码
    if currency.upper() in list(currency_code.keys()):
        return currency.upper()
    else:
        for c in currency_code.keys():
            if currency in currency_code[c]:
                return c
    return None


def get_wormholes(wormholes_name: str) -> List[str] | None:
    """
    获取虫洞数据

    :param wormholes_name:
    :return:
    """
    with open(data_path + '/wormholes.json', 'r', encoding='utf-8') as f:
        wormholes = json.load(f)
        if wormholes_name in wormholes.keys():
            return wormholes[wormholes_name]
        else:
            return None
