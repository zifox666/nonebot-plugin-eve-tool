from pathlib import Path

from ...model.common import data_path
from ...database.mysql import MysqlArray
from ...database.redis import RedisArray
from ...model.config import plugin_config

from ..sde import load_sde_to_mysql
from .sde import load_sde_to_redis, check_eve_sde_path
from .sql import Sql
from .sub import load_listener_to_redis
from .market import load_alias_to_redis, load_price_list_to_redis

from nonebot import logger


async def create_db(MYSQL: MysqlArray):
    """
    初始化数据库
    """
    logger.info("开始创建数据库eve_tool")
    await MYSQL.create_database()
    await MYSQL.create_pool()

    await MYSQL.execute(Sql.eve_type_sql)
    await MYSQL.execute(Sql.group_index)
    await MYSQL.execute(Sql.market_group_index)

    await MYSQL.execute(Sql.listener_sql)
    await MYSQL.execute(Sql.high_listener_sql)

    await MYSQL.execute(Sql.alias_items)

    await MYSQL.execute(Sql.set_limit_time)

    if await check_eve_sde_path(plugin_config.eve_sde_path):
        await load_sde_to_mysql(MYSQL, plugin_config.eve_sde_path)

    return True


async def init_data(RA: RedisArray, MYSQL: MysqlArray) -> bool:
    """
    初始化数据到Redis
    """
    Path(data_path / 'KillMailHtml').mkdir(parents=True, exist_ok=True)
    await load_sde_to_redis(RA, MYSQL)
    await load_listener_to_redis(RA, MYSQL)
    await load_alias_to_redis(RA, MYSQL)
    if plugin_config.eve_market_preference == 'esi_cache':
        await load_price_list_to_redis()
    return True




