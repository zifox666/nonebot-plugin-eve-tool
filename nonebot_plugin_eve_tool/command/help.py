from nonebot import on_command, Bot

from ..src import templates_path
from ..utils.png import md2pic, html2pic
from nonebot.adapters.onebot.v11 import MessageSegment


help_list = on_command("help", block=True)


@help_list.handle()
async def _(bot: Bot):
    with open(templates_path / "help.html", "r", encoding="utf-8") as file:
        template_content = file.read()
    await help_list.finish(MessageSegment.image(await html2pic(template_content)))
