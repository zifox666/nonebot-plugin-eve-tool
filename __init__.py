from textwrap import dedent

from nonebot.plugin import PluginMetadata
from nonebot import logger


from . import _version

__version__ = _version.__version__
__plugin_meta__ = PluginMetadata(
    name=f"EVE ONLINE 多功能机器人\n版本 - {__version__}\n",
    description="EVE ONLINE-游戏查价，合同，游戏信息查询\n",
    usage=
    "未完待续",
    extra={"version": __version__}
)

from nonebot import init
from nonebot import get_driver

from .model.config import plugin_config
from .database.redis.RedisArray import RedisArray
from .database.mysql.MysqlArray import MysqlArray
from .model import initialize

init()
driver = get_driver()
RA = RedisArray(url=plugin_config.eve_redis_url)
MYSQL = MysqlArray(
    host=plugin_config.eve_mysql_host,
    port=plugin_config.eve_mysql_port,
    user=plugin_config.eve_mysql_user,
    password=plugin_config.eve_mysql_password,
    database=plugin_config.eve_mysql_db
)

print("""
 _______   ___      ___ _______  _________  ________  ________  ___          
|\  ___ \ |\  \    /  /|\  ___ \|\___   ___\\   __  \|\   __  \|\  \         
\ \   __/|\ \  \  /  / | \   __/\|___ \  \_\ \  \|\  \ \  \|\  \ \  \        
 \ \  \_|/_\ \  \/  / / \ \  \_|/__  \ \  \ \ \  \\\  \ \  \\\  \ \  \       
  \ \  \_|\ \ \    / /   \ \  \_|\ \  \ \  \ \ \  \\\  \ \  \\\  \ \  \____  
   \ \_______\ \__/ /     \ \_______\  \ \__\ \ \_______\ \_______\ \_______\
    \|_______|\|__|/       \|_______|   \|__|  \|_______|\|_______|\|_______|
""")


@driver.on_startup
async def startup():
    await RA.create_pool()
    echo = await MYSQL.create_pool()
    logger.info(echo)
    if not echo:
        logger.info('数据库不存在，开始初始化数据库')
        await initialize.create_db(MYSQL, plugin_config.eve_mysql_db)

    await initialize.init_data(RA, MYSQL)


@driver.on_shutdown
async def shutdown():
    await RA.close()
    await MYSQL.close()



