import aiomysql
from aiomysql import Pool
from pydantic import BaseModel
from nonebot import logger

from ...model.config import plugin_config


class MysqlArray:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.aioClient = None
            cls._instance.host = None
        return cls._instance

    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            password: str,
            database: str
    ):
        """
        :param host: MySQL 主机地址
        :param port: MySQL 端口
        :param user: MySQL 用户名
        :param password: MySQL 密码
        :param database: MySQL 数据库名
        """
        if self.host is None:
            self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.database: str = database
        self.aioClient: Pool

    def get_client(self) -> Pool:
        if self.aioClient is None:
            raise RuntimeError("Mysql client is not initialized. Call create_pool() first.")
        return self.aioClient

    async def create_pool(self):
        """
        创建连接池
        """
        try:
            self.aioClient = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                charset='utf8mb4',
                autocommit=False
            )
            return "成功连接数据库"
        except Exception as e:
            logger.error(e)
            return False

    async def create_database(self):
        """
        创建数据库
        """
        conn = await aiomysql.connect(host=self.host, port=self.port, user=self.user, password=self.password)
        async with conn.cursor() as cursor:
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            await conn.commit()
            logger.success(f"数据库{self.database}已经成功创建")
            return True

    async def close(self):
        """
        关闭MySQL连接
        """
        if self.aioClient:
            self.aioClient.close()
            await self.aioClient.wait_closed()

    async def execute(self, query: str, args: tuple = ()):
        """
        执行单个查询
        :param query: SQL 查询
        :param args: 查询参数
        """
        async with self.aioClient.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                await conn.commit()

    async def executemany(self, query: str, args_list: list):
        """
        批量执行查询
        :param query: SQL 查询
        :param args_list: 查询参数列表
        """
        async with self.aioClient.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.executemany(query, args_list)
                await conn.commit()

    async def fetchall(self, query: str, args: tuple = ()):
        """
        执行查询并获取所有结果
        :param query: SQL 查询
        :param args: 查询参数
        """
        async with self.aioClient.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, args)
                return await cur.fetchall()

    async def fetchone(self, query: str, args: tuple = ()):
        """
        执行查询并获取单个结果
        :param query: SQL 查询
        :param args: 查询参数
        """
        async with self.aioClient.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, args)
                result = await cur.fetchone()
                return result

    async def insert_many(self, table: str, data: list):
        """
        批量插入数据
        :param table: 表名
        :param data: 要插入的数据列表，每项为一个字典
        """
        if not data:
            return

        keys = data[0].keys()
        columns = ", ".join(keys)
        placeholders = ", ".join(["%s"] * len(keys))
        values = [tuple(item[key] for key in keys) for item in data]

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        await self.executemany(query, values)

    async def delete_many(self, table: str, condition: str, args: list):
        """
        批量删除数据
        :param table: 表名
        :param condition: 条件语句 (WHERE 后面的部分)
        :param args: 条件参数列表
        """
        query = f"DELETE FROM {table} WHERE {condition}"
        await self.executemany(query, args)

    async def commit(self):
        """
        提交当前事务
        """
        async with self.aioClient.acquire() as conn:
            await conn.commit()

    async def rollback(self):
        """
        回滚当前事务
        """
        async with self.aioClient.acquire() as conn:
            await conn.rollback()


MYSQL = MysqlArray(
    host=plugin_config.eve_mysql_host,
    port=plugin_config.eve_mysql_port,
    user=plugin_config.eve_mysql_user,
    password=plugin_config.eve_mysql_password,
    database=plugin_config.eve_mysql_db
)
