from datetime import timedelta

from nonebot import logger

from ..database.redis.RedisArray import RedisArray
from ..model.config import plugin_config

EXPIRATION_TIME = timedelta(minutes=30)
RA = RedisArray(plugin_config.eve_redis_url)


async def add_kill_id_to_group(group_id, kill_id):
    group_key = f"group:{group_id}"

    is_member = await RA.sismember(group_key, kill_id)

    if is_member:
        logger.debug(f"限速器存在{kill_id}:{group_id}")
        return True
    else:
        await RA.sadd(group_key, kill_id)
        await RA.expire(group_key, EXPIRATION_TIME)
        logger.debug(f"限速器增加{kill_id}:{group_id}")
        return False


async def speed_limit(kill_id: int, group_id: int) -> bool:
    exists = await add_kill_id_to_group(group_id, kill_id)
    if exists:
        return True
    else:
        return False
