import json

from .RedisArray import RedisArray
from ...model.config import plugin_config
from ...utils.common import pack_strings

RA = RedisArray(plugin_config.eve_redis_url)


async def get_names_for_redis(ids: int | str) -> str | list[str]:
    """
    批量通过id获取名称
    :param ids:
    :return:
    """
    names_list = []
    if isinstance(ids, int):
        ids = [ids]
    for _id in ids:
        name = await RA.hget(f'eve_type:{_id}',
                             'name' if plugin_config.eve_lagrange_preference == 'zh' else 'name_en')
        names_list.append(pack_strings(name))
    print(names_list)
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
        print(f"查询到物品别名:\n{data}")
        return data


async def search_eve_types(query_list, lang='zh', fuzzy: bool = True):
    """
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
        search_query = f'@name:{" ".join(query)}' if lang == 'zh' else f'@name_en:{query}'

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
