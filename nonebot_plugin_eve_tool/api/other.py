from .aioclient import aioClient

from nonebot import logger
from typing import *


async def get_short_url(long_url: str, call_qq: str, send_group: str = "private") -> str:
    """
    获取带标记的短链接
    :param long_url: 原链接
    :param call_qq: 请求链接的QQ
    :param send_group: 请求链接的群
    :return:返回短链接code
    """
    payload = {
        "long_url": long_url,
        "call_qq": call_qq,
        "send_group": send_group
    }
    data = await aioClient.post(uri="http://192.168.0.110:18000/shorten/", data=payload)
    return data["short_url"]


