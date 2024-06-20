import json
from nonebot import logger

from ...database.mysql.MysqlArray import MysqlArray
from ...database.redis.RedisArray import RedisArray


async def load_listener_to_redis(RA: RedisArray, MYSQL: MysqlArray):
    listener_data = await MYSQL.fetchall("SELECT * FROM listener")
    high_listener_data = await MYSQL.fetchall("SELECT * FROM high_listener")

    await RA.execute('FT.CREATE', 'listenerIdx', 'ON', 'HASH', 'PREFIX', '1', 'listener:',
                     'SCHEMA', 'entity_id', 'TAG', 'attack_value_limit', 'NUMERIC', 'victim_value_limit', 'NUMERIC')

    for row in listener_data:
        redis_key = f"listener:{row['entity_id']}"
        redis_value = json.dumps({
            'type': row['type'],
            'push_type': row['push_type'],
            'push_to': row['push_to'],
            'attack_value_limit': str(row['attack_value_limit']),
            'victim_value_limit': str(row['victim_value_limit']),
            'title': row['title']
        })
        await RA.hset('listenerIdx', redis_key, redis_value)
    logger.info("listener数据写入Redis完成")

    await RA.execute('FT.CREATE', 'highListenerIdx', 'ON', 'HASH', 'PREFIX', '1', 'high_listener:',
                     'SCHEMA', 'high_value_limit', 'NUMERIC', 'push_type', 'TEXT', 'push_to', 'TEXT')

    for row in high_listener_data:
        redis_key = f"high_listener:{row['id']}"
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
