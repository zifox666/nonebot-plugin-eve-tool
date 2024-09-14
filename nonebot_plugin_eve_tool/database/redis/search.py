import json

from nonebot import logger

from .RedisArray import RedisArray
from ...model.config import plugin_config

RA = RedisArray(plugin_config.eve_redis_url)


async def get_names_for_redis(ids: int | str | list) -> str | list[str]:
    """
    批量通过id获取名称
    :param ids:
    :return:
    """
    names_list = []
    if isinstance(ids, str | int):
        ids = [ids]
    for _id in ids:
        name = await RA.hget(f'eve_type:{_id}',
                             'name' if plugin_config.eve_lagrange_preference == 'zh' else 'name_en')
        names_list.append(name)
    return names_list[0] if len(names_list) == 1 else names_list


async def get_alias_for_redis(alias: str) -> list | None:
    """
    批量获取alias组
    :param alias:
    :return:
    """
    data = await RA.lrange(
        'alias',
        alias
    )
    if not data:
        return None
    else:
        logger.info(f"查询到物品别名:\n{data}")
        return data


async def search_eve_types_for_redis(query_list, lang='zh', fuzzy: bool = True):
    """
    !!!废弃!!!
    在 Redis 中根据指定语言进行模糊搜索
    :param query_list: 查询字符串或字符串列表
    :param lang: 语言类型 ('zh' 表示中文, 'en' 表示英文)
    :param fuzzy: 是否模糊搜索
    :return: 搜索结果列表
    """
    if isinstance(query_list, str):
        query_list = [query_list]

    combined_results = []
    total_count = 0

    for query in query_list:
        search_query = f'@name:{query}' if lang == 'zh' else f'@name_en:{query}*'

        result = await RA.execute('FT.SEARCH', 'eveTypeIdx', search_query, 'RETURN', '2', 'name',
                                  'name_en', 'LIMIT', '0', '50')

        count, ids = await extract_ids_from_results(result)
        total_count += count
        combined_results.extend(ids)

    return total_count, combined_results


async def extract_ids_from_results(results):
    items_list = []
    for i in range(1, len(results), 2):
        eve_type_id = int(results[i].split(':')[1])
        items_list.append(eve_type_id)
    items_list.sort()
    return results[0], items_list


async def get_price_from_cache(ids: list[int]) -> dict:
    result = {}
    for _id in ids:
        try:
            key = f"market_price:{_id}"
            result[str(_id)] = json.loads(await RA.hget(key, key))
            if not result[str(_id)]["name"]:
                result[str(_id)]["name"] = await get_names_for_redis(str(_id))
        except Exception as e:
            logger.error(e)
            result[str(_id)] = {
                "sell": 0,
                "sell_num": 0,
                "buy": 0,
                "buy_num": 0,
                "name": "None"
            }
    if result:
        return result


