from nonebot import require

require("nonebot_plugin_htmlrender")

from nonebot_plugin_htmlrender import (
    text_to_pic,
    md_to_pic,
    template_to_pic,
    get_new_page,
)


async def md2pic(content):
    return await md_to_pic(md=content)

