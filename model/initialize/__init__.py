from ...database.mysql import MysqlArray
from ...database.redis import RedisArray
from ...model.config import plugin_config

from ..sde import load_sde_to_mysql
from .sde import load_sde_to_redis, check_eve_sde_path
from .sql import Sql
from .sub import load_listener_to_redis

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

    if check_eve_sde_path(plugin_config.eve_sde_path):
        await load_sde_to_mysql(MYSQL, plugin_config.eve_sde_path)

    return True


async def init_data(RA: RedisArray, MYSQL: MysqlArray) -> bool:
    """
    初始化数据到Redis
    """
    await load_sde_to_redis(RA, MYSQL)
    await load_listener_to_redis(RA, MYSQL)
    return True




