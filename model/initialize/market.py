from nonebot import logger

from ...database.mysql.MysqlArray import MysqlArray
from ...database.redis.RedisArray import RedisArray


async def load_alias_to_redis(RA: RedisArray, MYSQL: MysqlArray):
    data = await MYSQL.fetchall('SELECT alias, item FROM alias_items')

    for row in data:
        await RA.rpush(f"alias:{row['alias']}", row['item'])

    logger.info("alias数据写入Redis完成")
