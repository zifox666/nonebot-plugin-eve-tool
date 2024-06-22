from nonebot.plugin import PluginMetadata
from nonebot import logger

from . import _version

__version__ = _version.__version__

from nonebot import init
from nonebot import get_driver
from nonebot.plugin import inherit_supported_adapters

from .model.config import plugin_config, Config
from .database.redis.RedisArray import RedisArray
from .database.mysql.MysqlArray import MysqlArray
from .model import initialize

from .utils import mission

from .command import *
from .src import *


__plugin_meta__ = PluginMetadata(
    name=f"EVE ONLINE 多功能机器人\n版本 - {__version__}\n",
    description="EVE ONLINE-游戏查价，合同，游戏信息查询\n",
    usage="导入并安装mysql和redis即可使用",

    type="application",

    homepage="https://github.com/zifox666/nonebot-plugin-eve-tool",

    config=Config,

    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
)


init()
driver = get_driver()
RA = RedisArray(plugin_config.eve_redis_url)
MYSQL = MysqlArray(
    host=plugin_config.eve_mysql_host,
    port=plugin_config.eve_mysql_port,
    user=plugin_config.eve_mysql_user,
    password=plugin_config.eve_mysql_password,
    database=plugin_config.eve_mysql_db
)

logger.info("""

                                                                           .-'''-.        .-'''-.          
                                                                          '   _    \     '   _    \  .---. 
       __.....__   .----.     .----.   __.....__                        /   /` '.   \  /   /` '.   \ |   | 
   .-''         '.  \    \   /    /.-''         '.                     .   |     \  ' .   |     \  ' |   | 
  /     .-''"'-.  `. '   '. /'   //     .-''"'-.  `.                .| |   '      |  '|   '      |  '|   | 
 /     /________\   \|    |'    //     /________\   \             .' |_\    \     / / \    \     / / |   | 
 |                  ||    ||    ||                  |           .'     |`.   ` ..' /   `.   ` ..' /  |   | 
 \    .-------------''.   `'   .'\    .-------------'          '--.  .-'   '-...-'`       '-...-'`   |   | 
  \    '-.____...---. \        /  \    '-.____...---.             |  |                               |   | 
   `.             .'   \      /    `.             .'              |  |                               |   | 
     `''-...... -'      '----'       `''-...... -'                |  '.'                             '---' 
                                                                  |   /                                    
                                                                  `'-'                                     
""")


@driver.on_startup
async def startup():
    await RA.create_pool()
    echo = await MYSQL.create_pool()
    logger.info(echo)
    if not echo:
        logger.info('数据库不存在，开始初始化数据库')
        await initialize.create_db(MYSQL)

    await initialize.init_data(RA, MYSQL)


@driver.on_shutdown
async def shutdown():
    await stop_wss()
    await RA.execute('FLUSHDB')
    await RA.close()
    await MYSQL.close()


@driver.on_bot_connect
async def bot_connect(bot: Bot):
    await start_wss(bot)


@driver.on_bot_disconnect
async def bot_disconnect():
    await stop_wss()
