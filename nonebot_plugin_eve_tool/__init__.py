from nonebot.plugin import PluginMetadata
from nonebot import logger

from . import _version

__version__ = _version.__version__

from nonebot import init
from nonebot import get_driver

from .model.config import plugin_config, Config
from .database.redis.RedisArray import RedisArray
from .database.mysql.MysqlArray import MysqlArray
from .model import initialize

# from .utils import mission

from .command import *


__plugin_meta__ = PluginMetadata(
    name="EVE ONLINE 多功能机器人\n版本 - {__version__}\n",
    description="EVE ONLINE-游戏查价，合同，游戏信息查询\n",
    usage="导入并安装mysql和redis即可使用",

    type="application",
    # 发布必填，当前有效类型有：`library`（为其他插件编写提供功能），`application`（向机器人用户提供功能）。

    homepage="https://github.com/zifox666/nonebot-plugin-eve-tool",
    # 发布必填。

    config=Config,
    # 插件配置项类，如无需配置可不填写。

    supported_adapters={"~onebot.v11"},
    # 支持的适配器集合，其中 `~` 在此处代表前缀 `nonebot.adapters.`，其余适配器亦按此格式填写。
    # 若插件可以保证兼容所有适配器（即仅使用基本适配器功能）可不填写，否则应该列出插件支持的适配器。
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

print("""
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
    await RA.execute('FLUSHDB')
    await RA.close()
    await MYSQL.close()



