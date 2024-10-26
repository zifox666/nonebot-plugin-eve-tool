import asyncio
import random

from nonebot import logger
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import MessageSegment

from ..database.redis.search import RA
from .speed_limit import speed_limit, save_url
from ..model import KillMailDetails
from ..src import use_killmail_html
from .png import html2pic, html2pic_element
from .statis import insert_statis


async def process_image(kill_mail_details: KillMailDetails) -> KillMailDetails:
    kill_mail_details.img = kill_mail_details.pic
    return kill_mail_details


async def message_send(bot: Bot, push_item, kill_mail_details):
    if push_item['push_type'] == 'group':
        # kill_mail_details = await process_image(kill_mail_details, 'G', push_item[3])
        kill_mail_details = await process_image(kill_mail_details)
        return await bot.send_group_msg(group_id=push_item['push_to'], message=MessageSegment.image(kill_mail_details.img))
    else:
        # kill_mail_details = await process_image(kill_mail_details, 'F', push_item[3])
        kill_mail_details = await process_image(kill_mail_details)
        return await bot.send_private_msg(user_id=push_item['push_to'], message=MessageSegment.image(kill_mail_details.img))


async def process_push_items(push_items, subscription_type, kill_mail_details, bot):
    delay_time = 5
    for push_item in push_items:
        try:
            kill_mail_details.title = f"{push_item['title']} {subscription_type}"
        except:
            kill_mail_details.title = "高价值击杀"
            delay_time = random.randint(0, 1)
        target_id = int(push_item['push_to'])
        # 推送限速器
        echo = await speed_limit(kill_mail_details.kill_mail_id, target_id)
        if echo:
            continue

        await insert_statis(
            "killmail_push",
            f"{kill_mail_details.title}:{kill_mail_details.kill_mail_id}",
            push_item['push_to'],
            push_item['push_to']
        )
        html_template = await use_killmail_html(kill_mail_details)
        # kill_mail_details.pic = await html2pic_element(html_content=str(html_template), element="container")
        kill_mail_details.pic = await html2pic(str(html_template), width=680, height=1080)
        message_id = await message_send(bot, push_item, kill_mail_details)
        message_id = message_id.get('message_id', 0)
        logger.debug(message_id)
        # await asyncio.sleep(delay_time)
        await save_url(
            RA,
            push_item['push_to'],
            message_id,
            f'https://zkillboard.com/kill/{kill_mail_details.kill_mail_id}'
        )


async def message_handler(bot: Bot, kill_mail_details: KillMailDetails) -> bool:
    if kill_mail_details.victim_char_push:
        await process_push_items(
            kill_mail_details.victim_char_push, '角色损失', kill_mail_details, bot
        )

    if kill_mail_details.victim_corp_push:
        await process_push_items(
            kill_mail_details.victim_corp_push, '军团损失', kill_mail_details, bot
        )

    if kill_mail_details.attacker_char_push:
        await process_push_items(
            kill_mail_details.attacker_char_push, '角色击杀', kill_mail_details, bot
        )

    if kill_mail_details.attacker_corp_push:
        await process_push_items(
            kill_mail_details.attacker_corp_push, '军团击杀', kill_mail_details, bot
        )

    if kill_mail_details.high_value_push:
        await process_push_items(
            kill_mail_details.high_value_push, '高价值击杀订阅', kill_mail_details, bot
        )

    return True
