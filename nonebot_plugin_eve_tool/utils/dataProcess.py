import json
from typing import List

from nonebot import logger

from ..database.redis import search, RedisArray
from ..database.mysql.MysqlArray import MysqlArray
from ..model.config import plugin_config

MYSQL = MysqlArray(
    host=plugin_config.eve_mysql_host,
    port=plugin_config.eve_mysql_port,
    user=plugin_config.eve_mysql_user,
    password=plugin_config.eve_mysql_password,
    database=plugin_config.eve_mysql_db
)
RA = RedisArray(plugin_config.eve_redis_url)


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


async def insert_sub_listener(
        sub_type, entity_id, push_type, push_to, title, attack_value_limit=None, victim_value_limit=None
):
    try:
        await remove_listener(sub_type, entity_id, push_type, push_to)
    except Exception as e:
        logger.debug(e)
    redis_key = f"listener:{entity_id}"
    redis_value = json.dumps({
        'type': sub_type,
        'push_type': push_type,
        'push_to': push_to,
        'attack_value_limit': str(attack_value_limit),
        'victim_value_limit': str(victim_value_limit),
        'title': title
    })
    await RA.hset('listenerIdx', redis_key, redis_value)
    sql = """
    INSERT INTO listener (type, entity_id, push_type, push_to, attack_value_limit, victim_value_limit, title) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    args = (sub_type, entity_id, push_type, push_to, attack_value_limit, victim_value_limit, title)
    await MYSQL.execute(sql, args)


async def remove_all_listener(push_type, push_to):
    cursor = 0
    while True:
        cursor, keys = await RA.hscan('listenerIdx', cursor, match="listener:*")
        if not keys:
            break
        for key, value in keys.items():
            item = json.loads(value)
            if item.get('push_type') == push_type and item.get('push_to') == push_to:
                await RA.hdel('listenerIdx', key)
        if cursor == 0:
            break
    sql = """
    DELETE FROM listener WHERE push_type = %s AND push_to = %s
    """
    args = (push_type, push_to)
    await MYSQL.execute(sql, args)


async def remove_listener(sub_type, entity_id, push_type, push_to):
    redis_key = f"listener:{entity_id}"
    await RA.hdel('listenerIdx', redis_key)
    sql = """
    DELETE FROM listener WHERE push_type = %s AND push_to = %s AND entity_id = %s AND type = %s
    """
    args = (push_type, push_to, entity_id, sub_type)
    await MYSQL.execute(sql, args)


async def insert_high_listener(push_type, push_to, high_value_limit=None):
    try:
        await remove_high_listener(push_type, push_to)
    except Exception as e:
        logger.debug(e)
    redis_key = f"high_listener:{push_to}"
    redis_value = json.dumps({
        'high_value_limit': str(high_value_limit),
        'push_type': push_type,
        'push_to': push_to
    })
    await RA.hset('highListenerIdx', redis_key, redis_value)
    sql = "INSERT INTO high_listener (high_value_limit, push_type, push_to) VALUES (%s, %s, %s)"
    args = (high_value_limit, push_type, push_to)
    await MYSQL.execute(sql, args)


async def remove_high_listener(push_type, push_to):
    redis_key = f"high_listener:{push_to}"
    await RA.hdel('highListenerIdx', redis_key)
    sql = """
    DELETE FROM high_listener WHERE push_type = %s AND push_to = %s
    """
    args = (push_type, push_to)
    await MYSQL.execute(sql, args)
