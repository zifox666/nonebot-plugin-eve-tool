import json

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


@scheduler.scheduled_job('cron', minute='*/30', id='001')
async def refresh_price_cache():
    logger.info("定时任务：开始拉取市场列表")
    skip = False
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




