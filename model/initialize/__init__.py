import json
from pathlib import Path

from ...database.mysql import MysqlArray
from ...database.redis import RedisArray
from ...model.common import data_path
from ...model.config import plugin_config
from ...utils.common import check_files_exist, download_sde
from ..sde import load_sde_to_mysql

from nonebot import logger


async def create_db(MYSQL: MysqlArray, db: str):
    logger.info("开始创建数据库eve_tool")
    await MYSQL.create_database()
    await MYSQL.create_pool()
    eve_type_sql = """
            CREATE TABLE eve_type (
                id                   INT          NOT NULL COMMENT '物品ID'
                    PRIMARY KEY,
                name                 VARCHAR(200) NULL COMMENT '物品名称',
                name_en              VARCHAR(200) NULL COMMENT '物品名称英文',
                description          LONGTEXT     NULL COMMENT '物品描述',
                description_en       LONGTEXT     NULL COMMENT '物品描述英文',
                group_id             INT          NULL COMMENT '分组ID',
                group_name           VARCHAR(200) NULL COMMENT '分组名称',
                group_name_en        VARCHAR(200) NULL COMMENT '分组名称英文',
                meta_group_id        INT          NULL COMMENT '元分组ID',
                meta_group_name      VARCHAR(200) NULL COMMENT '元分组名称',
                meta_group_name_en   VARCHAR(200) NULL COMMENT '元分组名称英文',
                market_group_id      INT          NULL COMMENT '市场分组ID',
                market_group_name    VARCHAR(200) NULL COMMENT '市场分组名称',
                market_group_name_en VARCHAR(200) NULL COMMENT '市场分组名称英文',
                category_id          INT          NULL COMMENT '分类ID',
                category_name        VARCHAR(200) NULL COMMENT '分类名称',
                category_name_en     VARCHAR(200) NULL COMMENT '分类名称中文',
                create_time          TIMESTAMP    NULL
            )
            """
    await MYSQL.execute(eve_type_sql)
    await MYSQL.execute("CREATE INDEX idx_group_id ON eve_type (group_id)")
    await MYSQL.execute("CREATE INDEX idx_market_group_id ON eve_type (market_group_id)")

    listener_sql = """
    create table listener
(
    id                 int auto_increment
        primary key,
    type               enum ('char', 'corp', 'alliance', 'high') not null,
    entity_id          varchar(255)   default '0'                not null,
    push_type          enum ('group', 'friend')                  not null,
    push_to            varchar(255)                              not null,
    attack_value_limit decimal(14, 2) default 15000000.00        not null,
    victim_value_limit decimal(14, 2) default 30000000.00        not null,
    title              varchar(255)                              not null
)"""
    high_listener_sql = """
    CREATE TABLE high_listener (
    id INT PRIMARY KEY AUTO_INCREMENT,
    high_value_limit DECIMAL(14,2) DEFAULT 20000000000.00,
    push_type VARCHAR(255) NOT NULL,
    push_to VARCHAR(255) NOT NULL
)"""
    await MYSQL.execute(listener_sql)
    await MYSQL.execute(high_listener_sql)

    if check_eve_sde_path(plugin_config.eve_sde_path):
        await load_sde_to_mysql(MYSQL, plugin_config.eve_sde_path)

    return True


async def init_data(RA: RedisArray, MYSQL: MysqlArray) -> bool:
    """
    初始化数据到Redis
    """
    eve_type_data = await MYSQL.fetchall("SELECT id, name, name_en FROM eve_type WHERE market_group_id IS NOT NULL")
    await RA.execute('FLUSHDB')
    await RA.execute('FT.CREATE', 'eveTypeIdx', 'ON', 'HASH', 'PREFIX', '1', 'eve_type:',
                     'SCHEMA', 'name', 'TEXT', 'name_en', 'TEXT')

    for row in eve_type_data:
        redis_key = row['id']
        redis_value = {
            'name': row['name'],
            'name_en': row['name_en']
        }
        redis_value = json.dumps(redis_value)
        await RA.hset('eveTypeIdx', redis_key, redis_value)
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

