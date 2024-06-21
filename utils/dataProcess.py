import json
from typing import List

from ..database.redis import search


async def process_orders(data: List[dict], type_id: int) -> dict:
    """
    处理数据，寻找sell和buy
    """
    min_sell_price = float('inf')
    max_buy_price = float('-inf')
    sell_volume = 0
    buy_volume = 0
    for order in data:
        if not order['is_buy_order']:
            sell_volume += order['volume_remain']
            if order['price'] < min_sell_price:
                min_sell_price = order['price']

        else:
            buy_volume += order['volume_remain']
            if order['price'] > max_buy_price:
                max_buy_price = order['price']

    if min_sell_price == float('inf'):
        min_sell_price = 0
    if max_buy_price == float('inf'):
        max_buy_price = 0

    return {
        'sell': min_sell_price,
        'sell_num': sell_volume,
        'buy': max_buy_price,
        'buy_num': buy_volume,
        'name': await search.get_names_for_redis(type_id)
    }


async def process_all(all_data: List[dict]) -> dict:
    price_list = {}
    min_sell_price = float('inf')
    max_buy_price = float('-inf')
    sell_volume = 0
    buy_volume = 0
    for order in all_data:
        if order["type_id"] not in price_list:
            price_list[order["type_id"]] = {
                'sell': min_sell_price,
                'sell_num': sell_volume,
                'buy': max_buy_price,
                'buy_num': buy_volume,
                'name': await search.get_names_for_redis(order["type_id"])
            }
        if not order['is_buy_order']:
            price_list[order["type_id"]]["sell_num"] += order['volume_remain']
            if order['price'] < price_list[order["type_id"]]["sell"]:
                price_list[order["type_id"]]["sell"] = order['price']
        else:
            price_list[order["type_id"]]["buy_num"] += order['volume_remain']
            if order['price'] > price_list[order["type_id"]]["buy"]:
                price_list[order["type_id"]]["buy"] = order['price']
    return price_list

