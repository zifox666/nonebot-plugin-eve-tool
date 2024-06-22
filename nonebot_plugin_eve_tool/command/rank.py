from ..model.config import plugin_config
from ..api import get_corp_id, get_corp_info, get_char_title
from ..utils.png import md2pic

from nonebot import require

require("nonebot_plugin_alconna")

from nonebot_plugin_alconna import on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage
from arclet.alconna import Alconna, Args, CommandMeta, MultiVar


__all__ = ["rank"]


rank = on_alconna(
    Alconna(
        plugin_config.eve_command_start,
        "rank",
        Args['args', MultiVar(str)],
        meta=CommandMeta(
            "查询某个军团的签名排行榜",
            usage="查询某个军团的签名排行榜（支持缩写）",
            example="rank THXFC",
            fuzzy_match=True
        )
    ),
    aliases=("签名排行", "军团排名")
)


@rank.handle()
async def handle_rank(
        args: tuple
):
    args = ' '.join(args)
    if args:
        corp_name = args
        corp_id = await get_corp_id(corp_name)
        if not corp_id:
            await rank.finish(f"请检查军团名称[{args}]")
        data = await get_corp_info(corp_id)
        data = data['topLists']
        if data[0]['type'] == 'character':
            text = f"##[{corp_name}]军团签名排行榜\n"
            for char in data[0]['values']:
                title = await get_char_title(char['id'])
                kills = char['kills']
                if title:
                    text += f"* {char['characterName']} [{title}] 签名：{kills}\n"
                else:
                    text += f"* {char['characterName']} [无头衔] 签名：{kills}\n"
            pic = await md2pic(text)
            await rank.finish(UniMessage.image(pic))

    