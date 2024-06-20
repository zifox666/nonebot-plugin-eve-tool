from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment, Bot, Event
from nonebot import logger

from ..model.config import plugin_config
from ..utils.price import get_marketer_price

from nonebot import require

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import (
    on_alconna,
    Match,
    Query,
    AlconnaMatch,
    AlcResult
)
from arclet.alconna import Alconna, Args, Option, Arparma, Subcommand, CommandMeta, OptionResult, MultiVar

__all__ = ["query_price"]

query_price = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "ojita",
        Args['args', MultiVar(str)],
        Option(
            "-u|--use",
            Args["api", str],
            help_text="选择市场查询所用的API['ceve', 'esi', 'tycoon']",
            default=OptionResult(args={"api": plugin_config.eve_market_preference})
        ),
        Option(
            "--history",
            Args["history", str],
            help_text="选择是否显示历史曲线['follow', 'mix', 'none', 'only']",
            default=OptionResult(args={"history": plugin_config.eve_history_preference})
        ),
        meta=CommandMeta(
            "查询欧服吉他价格",
            usage="可以模糊查询名称或者名称*数量",
            example="ojita 毒蜥级*10",
        ),
    ),
    aliases=("查价", "Ojita", "OJITA")
)

alias_plex = {
    "月卡": 500,
    "季卡": 1200,
    "半年卡": 2100,
    "年卡": 3600,
    "两年卡": 6600,
    "plex": 500,
    "PLEX": 500,
    "伊甸币": 500
}


@query_price.handle()
async def _query_price(
        bot: Bot,
        event: Event,
        args: tuple[str, ...],
        api: str,
        history: str
):
    args = ' '.join(args)
    item_name = args if "*" not in args else args.split("*")[0].strip()
    num = 1 if "*" not in args else (int(args.split("*")[1].strip()) if args.split("*")[1].strip().isdigit() else 1)

    # PLEX特殊处理
    if num == 1 and item_name in alias_plex:
        num = alias_plex[item_name]
        item_name = "plex"
    logger.info(f"查询价格:{item_name}*{num}")

    if item_name:
        result = await get_marketer_price(item_name, api, num)
        # pic = await _md2pic(text)
        await query_price.finish(MessageSegment.text(result))
    else:
        await query_price.finish("数据错误")

