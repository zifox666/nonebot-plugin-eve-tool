from nonebot.adapters.onebot.v11 import Bot, Event

import re

from ..api.esi import get_corp_id, get_character_id
from .dataProcess import remove_high_listener, insert_high_listener, insert_sub_listener, remove_listener


async def check_user_id(event):
    if event.sub_type == "normal":
        if event.sender.role == "member" and event.sender.user_id != 1442493508:
            return
        else:
            return "group"
    if event.sub_type == "friend":
        return "friend"


async def parse_subscription_command(command: str) -> dict | None:
    """
    解析订阅命令
    :param command: 输入的命令字符串
    :return: 解析后的命令参数字典
    """
    # 定义正则表达式模式来匹配命令
    pattern = rf"(add|remove) (--corp|--char) ([\S ]+?)(?: -a(\d+))?(?: -v(\d+))?$"

    # 使用正则表达式匹配命令
    match = re.match(pattern, command)
    if not match:
        return

    # 获取匹配的参数
    action = match.group(1)
    target_type = match.group(2)
    target_name = match.group(3)
    attacker_value_limit = match.group(4) or None
    victim_value_limit = match.group(5) or None

    # 构造命令参数字典
    command_params = {
        "action": action,
        "target_type": target_type,
        "target_name": target_name,
        "attacker_value_limit": attacker_value_limit,
        "victim_value_limit": victim_value_limit
    }
    print(command_params)

    return command_params


async def parse_high_value_kill_subscription_command(command: str) -> dict | None:
    """
    解析高价值击杀订阅命令
    :param command: 输入的命令字符串
    :return: 解析后的命令参数字典
    """
    # 定义正则表达式模式来匹配命令
    pattern = rf"(add|remove)(?:\s+(-l|--limit)(\S+))?"

    # 使用正则表达式匹配命令
    match = re.match(pattern, command)
    if not match:
        return

    # 获取匹配的参数
    action = match.group(1)
    limit_option = match.group(2) or None
    limit_value = match.group(3) or None

    # 构造命令参数字典
    command_params = {
        "action": action,
        "limit_option": limit_option,
        "limit_value": limit_value
    }

    return command_params


help_message = """
1. /km订阅 [add/remove] --corp/--char [name] -a[value] -v[value]
   - 用于订阅或取消订阅击杀邮件通知。
   - 参数说明：
     - [add/remove]: 添加或移除订阅。
     - --corp/--char [name]: 指定是订阅公司还是角色，name是公司或角色的名称。
     - -a [value]: 可选参数，指定订阅击杀km最低限值，默认15m
     - -v [value]: 可选参数，指定订阅损失km最低限值，默认30m
    例如 /km订阅 add --char BigfishOVO -a15000000 -v30000000

2. /高价值击杀订阅 [add/remove] [-l/--limit value]
   - 用于订阅或取消订阅高价值击杀通知。
   - 参数说明：
     - [add/remove]: 添加或移除订阅。
     - -l/--limit [value]: 可选参数，指定限制条件的值。
    例如：/高价值击杀订阅 add -l20000000000

"""


async def handle_high_value_sub(bot: Bot, event: Event):
    type_check = await check_user_id(event)
    _id = 0
    if type_check:
        if type_check == "group":
            _id = event.group_id
        if type_check == "friend":
            _id = event.user_id
    else:
        await bot.send(event, "只有群管理能更改KM订阅")
        return

    high_value_help = """
     /高价值击杀订阅 [add/remove] -l/--limit[value]
     - 用于订阅或取消订阅高价值击杀通知。
     - 更改通知门限请直接使用add参数
     - 参数说明：
     - [add/remove]: 添加或移除订阅。
     - -l/--limit [value]: 可选参数 默认18b，最低8b
     请把[]去掉，不要去掉-。把限价过低导致机器人恶意刷屏将会拉入黑名单
     例如：/高价值击杀订阅 add -l20000000000 是l不是1
     """
    args = " ".join(str(event.message).split(" ")[1:]).strip()
    if not args:
        await bot.send(event, high_value_help)
        return
    command_params = await parse_high_value_kill_subscription_command(args)
    if not command_params:
        await bot.send(event, f"解析参数失败，请确认参数\n{high_value_help}")
        return
    if command_params["action"] == "remove":
        await remove_high_listener(type_check, str(_id))
        await bot.send(event, f"高价值订阅已移除\n移除{type_check}[{_id}]")
    if command_params["action"] == "add":
        if command_params['limit_value']:
            if int(command_params['limit_value']) <= 8000000000:
                limit_value = 18000000000
            else:
                limit_value = command_params['limit_value']
        else:
            limit_value = 18000000000
        await insert_high_listener(type_check, str(_id), limit_value)
        limit_value = f"{int(limit_value):,.2f}"
        await bot.send(event, f"高价值订阅已增加\n订阅{type_check}[{_id}]\n限额: {limit_value} isk")


async def handle_sub_km(bot: Bot, event: Event):
    type_check = await check_user_id(event)
    _id = 0
    if type_check:
        if type_check == "group":
            _id = event.group_id
        if type_check == "friend":
            _id = event.user_id
    else:
        await bot.send(event, "只有群管理能更改KM订阅")
        return

    sub_km_help = """
    /击杀订阅 [add/remove] --corp/--char [name] -a[value] -v[value]
   - 用于订阅或取消订阅击杀邮件通知。
   - 参数说明：
     - [add/remove]: 添加或移除订阅。
     - --corp/--char [name]: 指定是订阅公司还是角色，name是公司或角色的名称。
     - -a [value]: 可选参数，指定订阅击杀km最低限值，默认15m，最低10m
     - -v [value]: 可选参数，指定订阅损失km最低限值，默认30m，最低10m
     - 恶意批量订阅会被拉入黑名单
    例如 
     - /击杀订阅 add --char RedHog -a15000000 -v30000000
     - /击杀订阅 remove --char RedHog
    """

    args = " ".join(str(event.message).split(" ")[1:]).strip()
    if not args:
        await bot.send(event, sub_km_help)
        return
    command_params = await parse_subscription_command(args)
    if not command_params:
        await bot.send(event, f"解析参数失败，请确认参数\n{sub_km_help}")
        return

    attacker_value_limit,  victim_value_limit = 15000000, 30000000
    sub_type = "corp"
    eve_id = ""
    if command_params["attacker_value_limit"]:
        attacker_value_limit = int(command_params["attacker_value_limit"])
    if command_params["victim_value_limit"]:
        victim_value_limit = int(command_params["victim_value_limit"])

    if attacker_value_limit < 10000000:
        attacker_value_limit = 50000000
    if victim_value_limit < 10000000:
        victim_value_limit = 50000000

    if command_params["target_type"] == "--corp":
        eve_id = await get_corp_id(command_params['target_name'])
        sub_type = "corp"
    elif command_params["target_type"] == "--char":
        sub_type = "char"
        eve_id = await get_character_id(command_params['target_name'])

    if not eve_id:
        await bot.send(event, f"未找到[{sub_type}]{command_params['target_name']}\n请确认名称后再试")
        return

    if command_params["action"] == "add":
        await insert_sub_listener(
            sub_type=sub_type,
            push_type=type_check,
            push_to=_id,
            entity_id=eve_id,
            attack_value_limit=attacker_value_limit,
            victim_value_limit=victim_value_limit,
            title=command_params['target_name']
        )

    else:
        await remove_listener(
            sub_type=sub_type,
            push_type=type_check,
            push_to=_id,
            entity_id=eve_id
        )

    await bot.send(
        event,
        f"订阅已{command_params['action']}\n[{sub_type}]{command_params['target_name']}\n"
        f"击杀限额：{attacker_value_limit:,.2f} isk\n损失限额：{victim_value_limit:,.2f} isk")
