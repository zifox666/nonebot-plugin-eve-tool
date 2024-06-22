from ..model.config import plugin_config
from ..utils import is_chinese
from ..utils.trans import get_trans

from nonebot import require

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import (
    on_alconna
)
from arclet.alconna import Alconna, Args, Option, CommandMeta, OptionResult, MultiVar


__all__ = ["trans"]


trans = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "trans",
        Args['args', MultiVar(str)],
        Option(
            "-n|--num",
            Args["num", int],
            help_text="选择显示的条数，默认为6个",
            default=OptionResult(args={"num": 6})
        ),
        meta=CommandMeta(
            "获取eve物品中英文对照",
            usage="可以模糊查询，支持eve所有物品",
            example="fy 毒蜥",
        )
    ),
    aliases=("翻译", "fy", "fanyi")
)


@trans.handle()
async def trans_handle(
        args: tuple,
        num: int
):
    args = ' '.join(args)
    if args:
        lagrange = 'zh' if is_chinese(args) else 'en'
        result = await get_trans(
            args,
            num,
            lagrange
        )
        await trans.finish(result)
