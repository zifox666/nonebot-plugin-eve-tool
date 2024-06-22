from typing import *
from typing import Dict

from nonebot import logger

from .common import format_price, is_chinese
from ..api.esi.market import get_price_for_esi, get_price_for_ceve, get_price_for_tycoon
from ..database.redis.search import get_alias_for_redis, get_price_from_cache
from ..database.mysql.search import search_eve_types_for_mysql, get_ids_names_for_mysql


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
    elif api == 'esi_cache':
        return await get_price_from_cache(types_id)


async def get_marketer_price(item_name: str, api: str, num: int = 1, lagrange: str = 'zh') -> tuple[str, str]:
    # 彩蛋
    if item_name in special_cases:
        return special_cases[item_name]
    text = ""
    item_type = lagrange
    # 别名组查询
    items_list = await get_alias_for_redis(item_name)
    if items_list:
        type_dict = await get_ids_names_for_mysql(items_list,  item_name, "zh")
    else:
        if is_chinese(item_name):
            item_type = "zh"
        else:
            item_name = item_name.capitalize()
            item_type = "en"
            logger.debug("使用的是EN")
        type_dict = await search_eve_types_for_mysql(
            item_name,
            lagrange=item_type,
            market=True
        )
    logger.debug(type_dict)

    if type_dict["total"] == 0:
        return f"没有查询到[{item_name}]相关物品", str(0)

    if int(type_dict["total"]) <= 6:
        type_dict = type_dict
    else:
        keys = list(type_dict.keys())[:3]
        type_dict = {key: type_dict[key] for key in keys}
    type_dict.pop("total", None)
    results = await query_diversion(list(type_dict.keys()), api)

    buy_total = 0
    sell_total = 0
    cost = None
    for item in results:
        name = results[item]["name"]
        buy = float(0 if float(format_price(results[item]['buy']).replace(',', '')) == float('inf')
                    else format_price(results[item]['buy']).replace(',', ''))
        sell = float(0 if float(format_price(results[item]['sell']).replace(',', '')) == float('inf')
                     else format_price(results[item]['sell']).replace(',', ''))
        mid = (buy + sell) / 2
        if name != "None":
            text += f"### {name}\n" \
                    f"* 中间价：{mid:,.2f}\n" \
                    f"* 买单价格: {buy:,.2f}  ({results[item]['buy_num']})\n" \
                    f"* 卖单价格: {sell:,.2f}  ({results[item]['sell_num']})\n"
        buy_total += buy
        sell_total += sell
    buy_total = buy_total * num
    sell_total = sell_total * num
    text += f"\n> 买单总价(x{num})：{format_price(buy_total)} <br> 卖单总价(x{num})：{format_price(sell_total)}\n"
    return text, next(iter(type_dict.keys()))
