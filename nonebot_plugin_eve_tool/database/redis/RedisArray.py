from nonebot import logger
from redis import asyncio as aioredis
import redis
from nonebot import logger
from redis import Redis


class RedisArray:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.aioClient = None
            cls._instance.url = None
        return cls._instance

    def __init__(self, url):
        """
        :param url: redis url
        """
        self.aioClient: Redis
        if self.url is None:
            self.url = url

    async def create_pool(self):
        """
        创建连接池
        """
        self.aioClient = await aioredis.from_url(self.url, decode_responses=True)

    def get_client(self) -> Redis:
        if self.aioClient is None:
            raise RuntimeError("Redis client is not initialized. Call create_pool() first.")
        return self.aioClient

    async def lpush(self, list_name, value):
        """
        往列表左边, 也就是头部插入元素
        :param list_name: 列表名称
        :param value: element value
        """
        try:
            return await self.aioClient.lpush(list_name, value)
        except Exception as e:
            logger.error(f"lpush 插入: {list_name}/{value}报错: {str(e)}")
            return None

    async def rpush(self, list_name, value):
        """
        往列表右边, 也就是尾部插入元素
        :param list_name: 列表名称
        :param value: element value
        """
        try:
            return await self.aioClient.rpush(list_name, value)
        except Exception as e:
            logger.error(f"rpush 插入: {list_name}/{value}报错: {str(e)}")
            return None

    async def sismember(self, key, value):
        try:
            return await self.aioClient.sismember(key, value)
        except Exception as e:
            logger.error(f"查询: {key}/{value}报错: {str(e)}")
            return None

    async def hscan(
            self,
            name,
            cursor: int = 0,
            match=None,
            count: int = None):
        try:
            return await self.aioClient.hscan(name, cursor, match, count)
        except Exception as e:
            logger.error(f"读取: {name}报错: {str(e)}")
            return None

    async def get(self, list_name, start=0, end=-1):
        """
        获取元素
        :param list_name: 列表名称
        :param start: element start index
        :param end: element end index
        """
        try:
            result = await self.aioClient.lrange(list_name, start, end)
            logger.error(result)
            return result
        except Exception as e:
            logger.error(f"读取: {list_name}/{start}/{end}错误: {str(e)}")
            return []

    async def hset(self, hash_name, key, value):
        """
        设置哈希值
        :param hash_name: 哈希名称
        :param key: 哈希键
        :param value: 哈希值
        """
        try:
            return await self.aioClient.hset(hash_name, key, value)
        except Exception as e:
            logger.error(f"hset 插入: {hash_name}/{key}/{value}报错: {str(e)}")
            return None

    async def hget(self, hash_name, key):
        """
        获取哈希值
        :param hash_name: 哈希名称
        :param key: 哈希键
        """
        try:
            result = await self.aioClient.hget(hash_name, key)
            return result
        except Exception as e:
            logger.error(f"读取: {hash_name}/{key}错误: {str(e)}")
            return None

    async def hkeys(self, name):
        try:
            result = await self.aioClient.hkeys(name)
            return result
        except Exception as e:
            logger.error(f"读取: {name}错误: {str(e)}")
            return None

    async def hmget(self, hash_name, keys):
        """
        获取多个哈希值
        :param hash_name: 哈希名称
        :param keys: 哈希键列表
        """
        try:
            result = await self.aioClient.hmget(hash_name, *keys)
            return result
        except Exception as e:
            logger.error(f"读取多个哈希值: {hash_name}/{keys}错误: {str(e)}")
            return None

    async def hgetall(self, hash_name):
        """
        获取整个哈希
        :param hash_name: 哈希名称
        """
        try:
            result = await self.aioClient.hgetall(hash_name)
            return result
        except Exception as e:
            logger.error(f"读取: {hash_name}错误: {str(e)}")
            return None

    async def execute(self, command, *args):
        """
        执行Redis命令
        :param command: Redis命令
        :param args: 命令参数
        """
        try:
            return await self.aioClient.execute_command(command, *args)
        except Exception as e:
            logger.error(f"Error executing command {command} with args {args}: {e}")
            return None

    async def hdel(self, hash_name, key):
        try:
            if not key:
                keys = await self.aioClient.hkeys(hash_name)
                for key in keys:
                    await self.aioClient.hdel(hash_name, key)
                return
            else:
                await self.aioClient.hdel(hash_name, key)
                return

        except Exception as e:
            logger.error(f"Error hdel command {hash_name} with args {keys}: {e}")
            return None

    async def lrange(self, keyname, key, start=0, end=-1):
        try:
            key = f"{keyname}:{key}"
            items = await self.aioClient.lrange(key, start, end)
            return items
        except Exception as e:
            logger.error(f"读取{key}错误: {e}")
            return None

    async def expire(self, key, seconds):
        """
        设置键的过期时间
        """
        try:
            return await self.aioClient.expire(key, seconds)
        except Exception as e:
            logger.error(f"expire_key 设置过期时间: {key}/{seconds}报错: {str(e)}")
            return None

    async def close(self):
        """
        关闭redis连接
        """
        await self.aioClient.close()

    async def sadd(self, name, values):
        try:
            return await self.aioClient.sadd(name, values)
        except Exception as e:
            logger.error(f"{name}/{values}报错: {str(e)}")
            return None

    async def scan(self, cursor, match, count):
        try:
            return await self.aioClient.scan(
                cursor=cursor,
                match=match,
                count=count
            )
        except Exception as e:
            logger.error(f"报错: {str(e)}")
            return None

    async def delete(self, *param):
        try:
            return await self.aioClient.delete(
                *param
            )
        except Exception as e:
            logger.error(f"报错: {str(e)}")
            return None


    async def keys(self, pattern="*", **kwargs):
        try:
            return await self.aioClient.keys(pattern, **kwargs)
        except Exception as e:
            logger.error(f"报错: {str(e)}")
            return None
