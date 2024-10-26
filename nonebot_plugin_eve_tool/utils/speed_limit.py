from datetime import timedelta

from nonebot import logger

from ..database.redis.RedisArray import RedisArray
from ..model.config import plugin_config

EXPIRATION_TIME = timedelta(minutes=720)
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


async def save_url(redis_array, group_id, message_id, url):
    """
    将 URL 存储到 Redis 中，键格式为 sendId:{group_id}:{message_id}
    """
    key = f"sendId:{group_id}:{message_id}"
    try:
        await redis_array.hset(key, "url", url)
        logger.info(f"Saved URL: {url} with key: {key}")
    except Exception as e:
        logger.error(f"Failed to save URL: {url} with key: {key}, error: {e}")


async def get_url(redis_array, group_id, message_id):
    """
    从 Redis 中读取 URL，键格式为 sendId:{group_id}:{message_id}
    """
    key = f"sendId:{group_id}:{message_id}"
    try:
        url = await redis_array.hget(key, "url")
        if url:
            logger.info(f"Retrieved URL: {url} for key: {key}")
        else:
            logger.warning(f"No URL found for key: {key}")
        return url
    except Exception as e:
        logger.error(f"Failed to retrieve URL for key: {key}, error: {e}")
        return None
