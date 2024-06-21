from ...database.redis.cache import cache_async
from ..aioclient import aioClient

from nonebot import logger
from typing import *


@cache_async(cache_expiry_seconds=86400)
async def get_character_id(char_name: str) -> str | None:
    """
    查询角色id
    :param char_name: 角色名称
    :return: 如果有则返回角色id，无则为None
    """
    payload = [char_name]
    uri = 'https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en'
    data = await aioClient.post(uri, payload)
    try:
        return data['characters'][0]['id']
    except Exception as e:
        logger.error(e)
        return None


@cache_async(cache_expiry_seconds=86400)
async def get_char_name(char_id: int) -> str:
    """
    查询角色名称
    :param char_id: 角色id
    :return: 如果有则返回角色名称，无则为str(未知)
    """
    try:
        url = f"https://esi.evetech.net/latest/characters/{str(char_id)}/?datasource=tranquility"
        data = await aioClient.get(url)
        if "name" in data:
            return data["name"]
        else:
            return "未知"
    except Exception as e:
        logger.error(e)
        return "未知"


@cache_async(cache_expiry_seconds=86400)
async def get_char_title(char_id: int) -> str | None:
    """
    查询角色title
    :param char_id: 角色id
    :return: 如果有则返回角色title，无则为None
    """
    url = "https://esi.evetech.net/latest/characters/" + str(char_id)
    data = await aioClient.get(url)
    if 'title' in data:
        return data['title']
    else:
        return None


@cache_async(cache_expiry_seconds=86400)
async def get_system_name(system_id: int) -> Tuple[str, str | None]:
    """
    查询星系（system）名称以及星座id
    :param system_id:星系id
    :return:星系名称， 星座id | None
    """
    url = url = f'https://esi.evetech.net/latest/universe/systems/{str(system_id)}/?datasource=tranquility&language=zh'
    data = await aioClient.get(url)
    if "name" in data:
        return data["name"], data["constellation_id"]
    else:
        return "unknown", None


@cache_async(cache_expiry_seconds=86400)
async def get_alliance_name(alliance_id: int) -> Tuple[str, str]:
    """
    获取联盟名称和简写
    :param alliance_id: 联盟id
    :return: 联盟名称， 联盟简写
    """
    try:
        url = f"https://esi.evetech.net/latest/alliances/{str(alliance_id)}/?datasource=tranquility"
        data = await aioClient.get(url)
        logger.info(data)
        alliance_name = data['name']
        alliance_ticker = data['ticker']
        return alliance_name, alliance_ticker
    except Exception as e:
        logger.info(f"{e}")
        return "未知", ""


@cache_async(cache_expiry_seconds=86400)
async def get_corp_name(corp_id: int) -> Tuple[str, str]:
    """
        获取军团名称和简写
        :param corp_id: 联盟id
        :return: 联盟名称， 联盟简写
        """
    try:
        url = f"https://esi.evetech.net/latest/corporations/{str(corp_id)}/?datasource=tranquility"
        data = await aioClient.get(url)
        corp_name = data['name']
        corp_ticker = data['ticker']
        return corp_name, corp_ticker
    except Exception as e:
        logger.info(f"{e}")
        return "未知", ""


@cache_async(cache_expiry_seconds=86400)
async def get_constellation_name(constellation_id: int) -> Tuple[str, str | None]:
    """
    获取constellation信息
    :param constellation_id:
    :return: constellation名称, region id
    """
    url = url = (f'https://esi.evetech.net/latest/universe/constellations/{str(constellation_id)}/?datasource'
                 f'=tranquility&language=zh')
    data = await aioClient.get(url)
    if "name" in data:
        return data["name"], data["region_id"]
    else:
        return "unknown", None


@cache_async(cache_expiry_seconds=86400)
async def get_region_name(region_id: int) -> str:
    """
    获取region信息
    :param region_id:
    :return:
    """
    url = f'https://esi.evetech.net/latest/universe/regions/{str(region_id)}/?datasource=tranquility&language=zh'
    data = await aioClient.get(url)
    if "name" in data:
        return data["name"]
    else:
        return "unknown"


@cache_async(cache_expiry_seconds=86400)
async def get_moon_info(moon_id: int) -> List | None:
    """
    获取moon信息
    :param moon_id:
    :return:
    """
    url = f'https://esi.evetech.net/latest/universe/moons/{str(moon_id)}/?datasource=tranquility'
    data = await aioClient.get(url)
    if "name" in data:
        return data
    else:
        return None


@cache_async(cache_expiry_seconds=86400)
async def get_corp_id(corp_name: str) -> str | None:
    """
    获取军团id
    :param corp_name:
    :return:
    """
    payload = [corp_name]
    uri = 'https://esi.evetech.net/latest/universe/ids/?datasource=tranquility&language=en'
    data = await aioClient.post(uri, payload)
    try:
        return data['corporations'][0]['id']
    except Exception as e:
        logger.error(e)
        return None



