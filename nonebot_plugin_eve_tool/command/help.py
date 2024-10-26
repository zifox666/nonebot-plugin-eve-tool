from nonebot import on_command, Bot, logger

from ..model.initialize import init_data
from ..database.redis.cache import RA, delete_empty_cache_entries
from ..utils import download_sde
from ..utils.dataProcess import MYSQL
from ..model.sde import load_sde_to_mysql
from ..src import templates_path
from ..utils.png import md2pic, html2pic, render_help
from ..model import plugin_config
from .._version import __version__
from nonebot.adapters.onebot.v11 import MessageSegment


help_list = on_command("help", block=True)


@help_list.handle()
async def _(bot: Bot):
    help_data = {
        "headStyle": "<style>body { background-color: #f0f0f0; }</style>",
        "helpData": [
            {
                "group": "信息查询类",
                "list": [
                    {
                        "icon": "archaic_stone.png",
                        "title": "ojita",
                        "desc": "ojita [查询名称]*<数量> 查询吉他市场价格"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "trans",
                        "desc": "trans [查询名称] 查询中英文对照翻译"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "合同估价",
                        "desc": "合同估价 [合同内容完整复制] 合同估价"
                    }
                ]
            },
            {
                "group": "zkillboard类",
                "list": [
                    {
                        "icon": "archaic_stone.png",
                        "title": "zkb",
                        "desc": "zkb [角色名] 查询角色危险度"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "rank",
                        "desc": "rank [军团名/军团缩写] 查询军团签名排行榜"
                    }
                ]
            },
            {
                "group": "killmail订阅类 - 不会用请联系超级管理员",
                "list": [
                    {
                        "icon": "archaic_stone.png",
                        "title": "新增/更改指定击杀",
                        "desc": "/击杀订阅 add --[char|corp] [name] -a [value] -v [value]"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "移除指定订阅",
                        "desc": "/击杀订阅 remove --[char|corp] [name]"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "新增/更改高价值推送",
                        "desc": "/高价值击杀订阅 add [value] <- 推送价格最低8b（8_000_000_000）"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "移除高价值推送",
                        "desc": "/高价值击杀订阅 remove"
                    }
                ]
            },
            {
                "group": "链接预览类",
                "list": [
                    {
                        "icon": "archaic_stone.png",
                        "title": "预览zkb信息",
                        "desc": "发送zkb链接即可"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "预览janice估价",
                        "desc": "发送janice链接即可"
                    }
                ]
            },
            {
                "group": "其他功能",
                "list": [
                    {
                        "icon": "archaic_stone.png",
                        "title": "查询eve时间",
                        "desc": "/evetime"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "联系作者",
                        "desc": "feedback 后面写你要找作者说的话，也可以直接加作者qq"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "EVE老黄历",
                        "desc": "发送 老黄历 即可，差异化占卜正在新建文件夹"
                    },
                    {
                        "icon": "archaic_stone.png",
                        "title": "查询链接",
                        "desc": "回复机器人发送的zkb相关图片加上/link就可以获得链接"
                    }
                ]
            }
        ],
        "version": __version__
    }
    await help_list.finish(MessageSegment.image(await render_help(help_data)))


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
