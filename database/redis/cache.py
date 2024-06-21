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
            # 构建缓存的key，这里示例中使用函数名 + 参数作为key
            cache_key = func.__name__ + '_' + '_'.join(map(str, args)) + '_' + '_'.join(f'{key}={value}' for key, value in kwargs.items())

            # 尝试从缓存中读取数据
            cached_data = await read_from_cache(func.__name__, cache_key, 'api')
            if cached_data:
                return cached_data

            # 缓存中没有数据，调用实际的函数获取数据
            result = await func(*args, **kwargs)

            # 将结果写入缓存
            await write_to_cache(func.__name__, cache_key, result, 'api', cache_expiry_seconds)

            return result

        return wrapper

    return decorator

