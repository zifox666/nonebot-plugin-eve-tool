import json

import yaml
import asyncio
import aiomysql


async def load_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


async def transform_data(eve_type_data, meta_groups, market_groups, groups,categories):
    transformed_data = []
    for item_id, item_data in eve_type_data.items():
        group_id = item_data.get('groupID', None)
        market_group_id = item_data.get('marketGroupID', None)
        meta_group_id = item_data.get('metaGroupID', None)
        category_id = item_data.get('categoryID', None)

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
            category_id if category_id else None,
            categories.get(category_id, {}.get('name', {}).get('zh', None)),
            categories.get(category_id, {}.get('name', {}).get('en', None))
        )

        transformed_data.append(data)
    return transformed_data


async def save_to_txt(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(str(item) + '\n')


async def main():
    # 创建连接池
    pool = await aiomysql.create_pool(
        host='192.168.0.110',
        port=33061,
        user='root',
        password='Wy050427!',
        db='eve_corp_manager_cacx',
        charset='utf8mb4',
        autocommit=False,
        maxsize=10
    )

    eve_type_data = await load_yaml('types_full.yaml')
    print('types loaded')
    meta_groups = await load_yaml('metaGroups.yaml')
    print('meta groups loaded')
    market_groups = await load_yaml('marketGroups.yaml')
    print('market groups loaded')
    groups = await load_yaml('groups.yaml')
    print('groups loaded')
    categories = await load_yaml("categories.yaml")
    print('categories loaded')

    transformed_data = await transform_data(eve_type_data, meta_groups, market_groups, groups,categories)
    await save_to_txt(transformed_data, 'transformed_data.txt')

    insert_query = """
        INSERT INTO eve_type (
            id, name, name_en, description, description_en, group_id, group_name, group_name_en, meta_group_id, meta_group_name, meta_group_name_en, market_group_id, market_group_name, market_group_name_en, category_id, category_name, category_name_en, create_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
        """

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute("TRUNCATE TABLE eve_type")
            print('Table eve_type truncated')

            await cur.executemany(insert_query, transformed_data)
            await conn.commit()

    pool.close()
    await pool.wait_closed()


