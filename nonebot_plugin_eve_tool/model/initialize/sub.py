import json
from collections import defaultdict

from nonebot import logger

from ...database.mysql.MysqlArray import MysqlArray
from ...database.redis.RedisArray import RedisArray


async def load_listener_to_redis(RA: RedisArray, MYSQL: MysqlArray):
    listener_data = await MYSQL.fetchall("SELECT * FROM listener")
    high_listener_data = await MYSQL.fetchall("SELECT * FROM high_listener")

    listener_dict = defaultdict(list)
    for row in listener_data:
        redis_value = {
            'type': row['type'],
            'push_type': row['push_type'],
            'push_to': row['push_to'],
            'attack_value_limit': int(row['attack_value_limit']),
            'victim_value_limit': int(row['victim_value_limit']),
            'title': row['title']
        }
        listener_dict[row['entity_id']].append(redis_value)

    for entity_id, values in listener_dict.items():
        redis_key = f"listener:{entity_id}"
        redis_value = json.dumps(values)
        await RA.hset('listenerIdx', redis_key, redis_value)
    logger.info("listener数据写入Redis完成")

    for row in high_listener_data:
        redis_key = f"high_listener:{row['push_to']}"
        redis_value = json.dumps({
            'high_value_limit': str(row['high_value_limit']),
            'push_type': row['push_type'],
            'push_to': row['push_to']
        })
        await RA.hset('highListenerIdx', redis_key, redis_value)
    logger.info("highListener数据写入Redis完成")

    return True


async def load_alias_to_redis(RA: RedisArray, MYSQL: MysqlArray):
    data = await MYSQL.fetchall('SELECT alias, item FROM alias_items')

    for row in data:
        await RA.rpush(f"alias:{row['alias']}", row['item'])

    logger.info("alias数据写入Redis完成")
