import aioredis
from nonebot import logger

from aioredis import Redis


class RedisArray:
    def __init__(self, url):
        """
        :param url: redis url
        """
        self.aioClient: Redis
        self.url: str = url

    async def create_pool(self):
        """
        创建连接池
        """
        self.aioClient = await aioredis.from_url(self.url, decode_responses=True)

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

    async def hgetall(self, hash_name):
        """
        获取整个哈希
        :param hash_name: 哈希名称
        """
        try:
            result = await self.aioClient.hgetall(hash_name)
            logger.error(result)
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
            print(f"Error executing command {command} with args {args}: {e}")
            return None

    async def close(self):
        """
        关闭redis连接
        """
        await self.aioClient.close()
