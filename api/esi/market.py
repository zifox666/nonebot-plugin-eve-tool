from typing import Dict, Any

import httpx

from ..aioclient import aioClient
from ...utils.dataProcess import process_orders
from ...database.redis import search

from nonebot import logger
from typing import *
import xml.etree.ElementTree as ET


async def get_price_for_ceve(types_id: List[int]) -> dict[str | None, dict[str, int | float | str]] | None:
    """
    通过ceve批量查询
    :param types_id:
    :return:
    """
    params = {
        'typeid': types_id,
        "regionlimit": 10000002,
        "usesystem": 30000142,
    }
    url = f"https://www.ceve-market.org/tqapi/marketstat"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params)
        if r.status_code == 200:
            result = {}
            data = r.text
            # 解析xml
            root = ET.fromstring(data).find('marketstat')
            for type_id in root:
                result[type_id.get("id")] = {"buy": float(type_id.find("buy").find("max").text),
                                             "buy_num": int(type_id.find("buy").find("volume").text),
                                             "sell": float(type_id.find("sell").find("min").text),
                                             "sell_num": int(type_id.find("sell").find("volume").text),
                                             "name": await search.get_names_for_redis(type_id.get("id"))}
            return result
        else:
            logger.error(r.status_code)
            return None


async def get_price_for_tycoon(types_id: List[int]) -> dict[int, dict[str, int | float | Any]]:
    """
    通过tycoon批量查询
    :param types_id:
    :return:
    """
    result = {}
    for type_id in types_id:
        url = f"https://evetycoon.com/api/v1/market/stats/10000002/{str(type_id)}"
        data = await aioClient.get(url)
        if data:
            result[type_id] = {"buy": 0 if data.get('maxBuy') == float('inf') else float(data.get('maxBuy', 0)),
                               "buy_num": int(data.get('buyOrders', 0)),
                               "sell": 0 if data.get('minSell') == float('inf') else float(data.get('minSell', 0)),
                               "sell_num": int(data.get('sellOrders', 0)),
                               "name": await search.get_names_for_redis(type_id)}

    return result


async def get_price_for_esi(types_id: List[int]) -> dict[int, dict[str, int | float | str]]:
    """
    通过esi批量查询价格
    :param types_id:
    :return:
    """
    result = {}
    print(types_id)
    for type_id in types_id:
        url = f"https://esi.evetech.net/latest/markets/10000002/orders/?&order_type=all&type_id={str(type_id)}"
        data = await aioClient.get(url)
        if data:
            result[type_id] = await process_orders(data, type_id)

    return result


async def get_price_history(type_id: int) -> dict[int, dict[str, int | float | str]]:
    """
    获取一年的历史价格
    """
    url = f"https://esi.evetech.net/latest/markets/10000002/history/?datasource&type_id={str(type_id)}"
    return await aioClient.get(url)

