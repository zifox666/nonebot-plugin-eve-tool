from ...database.redis.cache import cache_async
from ..aioclient import aioClient


from nonebot import logger
from typing import *
import httpx


@cache_async(cache_expiry_seconds=600)
async def get_esi_kill_mail(kill_id: str) -> list:
    """
    拼接一个zkb用的kill mail
    """
    url = f"https://zkillboard.com/api/killID/{kill_id}/"
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.get(url)
        data = r.json()
        data = data[0]
        zkb = data.get('zkb')
        esi_url = f"https://esi.evetech.net/latest/killmails/{kill_id}/{zkb['hash']}/"
        kb_url = f"https://zkillboard.com/kill/{kill_id}/"
        zkb['esi'] = esi_url
        zkb['url'] = kb_url
        r = await client.get(esi_url)
        esi_data = r.json()
        esi_data['zkb'] = zkb
        return esi_data


