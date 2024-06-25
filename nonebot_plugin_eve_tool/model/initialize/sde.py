import gc
import tracemalloc
from pathlib import Path


from ...database.mysql.MysqlArray import MysqlArray
from ...database.redis.RedisArray import RedisArray
from ...utils.common import check_files_exist, download_sde

from nonebot import logger


async def load_sde_to_redis(RA: RedisArray, MYSQL: MysqlArray) -> bool:
    """
    从Mysql读取SDE存放到Redis方便查询
    初始化操作
    """
    eve_type_data = None
    try:
        eve_type_data = await MYSQL.fetchall(
            "SELECT id, name, name_en FROM eve_type WHERE meta_group_id LIKE '15' OR market_group_id IS NOT NULL")

        for row in eve_type_data:
            redis_key = f"eve_type:{row['id']}"
            await RA.hset(redis_key, 'name', row['name'] if row['name'] else row['name_en'])
            await RA.hset(redis_key, 'name_en', row['name_en'])
    finally:
        del eve_type_data
        gc.collect()

        logger.info("eve_type数据写入Redis完成")
    return True


async def check_eve_sde_path(sde_path: Path) -> bool | str:
    """
    判断SDE文件
    """
    files = ["types.yaml", "marketGroups.yaml", "metaGroups.yaml", "groups.yaml", "categories.yaml"]
    if check_files_exist((sde_path / 'fsd'), files):
        logger.info('SDE文件已导入')
    else:
        logger.info('SDE文件不存在，开始下载')
        Path(sde_path).mkdir(parents=True, exist_ok=True)
        if await download_sde(sde_path):
            logger.success("SDE数据下载完成，开始解压")
            return True
        else:
            raise FileNotFoundError(f'SDE自动下载失败，请手动放置SDE文件到{sde_path}下')


"""async def load_sde_to_redis(RA: RedisArray, MYSQL: MysqlArray) -> bool:
    
    tracemalloc.start()

    eve_type_data = None
    try:
        log_memory_usage("Before fetching data")
        snapshot1 = tracemalloc.take_snapshot()

        eve_type_data = await MYSQL.fetchall(
            "SELECT id, name, name_en FROM eve_type WHERE meta_group_id LIKE '15' OR market_group_id IS NOT NULL")

        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        print("[ Top 10 differences after fetching data ]")
        for stat in top_stats[:10]:
            print(stat)

        log_memory_usage("After fetching data")

        for row in eve_type_data:
            redis_key = f"eve_type:{row['id']}"
            await RA.hset(redis_key, 'name', row['name'] if row['name'] else row['name_en'])
            await RA.hset(redis_key, 'name_en', row['name_en'])

        snapshot3 = tracemalloc.take_snapshot()
        top_stats = snapshot3.compare_to(snapshot2, 'lineno')
        print("[ Top 10 differences after Redis insertion ]")
        for stat in top_stats[:10]:
            print(stat)

        log_memory_usage("After inserting into Redis")

    finally:
        del eve_type_data
        gc.collect()

        snapshot4 = tracemalloc.take_snapshot()
        top_stats = snapshot4.compare_to(snapshot3, 'lineno')
        print("[ Top 10 differences after garbage collection ]")
        for stat in top_stats[:10]:
            print(stat)

        tracemalloc.stop()
        log_memory_usage("After garbage collection")

        logger.info("eve_type数据写入Redis完成")
    return True"""