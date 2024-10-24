import httpx

from ..database.redis.cache import cache_async, retry_on_timeout_async
from ..model import plugin_config

from nonebot import logger
from typing import *


proxy = plugin_config.eve_proxy


@cache_async(cache_expiry_seconds=86400)
@retry_on_timeout_async(retries=3, delay=0.5)
async def get_zkb_info(killID: str):
    """
    获取角色zkb信息
    :param killID:
    :return:
    """
    url = f"https://zkillboard.com/api/stats/characterID/{str(killID)}/"
    async with httpx.AsyncClient(proxies=proxy, timeout=120.0) as client:
        r = await client.get(url)
        return r.json()


@cache_async(cache_expiry_seconds=86400)
async def get_corp_info(corp_id: str):
    """
    获取zkb军团信息
    :param corp_id:
    :return:
    """
    url = f'https://zkillboard.com/api/stats/corporationID/{corp_id}/'
    async with httpx.AsyncClient(proxies=proxy, timeout=120.0) as client:
        r = await client.get(url)
        return r.json()
