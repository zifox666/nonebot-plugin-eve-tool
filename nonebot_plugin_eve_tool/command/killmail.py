import asyncio
import re
import traceback
import time
import json

import httpx
import httpx_ws
import websockets

import nonebot
from nonebot import logger, on_command, on_regex
from nonebot.adapters import Bot, Event
from nonebot.adapters.onebot.v11 import MessageSegment

from nonebot import require

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

from ..src import use_killmail_html
from ..api import get_esi_kill_mail
from ..utils.killmail_handle import kill_mail_handle
from ..utils.png import html2pic
from ..utils.shit import message_handler, process_image
from ..model.config import plugin_config

__all__ = ["kb_listen", "close_listen", "killmail_matcher", "km", "start_wss", "stop_wss"]

running = True
last_action_time = time.time()

kb_listen = on_command("#启动wss")
close_listen = on_command("#关闭wss")
killmail_matcher = on_regex(r"https://zkillboard\.com/kill/(\d+)/")


ws = None


km_recv = 0


@kb_listen.handle()
async def start_wss(bot: Bot):
    global running
    running = True
    await km(bot)


@close_listen.handle()
async def stop_wss():
    global running
    running = False


"""async def km(bot: Bot):
    uri = "wss://zkillboard.com/websocket/"
    global km_recv
    while running:
        try:
            async with websockets.connect(uri) as _websocket:
                logger.info("zkill-WebSocket 连接成功")
                await _websocket.send(json.dumps({"action": "sub", "channel": "killstream"}))
                while running:
                    message = await _websocket.recv()
                    message_json = json.loads(message)
                    km_recv = km_recv + 1
                    kill_id = message_json["killmail_id"]
                    zkb_url = message_json["zkb"]["url"]
                    logger.debug(f"[{str(kill_id)}]{str(zkb_url)}")

                    kill_mail_details = await kill_mail_handle(message_json)
                    if kill_mail_details:
                        echo = await message_handler(bot, kill_mail_details)
                        if echo:
                            logger.info(f'{kill_id} send success')
                            del kill_mail_details

        except websockets.ConnectionClosed:
            logger.error("WebSocket 连接断开，尝试重新连接...")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"wss发生错误：{e}\n{traceback.format_exc()}")
            await asyncio.sleep(5)"""


async def km(bot: Bot):
    uri = "http://192.168.0.110:18920/killmail"
    client_id = "001"
    global km_recv

    while running:
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.get(f"{uri}?client_id={client_id}")

                message_json = response.json()

                if message_json.get("package") is None:
                    await asyncio.sleep(5)
                else:
                    message_json = message_json.get("package")
                    km_recv = km_recv + 1
                    kill_id = message_json["killmail_id"]
                    zkb_url = message_json["zkb"]["url"]
                    logger.debug(f"[{str(kill_id)}]{str(zkb_url)}")

                    await asyncio.create_task(handle_kill_mail(message_json, bot))

        except Exception as e:
            logger.error(f"Error: {e}\n{traceback.format_exc()}")
            await asyncio.sleep(10)


async def handle_kill_mail(message_json, bot):
    kill_mail_details = await kill_mail_handle(message_json)
    if kill_mail_details:
        echo = await message_handler(bot, kill_mail_details)
        if echo:
            logger.info(f'{message_json["killmail_id"]} send success')


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
