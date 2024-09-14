import asyncio
import gc
import json
import re
import traceback
import time

import httpx
import httpx_ws
import nonebot
import websockets
from nonebot import logger, on_command, on_regex
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment

from nonebot import require

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

from ..src import use_killmail_html
from ..api import get_esi_kill_mail
from ..utils.killmail_handle import kill_mail_handle
from ..utils.png import html2pic, html2pic_element
from ..utils.shit import message_handler, process_image
from ..model.config import plugin_config

__all__ = ["kb_listen", "close_listen", "killmail_matcher", "km", "start_wss", "stop_wss"]

running = True
last_action_time = time.time()

kb_listen = on_command("#启动wss")
close_listen = on_command("#关闭wss")
killmail_matcher = on_regex(r"https://zkillboard\.com/kill/(\d+)/")
test_listen = on_command("#测试关闭")


ws = None


@test_listen.handle()
async def _():
    global ws
    await ws.close()


km_recv = 0


@kb_listen.handle()
async def start_wss(bot: Bot):
    global running
    running = True
    await ws_ping()
    await km(bot)


@close_listen.handle()
async def stop_wss():
    global running
    running = False
    scheduler.remove_job('check_ws_status')


async def ws_ping():
    logger.debug("定时任务启动:wss保活")
    await asyncio.sleep(5)
    scheduler.add_job(check_ws_status, 'cron', minute='*/1', id='check_ws_status')


async def check_ws_status():
    global running
    global ws
    global last_action_time
    bot = nonebot.get_bot()
    heartbeat_interval = 60

    logger.debug("ping")

    if ws is None:
        logger.error("检测到 WebSocket 已关闭，尝试重新连接...")
        # await bot.send_group_msg(group_id=745342741, message="WebSocket 已断开，尝试重新连接...")
        await km(bot)
    else:
        current_time = time.time()
        time_since_last_action = current_time - last_action_time

        if time_since_last_action > heartbeat_interval:
            logger.error(f"WebSocket 已假死，尝试重新连接...")
            # await bot.send_group_msg(group_id=745342741, message="WebSocket 假死，尝试重新连接...")
            ws = None
            await km(bot)
        else:
            logger.debug(f"pong!")


async def km(bot: Bot):
    uri = "wss://zkillboard.com/websocket/"
    global km_recv
    global ws
    global last_action_time

    while running:
        try:
            async with httpx.AsyncClient(proxies=plugin_config.eve_proxy) as client:
                async with httpx_ws.aconnect_ws(
                        uri,
                        client
                ) as ws:
                    logger.info("zkill-WebSocket 连接成功")
                    await ws.send_json({"action": "sub", "channel": "killstream"})
                    await ws.send_json({"action": "sub", "channel": "public"})
                    while running:
                        await asyncio.sleep(0.1)

                        message_json = await ws.receive_json()

                        if "action" in message_json:
                            last_action_time = time.time()
                            logger.debug(message_json)
                        else:
                            km_recv += 1
                            kill_id = message_json["killmail_id"]
                            zkb_url = message_json["zkb"]["url"]
                            logger.debug(f"[{km_recv}] kill_id: {kill_id}, uri: {zkb_url}")

                            kill_mail_details = await kill_mail_handle(message_json)
                            if kill_mail_details:
                                echo = await message_handler(bot, kill_mail_details)
                                if echo:
                                    logger.info(f'{kill_id} send success')

        except httpx_ws.WebSocketDisconnect:
            logger.error("WebSocket 连接断开，尝试重新连接...")
            await ws.close()
            await asyncio.sleep(5)
        except httpx_ws.WebSocketNetworkError:
            logger.error("WebSocket 网络错误，尝试重新连接...")
            await ws.close()
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"WebSocket 发生错误：{e}\n{traceback.format_exc()}")
            await ws.close()
            await asyncio.sleep(5)


@killmail_matcher.handle()
async def handle_killmail(event: Event):
    message = str(event.get_message())
    match = re.search(r"https://zkillboard\.com/kill/(\d+)/", message)
    if match:
        kill_id = match.group(1)
        data = await get_esi_kill_mail(kill_id)
        if data:
            kill_mail_details = await kill_mail_handle(data, False)
            kill_mail_details.title = "KM预览"
            html_template = await use_killmail_html(kill_mail_details)
            kill_mail_details.pic = await html2pic(str(html_template), width=660, height=1080)
            kill_mail_details = await process_image(kill_mail_details)
            await killmail_matcher.finish(MessageSegment.image(kill_mail_details.img))
            del kill_mail_details
