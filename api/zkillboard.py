from ..database.redis.cache import cache_async
from .aioclient import aioClient

from nonebot import logger
from typing import *


@cache_async(cache_expiry_seconds=86400)
async def get_zkb_info(killID: int):
    """
    获取角色zkb信息
    :param killID:
    :return:
    """
    url = f"https://zkillboard.com/api/stats/characterID/{str(killID)}/"
    response = await aioClient.get(url)
    data = response.json()
    return data


@cache_async(cache_expiry_seconds=86400)
async def get_corp_info(corp_id: str):
    """
    获取zkb军团信息
    :param corp_id:
    :return:
    """
    url = f'https://zkillboard.com/api/stats/corporationID/{corp_id}/'
    return await aioClient.get(url)
