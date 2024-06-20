from typing import *
from typing import Dict

from nonebot import logger

from .common import format_price, is_chinese
from ..api.esi.market import get_price_for_esi, get_price_for_ceve, get_price_for_tycoon
from ..database.redis.search import get_alias_for_redis, search_eve_types


special_cases = {
    "special666": "\n彩蛋"
}


async def query_diversion(types_id: List[int], api: str) -> dict:
    if api == 'ceve':
        return await get_price_for_ceve(types_id)
    elif api == 'esi':
        return await get_price_for_esi(types_id)
    elif api == 'tycoon':
        return await get_price_for_tycoon(types_id)


async def get_marketer_price(item_name: str, api: str, num: int = 1, lagrange: str = 'zh') -> str:
    # 彩蛋
    if item_name in special_cases:
        return special_cases[item_name]
    text = ""
    item_type = lagrange
    # 别名组查询
    items_list = await get_alias_for_redis(item_name)
    if items_list:
        item_num, type_dict = await search_eve_types(items_list, "zh")
    else:
        if is_chinese(item_name):
            item_type = "zh"
        else:
            item_name = item_name.capitalize()
            item_type = "en"
        item_num, type_dict = await search_eve_types(item_name, item_type)

    if item_num == 0:
        return f"没有查询到[{item_name}]相关物品"

    if item_num <= 6:
        type_dict = type_dict
    else:
        type_dict = type_dict[:3]

    results = await query_diversion(list(type_dict), api)

    buy_total = 0
    sell_total = 0
    cost = None
    for item in results:
        name = results[item]["name"]
        text += f"### {name}\n" \
                f"* 中间价：{format_price((results[item]['buy'] + results[item]['sell']) / 2)}\n" \
                f"* 买单价格: {format_price(results[item]['buy'])}  ({results[item]['buy_num']})\n" \
                f"* 卖单价格: {format_price(results[item]['sell'])}  ({results[item]['sell_num']})\n"
        buy_total += results[item]['buy']
        sell_total += results[item]['sell']
    buy_total = buy_total * num
    sell_total = sell_total * num
    text += f"\n> 买单总价(x{num})：{format_price(buy_total)} <br> 卖单总价(x{num})：{format_price(sell_total)}\n"
    return text
