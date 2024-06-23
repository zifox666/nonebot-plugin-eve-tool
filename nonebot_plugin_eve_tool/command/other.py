from datetime import datetime

import nonebot
import pytz
from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event

from ..utils import check_id
from ..model import plugin_config
from ..api import get_exchange_rate

from nonebot import require

from ..utils.mission import refresh_price_cache

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import (
    on_alconna
)
from arclet.alconna import Alconna, Args, CommandMeta

config = nonebot.get_driver().config

eve_time = on_command("evetime", aliases={"eve时间"}, priority=5)
feed_back = on_command("feedback", aliases={"report"}, priority=5)
rate = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "hl",
        Args['value', str]['code', str],
        meta=CommandMeta(
            "获取现实货币与人民币的汇率",
            usage="可以模糊查询，支持eve所有物品",
            example="fy 毒蜥",
        )
    ),
    aliases=("汇率", "HL")
)


@eve_time.handle()
async def handle_get_evetime():
    eve_zone = pytz.timezone('UTC')
    utc_time = datetime.now(tz=eve_zone).strftime('%Y-%m-%d %H:%M:%S')
    await eve_time.finish(f"eve游戏时间: {utc_time}")


@rate.handle()
async def get_rate(
        value: str,
        code: str
):
    if value:
        result = await get_exchange_rate(value, code)
        await rate.finish(result)


@feed_back.handle()
async def _(bot: Bot, event: Event):
    data = await check_id(event)
    msg = str(data) + str(event.message)
    await bot.send_private_msg(user_id=next(iter({int(uid) for uid in config.superusers})), message=msg)
    await feed_back.finish("已向作者发送消息")


refresh = on_command("refresh_market", priority=5)


@refresh.handle()
async def _():
    await refresh_price_cache()
