import gc
import json
import tracemalloc

from ..api.esi.market import fetch_all_price_pages
from ..database.redis.RedisArray import RedisArray
from ..model.config import plugin_config
from .dataProcess import process_all
from ..model.common import data_path

from nonebot import require, logger

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

RA = RedisArray(plugin_config.eve_redis_url)

file_path = data_path / "price_list.json"


"""def log_memory_usage(stage):
    process = psutil.Process(os.getpid())
    logger.debug(f"[{stage}] Current memory usage: {process.memory_info().rss / (1024 * 1024):.2f} MB")"""


async def init_market_job():
    scheduler.add_job(refresh_price_cache, 'cron', minute='*/30', id='refresh_price_cache')
    # await refresh_price_cache()


async def refresh_price_cache():
    logger.info("定时任务：开始拉取市场列表")
    skip = False
    data = None

    if file_path.exists():
        logger.info("市场初始化文件存在，使用市场初始化文件")
        skip = True
        with open(file_path, 'r') as file:
            data = file.read()
            data = json.loads(data)
    else:
        data = await fetch_all_price_pages()

    if data:
        if skip:
            datas = data
        else:
            datas = await process_all(data)
        for _id, _dict in datas.items():
            key = f"market_price:{_id}"
            await RA.hset(key, key, json.dumps(_dict))
        logger.success("市场列表更新完成")

        del data
        gc.collect()

        logger.info("eve_type数据写入Redis完成")
        return


@scheduler.scheduled_job('cron', minute='*/30', id='gc_job')
async def _gc():
    current, peak = tracemalloc.get_traced_memory()
    snapshot = tracemalloc.take_snapshot()
    # top_stats = snapshot.statistics('lineno')
    logger.debug(f"Current memory usage is {current / 10 ** 6}MB; Peak was {peak / 10 ** 6}MB")
    # gc.collect()
    # logger.debug(f"------gc-------\n{gc.get_stats()}")
    # logger.debug(f"------Top10-------\n")
    # for stat in top_stats[:10]:
    #     logger.debug(f"{stat}\n")

