import gc
from pathlib import Path

from nonebot import logger

from ..utils.common import load_yaml
from ..database.mysql import MysqlArray


async def transform_data(eve_type_data, meta_groups, market_groups, groups,categories):
    transformed_data = []
    for item_id, item_data in eve_type_data.items():
        group_id = item_data.get('groupID', None)
        market_group_id = item_data.get('marketGroupID', None)
        meta_group_id = item_data.get('metaGroupID', None)
        category_id = groups.get(group_id, {}).get('categoryID', None)

        data = (
            item_id,
            item_data['name'].get('zh', None),
            item_data['name'].get('en', None),
            item_data.get('description', {}).get('zh', None),
            item_data.get('description', {}).get('en', None),
            group_id if group_id else None,
            groups.get(group_id, {}).get('nameID', {}).get('zh', None),
            groups.get(group_id, {}).get('nameID', {}).get('en', None),
            meta_group_id if meta_group_id else None,
            meta_groups.get(meta_group_id, {}).get('nameID', {}).get('zh', None),
            meta_groups.get(meta_group_id, {}).get('nameID', {}).get('en', None),
            market_group_id if market_group_id else None,
            market_groups.get(market_group_id, {}).get('nameID', {}).get('zh', None),
            market_groups.get(market_group_id, {}).get('nameID', {}).get('en', None),
            category_id,
            categories.get(category_id, {}).get('name', {}).get('zh', None),
            categories.get(category_id, {}).get('name', {}).get('en', None)
        )

        transformed_data.append(data)
    return transformed_data


async def load_sde_to_mysql(MYSQL: MysqlArray, sde_path: Path):
    fsd_path: Path = sde_path / 'fsd'
    logger.info("开始加载SDE数据，耗时较长，请耐心等待，预计五分钟")
    eve_type_data = await load_yaml(f'{fsd_path}/types.yaml')
    logger.info('types loaded!')
    meta_groups = await load_yaml(f'{fsd_path}/metaGroups.yaml')
    logger.info('meta groups loaded!')
    market_groups = await load_yaml(f'{fsd_path}/marketGroups.yaml')
    logger.info('market groups loaded!')
    groups = await load_yaml(f'{fsd_path}/groups.yaml')
    logger.info('groups loaded!')
    categories = await load_yaml(f'{fsd_path}/categories.yaml')
    logger.info('categories loaded!')

    transformed_data = await transform_data(eve_type_data, meta_groups, market_groups, groups, categories)

    insert_query = """
        INSERT INTO eve_type (
            id, name, name_en, description, description_en, group_id, group_name, group_name_en, meta_group_id, meta_group_name, meta_group_name_en, market_group_id, market_group_name, market_group_name_en, category_id, category_name, category_name_en, create_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
        """

    await MYSQL.execute("TRUNCATE TABLE eve_type")
    logger.info('数据库清理完成')

    await MYSQL.executemany(insert_query, transformed_data)
    logger.success("SDE已写入数据库")

    del eve_type_data
    del meta_groups
    del market_groups
    del groups
    del categories
    del transformed_data
    gc.collect()
    return



