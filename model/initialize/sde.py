from pathlib import Path

from ...database.mysql.MysqlArray import MysqlArray
from ...database.redis.RedisArray import RedisArray
from ...utils.common import check_files_exist, download_sde

import json
from nonebot import logger


async def load_sde_to_redis(RA: RedisArray, MYSQL: MysqlArray) -> bool:
    """
    从Mysql读取SDE存放到Redis方便查询
    初始化操作
    """
    eve_type_data = await MYSQL.fetchall("SELECT id, name, name_en FROM eve_type WHERE market_group_id IS NOT NULL")
    await RA.execute('FLUSHDB')

    for row in eve_type_data:
        redis_key = f"eve_type:{row['id']}"
        if row['name']:
            await RA.hset(redis_key, 'name', row['name'])
        if row['name_en']:
            await RA.hset(redis_key, 'name_en', row['name_en'])

    await RA.execute('FT.CREATE', 'eveTypeIdx', 'ON', 'HASH', 'PREFIX', '1', 'eve_type:',
                     'SCHEMA', 'name', 'TEXT', 'name_en', 'TEXT')

    logger.info("eve_type数据写入Redis完成")
    return True


def check_eve_sde_path(sde_path: Path) -> bool | str:
    """
    判断SDE文件
    """
    files = ["types.yaml", "marketGroups.yaml", "metaGroups.yaml", "groups.yaml", "categories.yaml"]
    if check_files_exist((sde_path / 'fsd'), files):
        logger.info('SDE文件已导入')
    else:
        logger.info('SDE文件不存在，开始下载')
        Path(sde_path).mkdir(parents=True, exist_ok=True)
        if download_sde(sde_path):
            logger.success("SDE数据下载完成，开始解压")
            return True
        else:
            raise FileNotFoundError(f'SDE自动下载失败，请手动放置SDE文件到{sde_path}下')

