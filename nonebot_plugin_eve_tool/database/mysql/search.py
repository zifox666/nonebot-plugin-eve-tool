import json
import re

from nonebot import logger

from .MysqlArray import MysqlArray, MYSQL
from ...utils import word_handle
from ..redis.cache import read_from_cache, write_to_cache


async def search_eve_types_for_mysql(
        type_name: str,
        lagrange: str = 'zh',
        market: bool = False,
        fuzzy: bool = True
) -> dict:
    """
    模糊查询中英文
    """
    result = {}
    cache_result = await read_from_cache('market' if market else 'trans', type_name, 'fuzzy_list')
    if cache_result:
        return cache_result
    market_sql = ""
    if market:
        market_sql = " AND market_group_id IS NOT NULL"

    if lagrange == "zh":
        sql = f"SELECT id, name, name_en FROM eve_type WHERE name REGEXP %s {market_sql}"
        regex = await word_handle.jieba_cut_word(type_name) if fuzzy else f".*(?=.*{type_name}).*"
    else:
        sql = f"SELECT id, name, name_en FROM eve_type WHERE name_en REGEXP %s {market_sql}"
        regex = '.*' + '.*'.join(f'(?=.*{re.escape(word)})' for word in type_name.split()) + '.*'

    logger.debug(f"SQL Query:{sql}")
    logger.debug(f"Regex Pattern:{regex}")
    info = await MYSQL.fetchall(sql, (regex,))
    logger.debug(info)

    count = 0
    for i in info:
        result[i["id"]] = {
            "name": i["name"],
            "name_en": i["name_en"]
        }
        count += 1

    result["total"] = len(info)

    if result:
        await write_to_cache(
            name='market' if market else 'trans',
            params=type_name,
            data=result,
            cache_type='fuzzy_list'
        )
        return result


async def get_ids_names_for_mysql(type_names: list, fuzzy_str: str, data_type="zh") -> dict:
    cache_result = await read_from_cache('types', fuzzy_str, 'fuzzy_list')
    if cache_result:
        return cache_result
    result = {}

    if data_type == "zh":
        placeholders = ', '.join(['%s'] * len(type_names))
        sql = f"SELECT id, name, name_en FROM eve_type WHERE name IN ({placeholders}) AND market_group_id IS NOT NULL"
    else:
        placeholders = ', '.join(['%s'] * len(type_names))
        sql = f"SELECT id, name, name_en FROM eve_type WHERE name_en IN ({placeholders}) AND market_group_id IS NOT NULL"

    info = await MYSQL.fetchall(sql, tuple(type_names))
    logger.debug(info)

    for i in info:
        result[i["id"]] = {
            "name": i["name"],
            "name_en": i["name_en"]
        }
    result["total"] = len(info)
    await write_to_cache(
        name='types',
        params=fuzzy_str,
        data=result,
        cache_type='fuzzy_list'
    )
    return result


async def query_eve_types(ids: list[int], lagrange: str = 'zh') -> list[dict]:
    if lagrange == 'zh':
        query = f"SELECT id, name, group_name FROM eve_type WHERE id IN ({','.join(['%s'] * len(ids))});"
    else:
        query = f"SELECT id, name_en, group_name_en FROM eve_type WHERE id IN ({','.join(['%s'] * len(ids))});"
    return await MYSQL.fetchall(query, ids)

