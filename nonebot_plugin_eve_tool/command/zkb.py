import traceback

from ..src import use_kb_info_html
from ..model.config import plugin_config
from ..api import get_character_id
from ..utils.png import html2pic
from nonebot import require, logger

from ..utils.zkb import get_character_kb

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage
from arclet.alconna import Alconna, Args, CommandMeta, MultiVar

__all__ = ['zkb']


zkb = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "zkb",
        Args['args', MultiVar(str)],
        meta=CommandMeta(
            "查询某个角色的kb信息",
            usage="查询某个角色的kb信息",
            example="zkb Redeovg"
        )
    ),
    aliases=("kb", "ZKB", "KB"),
    auto_send_output=True
)


@zkb.handle()
async def handle_get_zkb(
        args: tuple
):
    args = " ".join(args)
    if args:
        char_name = args
        try:
            char_id = await get_character_id(char_name)
            if char_id == "":
                await zkb.finish("角色名称错误")
            if char_id:
                char_info = await get_character_kb(char_id)
                echo = await use_kb_info_html(char_info)
                pic = await html2pic(echo)
                if echo:
                    await zkb.finish(UniMessage.image(pic))
            else:
                await zkb.finish(f"未找到[{char_name}]，可能是未绑定zkb网")
        except Exception as e:
            logger.error(f"zkb error:{e}\n{traceback.format_exc()}")
    else:
        await zkb.finish("名称错误")

    
