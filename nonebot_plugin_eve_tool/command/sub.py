import re

from nonebot import on_notice, logger, on_command, on_request
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
from ..utils.rules import group_increase_notice, group_decrease_notice

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna, Query, CommandResult
from arclet.alconna import Alconna, Args, Option, CommandMeta, OptionResult, MultiVar, Subcommand, Arparma

# 为什么不用alconna？ 因为我对regex爱的深沉
# 他就是解析不成功啊，呜呜呜
sub_km = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "km订阅",
        Subcommand(
            "add",
            Option("--char", Args["name", MultiVar(str)]),
            Option("--corp", Args["name", MultiVar(str)]),
            Option("-a|--attack", Args["value", int, 15_000_000]),
            Option("-v|--victim", Args["value", int, 30_000_000]),
            default=OptionResult(args={"attack": 15_000_000,
                                       "victim": 30_000_000})
        ),
        Subcommand(
            "remove",
            Option("--char", Args["name", MultiVar(str)]),
            Option("--corp", Args["name", MultiVar(str)]),
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
            help_text="订阅的价格",
            compact=True
        ),
        Option(
            "remove",
            help_text="移除订阅"
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


@sub_km.assign("add.char")
async def _add_sub_char(
        event: Event,
        result: Arparma,
        attacker_value_limit: Query[int] = Query[int]("subcommands.add.attack.args.value", 15_000_000),
        victim_value_limit: Query[int] = Query[int]("subcommands.add.victim.args.value", 30_000_000),

):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")
    name = " ".join(result.query[MultiVar(str)]("subcommands.add.char.args.name"))
    tips1, tips2 = "", ""
    attacker_value, victim_value = attacker_value_limit.result, victim_value_limit.result
    if attacker_value < 10000000:
        attacker_value = 50000000
        tips1 = "\n击毁最低限度为10m"
    if victim_value < 10000000:
        victim_value = 50000000
        tips2 = "\n损失最低限度为10m"
    eve_id = await get_character_id(name)
    if not eve_id:
        await sub_km.finish(f"未找到[char]{name}\n请确认名称后再试")

    await remove_listener(
        sub_type='char',
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id
    )
    await insert_sub_listener(
        sub_type='char',
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id,
        attack_value_limit=attacker_value,
        victim_value_limit=victim_value,
        title=name
    )
    await sub_km.finish(
        f"订阅已增加\n{'Group' if check['type'] != 'friend' else 'Friend'}[{check['gid']}]\n[Char]{name}\n"
        f"击毁:{attacker_value:,.2f}\n损失:{victim_value:,.2f}{tips1}{tips2}")


@sub_km.assign("add.corp")
async def _add_sub_corp(
        event: Event,
        result: Arparma,
        attacker_value_limit: Query[int] = Query[int]("subcommands.add.attack.args.value", 15_000_000),
        victim_value_limit: Query = Query[int]("subcommands.add.victim.args.value", 30_000_000),

):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")
    name = " ".join(result.query[MultiVar(str)]("subcommands.add.corp.args.name"))
    tips1, tips2 = "", ""
    attacker_value, victim_value = attacker_value_limit.result, victim_value_limit.result
    if attacker_value_limit.result < 10000000:
        attacker_value = 50000000
        tips1 = "\n击毁最低限度为10m"
    if victim_value_limit.result < 10000000:
        victim_value = 50000000
        tips2 = "\n损失最低限度为10m"
    eve_id = await get_corp_id(name)
    if not eve_id:
        await sub_km.finish(f"未找到[corp]{name}\n请确认名称后再试")

    await remove_listener(
        sub_type='corp',
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id
    )
    await insert_sub_listener(
        sub_type='corp',
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id,
        attack_value_limit=attacker_value,
        victim_value_limit=victim_value,
        title=name
    )
    await sub_km.finish(
        f"订阅已增加\n{'Group' if check['type'] != 'friend' else 'Friend'}[{check['gid']}]\n[Corp]{name}\n"
        f"击毁:{attacker_value:,.2f}\n损失:{victim_value:,.2f}{tips1}{tips2}")


@sub_km.assign("remove.char")
async def _(
        event: Event,
        result: Arparma
):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")
    name = " ".join(result.query[MultiVar(str)]("subcommands.remove.char.args.name"))
    eve_id = await get_character_id(name)
    if not eve_id:
        await sub_km.finish(f"未找到[char]{name}\n请确认名称后再试")

    await remove_listener(
        sub_type='char',
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id
    )
    await sub_km.finish(
        f"订阅已删除\n{'Group' if check['type'] != 'friend' else 'Friend'}[{check['gid']}]\n[Char]{name}")


@sub_km.assign("remove.corp")
async def _(
        event: Event,
        result: Arparma
):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")
    name = " ".join(result.query[MultiVar(str)]("subcommands.remove.corp.args.name"))
    eve_id = await get_corp_id(name)
    if not eve_id:
        await sub_km.finish(f"未找到[corp]{name}\n请确认名称后再试")

    await remove_listener(
        sub_type='corp',
        push_type='group' if check['type'] != "friend" else 'friend',
        push_to=check['gid'],
        entity_id=eve_id
    )
    await sub_km.finish(
        f"订阅已删除\n{'Group' if check['type'] != 'friend' else 'Friend'}[{check['gid']}]\n[Corp]{name}")


@high_value_sub.assign("add")
async def add_high_value_sub(
        event: Event,
        value: Query[int] = Query[int]("options.add.args.value", 18_000_000_000)
):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")
    tips = ""
    if value:
        if value.result <= 7_999_999_999:
            limit_value = 18000000000
            tips = "最低限度8b"
        else:
            limit_value = value.result
    else:
        limit_value = 18000000000

    await insert_high_listener('group' if check['type'] != "friend" else 'friend', check['gid'], limit_value)
    limit_value = f"{int(limit_value):,.2f}"
    await high_value_sub.finish(
        f"高价值订阅已增加\n订阅{'Group' if check['type'] != 'friend' else 'Friend'}[{check['gid']}]\n限额: {limit_value} isk\n{tips}")


@high_value_sub.assign("remove")
async def del_high_value_sub(
        event: Event
):
    check = await check_id(event)
    if check['type'] == "group_member":
        await high_value_sub.finish(f"只有群管理能更改监听")
    await remove_high_listener('group' if check['type'] != "friend" else 'friend', check['gid'])
    await high_value_sub.finish(f"高价值订阅已删除\n{'Group' if check['type'] != 'friend' else 'Friend'}[{check['gid']}]")


group_increase_notice = on_request(group_increase_notice)
group_decrease_notice = on_request(group_decrease_notice)


@group_increase_notice.handle()
async def group_innotice(bot: Bot, event: GroupIncreaseNoticeEvent):
    user_id, group_id = await get_group_info(event, bot)
    if not user_id:
        return
    await insert_high_listener('group', str(group_id), 18000000000)
    await bot.send_group_msg(group_id=group_id,
                             message=f'欢迎使用eve bot插件，已经自动增加高价值击杀订阅，请输入/help查询机器人详细命令\n本机器人支持订阅角色/军团km')


@group_decrease_notice.handle()
async def group_denotice(bot: Bot, event: GroupDecreaseNoticeEvent):
    user_id, group_id = await get_group_info(event, bot)
    if not user_id:
        return
    await remove_high_listener('group', str(group_id))
    await remove_all_listener('group', str(group_id))


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

