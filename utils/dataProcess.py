import json
from typing import List

from ..database.redis import search


async def process_orders(data: List[dict], type_id: int) -> dict:
    """
    处理数据，寻找sell和buy
    """
    min_sell_price = float('inf')
    max_buy_price = float('-inf')
    min_sell_volume = 0
    max_buy_volume = 0

    for order in data:
        if not order['is_buy_order']:
            min_sell_volume += order['volume_remain']
            if order['price'] < min_sell_price:
                min_sell_price = order['price']

        else:
            max_buy_volume += order['volume_remain']
            if order['price'] > max_buy_price:
                max_buy_price = order['price']

    if min_sell_price == float('inf'):
        min_sell_price = 0
    if max_buy_price == float('inf'):
        max_buy_price = 0

    return {
        'sell': min_sell_price,
        'sell_num': min_sell_volume,
        'buy': max_buy_price,
        'buy_num': max_buy_volume,
        'name': await search.get_names_for_redis(type_id)
    }
