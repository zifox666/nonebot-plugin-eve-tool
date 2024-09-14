import asyncio
import json
from functools import wraps

from httpx import TimeoutException
from nonebot import logger

from ...model.config import plugin_config
from .RedisArray import RedisArray


RA = RedisArray(plugin_config.eve_redis_url)


async def read_from_cache(name: str, params: str, cache_type: str) -> dict | None:
    key = f"{cache_type}:{name}:{params}"
    cached_data = await RA.hget(key, key)
    if cached_data:
        return json.loads(cached_data)
    else:
        return None


async def write_to_cache(name: str, params: str, data: dict, cache_type: str, expire_seconds: int = -1):
    key = f"{cache_type}:{name}:{params}"
    data = json.dumps(data)
    await RA.hset(key, key, data)
    if expire_seconds > 0:
        await RA.expire(key, expire_seconds)


def cache_async(cache_expiry_seconds=-1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            args_str = '_'.join(map(str, args)).replace(' ', '_')
            kwargs_str = '_'.join(f'{key}={value}'.replace(' ', '_') for key, value in kwargs.items())
            cache_key = f"{func.__name__}_{args_str}_{kwargs_str}"

            cached_data = await read_from_cache(func.__name__, cache_key, 'api')
            if cached_data is not None:
                return cached_data

            result = await func(*args, **kwargs)

            await write_to_cache(func.__name__, cache_key, result, 'api', cache_expiry_seconds)

            return result

        return wrapper

    return decorator


def retry_on_timeout_async(retries=3, delay=1, exceptions=(TimeoutException,)):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < retries:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    if attempt == retries:
                        raise
                    logger.debug(f"第 {attempt} 次尝试失败: {e}，等待 {delay} 秒后重试...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
