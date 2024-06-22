from ..api import get_names_id, get_id_name
from ..database.mysql.search import search_eve_types_for_mysql


async def get_trans(args: str, num: int, lagrange: str) -> str:
    msg = ""
    name_id = None
    name_data = await get_names_id(args, lagrange)
    if name_data:
        if 'systems' in name_data:
            name_id = name_data['systems'][0]['id']
        elif 'constellations' in name_data:
            name_id = name_data['constellations'][0]['id']
        elif 'regions' in name_data:
            name_id = name_data['regions'][0]['id']

        if name_id:
            name = await get_id_name(name_id, lagrange='en' if lagrange == 'zh' else 'zh')
            msg = f"{name} <-> {args}"
            return msg

    data = await search_eve_types_for_mysql(
        args,
        lagrange,
    )
    if data:
        data_num = int(data["total"])
        if data_num == 0:
            return f"没有查询到[{args}]相关物品"
        data.pop("total", None)
        if data_num <= num:
            data = data
        else:
            msg += f"查询到的物品数量有{data_num}个，你可以进一步查询\n"
            keys = list(data.keys())[:num]
            data = {key: data[key] for key in keys}

        for key, value in data.items():
            name = value.get("name")
            name_en = value.get("name_en")
            msg += f"{name}: {name_en}\n"
        return msg
