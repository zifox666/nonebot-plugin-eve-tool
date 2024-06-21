from ...database.redis.cache import cache_async
from ..aioclient import aioClient


from nonebot import logger
from typing import *


@cache_async(cache_expiry_seconds=600)
async def get_kill_mails(killID: int, hash: str):
    """
    获取kill mail信息
    :param killID:
    :param hash:
    :return:
    """
    url = f"https://esi.evetech.net/latest/killmails/{str(killID)}/{hash}/"
    data = await aioClient.get(url)
    return data


