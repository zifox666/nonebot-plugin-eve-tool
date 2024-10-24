from nonebot import on_command, Bot, logger

from ..model.initialize import init_data
from ..database.redis.cache import RA, delete_empty_cache_entries
from ..utils import download_sde
from ..utils.dataProcess import MYSQL
from ..model.sde import load_sde_to_mysql
from ..src import templates_path
from ..utils.png import md2pic, html2pic
from ..model import plugin_config
from nonebot.adapters.onebot.v11 import MessageSegment


help_list = on_command("help", block=True)


@help_list.handle()
async def _(bot: Bot):
    with open(templates_path / "help.html", "r", encoding="utf-8") as file:
        template_content = file.read()
    await help_list.finish(MessageSegment.image(await html2pic(template_content)))


import_sde = on_command("/更新sde")
clean_cache = on_command("/清除缓存")


@import_sde.handle()
async def _():
    logger.debug("正在更新")
    await download_sde(plugin_config.eve_sde_path)
    await load_sde_to_mysql(MYSQL, sde_path=plugin_config.eve_sde_path)
    await init_data(RA, MYSQL)
    await clean_cache()
    await import_sde.finish("更新SDE完成")


@clean_cache.handle()
async def clean_cache():
    await delete_empty_cache_entries()
