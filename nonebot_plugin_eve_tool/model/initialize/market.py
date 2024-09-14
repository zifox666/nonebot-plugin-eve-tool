from nonebot import logger

from ...database.mysql.MysqlArray import MysqlArray
from ...database.redis.RedisArray import RedisArray
from ...utils.mission import refresh_price_cache, init_market_job


async def load_alias_to_redis(RA: RedisArray, MYSQL: MysqlArray):
    cursor = '0'
    while cursor != 0:
        cursor, keys = await RA.scan(cursor, match='alias:*', count=100)
        if keys:
            await RA.delete(*keys)
    data = await MYSQL.fetchall('SELECT alias, item FROM alias_items')
    for row in data:
        await RA.rpush(f"alias:{row['alias']}", row['item'])
        # await RA.hset(f"alias:{row['alias']}", f"alias:{row['alias']}", row['item'])

    logger.info("alias数据写入Redis完成")


async def load_price_list_to_redis():
    logger.info("开始拉取市场列表")
    await init_market_job()
