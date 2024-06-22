import re

from nonebot import on_notice, logger, on_command
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import GroupIncreaseNoticeEvent, GroupDecreaseNoticeEvent

from ..api import get_character_id, get_corp_id, get_esi_kill_mail
from ..utils import get_group_info, check_id
from ..model import plugin_config

from nonebot import require

from ..utils.dataProcess import insert_high_listener, remove_high_listener, remove_all_listener, insert_sub_listener, \
    remove_listener
from ..utils.killmail_handle import kill_mail_handle
from ..utils.shit import message_handler
from ..utils.sub import handle_high_value_sub, handle_sub_km

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna
from arclet.alconna import Alconna, Args, Option, CommandMeta, OptionResult, MultiVar, Subcommand, Arparma


# 为什么不用alconna？ 因为我对regex爱的深沉
# 他就是解析不成功啊，呜呜呜
"""sub_km = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "km订阅",
        Subcommand(
            "add",
            Args["type", str]["args", MultiVar(str)],
            Option("-a|--attack", Args["attack", int, 15_000_000], compact=True),
            Option("-v|--victim", Args["victim", int, 30_000_000], compact=True),
            default=OptionResult(args={"attack": 15_000_000,
                                       "victim": 30_000_000})
        ),
        Subcommand(
            "remove",
            Args["type", str]["args", MultiVar(str)]
        ),
        meta=CommandMeta(
            "订阅指定KM",
            usage="订阅宇宙中发生指定的击杀，支持军团缩写",
            example="/km订阅 add|remove char|corp [name] --attack|-a [15000000] --victim|-v [30000000]\n用的时候把[]去掉",
            compact=True,
            raise_exception=True
        )
    ),
    aliases=("击杀订阅", "KM订阅"),
    auto_send_output=True
)
high_value_sub = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "高价值订阅",
        Option(
            "add",
            Args["value", int, 18_000_000_000],
            help_text="增加的价格",
            default=OptionResult(args={"value": 18_000_000_000})
        ),
        Option(
            "remove",
            Args["value", int, 0],
            help_text="移除订阅",
            default=OptionResult(args={"value": 0})
        ),
        meta=CommandMeta(
            "高价值击杀订阅",
            usage="订阅宇宙中发生的高价值击杀，默认18b",
            example="/高价值订阅",
            compact=True,
            raise_exception=True
        ),
    ),
    aliases=("高价值击杀订阅", "/高价值"),
    auto_send_output=True
)


@sub_km.handle()
async def _sub_km(result: Arparma, event: Event):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")

    if result.subcommands['add']:
        await add_sub_km(result, check)
    elif result.subcommands['remove']:
        await del_sub_km(result, check)


async def add_sub_km(result: Arparma, check):
    logger.error(result)

    sub_type = result.subcommands['add'].args['type']
    name = result.subcommands['add'].args['args']
    attacker_value_limit = result.subcommands['add'].args['attack']
    victim_value_limit = result.subcommands['add'].args['victim']

    if attacker_value_limit < 10000000:
        attacker_value_limit = 50000000
    if victim_value_limit < 10000000:
        victim_value_limit = 50000000

    if sub_type == "corp":
        eve_id = await get_corp_id(name)
    elif sub_type == "char":
        eve_id = await get_character_id(name)
    else:
        eve_id = None

    if not eve_id:
        await sub_km.finish(f"未找到[{sub_type}]{name}\n请确认名称后再试")

    await insert_sub_listener(
        sub_type=sub_type,
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id,
        attack_value_limit=attacker_value_limit,
        victim_value_limit=victim_value_limit,
        title=name
    )


@sub_km.assign('remove')
async def del_sub_km(result: Arparma, check):
    sub_type = result.subcommands['remove'].args['type']
    name = result.subcommands['remove'].args['args']

    if sub_type == "corp":
        eve_id = await get_corp_id(name)
    elif sub_type == "char":
        eve_id = await get_character_id(name)
    else:
        eve_id = None

    await remove_listener(
        sub_type=sub_type,
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id
    )


@high_value_sub.handle()
async def _high_value_sub(result: Arparma, event: Event):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")

    if result.options['add']:
        await add_high_value_sub(result, check)
    elif result.options['remove']:
        await del_high_value_sub(check)


async def add_high_value_sub(result: Arparma, check):
    if result.options['add'].args['value']:
        if int(result.options['add'].args['value']) <= 8000000000:
            limit_value = 18000000000
        else:
            limit_value = result.options['add'].args['value']
    else:
        limit_value = 18000000000

    await insert_high_listener('group' if check['type'] != "friend" else 'friend', check['gid'], limit_value)
    limit_value = f"{int(limit_value):,.2f}"
    await high_value_sub.finish(
        f"高价值订阅已增加\n订阅{'group' if check['type'] != 'friend' else 'friend'}[{check['gid']}]\n限额: {limit_value} isk")


async def del_high_value_sub(check):
    try:
        await remove_high_listener('group' if check['type'] != "friend" else 'friend', check['gid'])
    except Exception as e:
        logger.debug(e)
        await high_value_sub.finish(f"删除订阅出错\n{e}")"""


group_increase_notice = on_notice()
group_decrease_notice = on_notice()


@group_increase_notice.handle()
async def group_innotice(bot: Bot, event: GroupIncreaseNoticeEvent):
    user_id, group_id = await get_group_info(event)
    if not user_id:
        return
    await insert_high_listener('group', str(group_id), 18000000000)
    await bot.send_group_msg(group_id=group_id,
                             message=f'欢迎使用eve bot插件，已经自动增加高价值击杀订阅，默认18b，如需更多订阅，请输入/help查询机器人详细命令')


@group_decrease_notice.handle()
async def group_denotice(bot: Bot, event: GroupDecreaseNoticeEvent):
    user_id, group_id = await get_group_info(event)
    if not user_id:
        return
    await remove_high_listener('group', str(group_id))
    await remove_all_listener('group', str(group_id))


async def check_user_id(event):
    if event.sub_type == "normal":
        if event.sender.role == "member" and event.sender.user_id != 1442493508:
            return
        else:
            return "group"
    if event.sub_type == "friend":
        return "friend"


test_json = on_command("km_test_json")


@test_json.handle()
async def _(bot: Bot, event: Event):
    message = str(event.get_message())
    match = re.search(r"kill(\d+)", message)
    if match:
        kill_id = match.group(1)
        data = await get_esi_kill_mail(kill_id)
        if data:
            kill_mail_details = await kill_mail_handle(data)
            if kill_mail_details:
                echo = await message_handler(bot, kill_mail_details)


high_value_sub = on_command("高价值击杀订阅", aliases={"高价值订阅", "/高价值"})
sub_km = on_command("km订阅", aliases={"新增订阅", "订阅击杀", "KM订阅", "击杀订阅"})


@high_value_sub.handle()
async def _(bot: Bot, event: Event):
    await handle_high_value_sub(bot, event)


@sub_km.handle()
async def _(bot: Bot, event: Event):
    await handle_sub_km(bot, event)
