import json
from functools import wraps

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

