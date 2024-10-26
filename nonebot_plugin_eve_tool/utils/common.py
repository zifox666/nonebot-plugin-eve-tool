import base64
import io
import json
import os
import random
import re
from datetime import datetime

import httpx
from dateutil import parser
from pathlib import Path
from typing import (Dict, Literal,
                    Union, Optional, Tuple, Iterable, List, Any)

import aiohttp
import yaml
import qrcode
from nonebot import Bot
from nonebot.adapters import Event
from nonebot.log import logger
import nonebot


import os
from zipfile import ZipFile
from tqdm.asyncio import tqdm
from urllib3.util import Url

try:
    from loguru import Logger
except ImportError:
    Logger = None
    pass

from ..model import data_path, plugin_path, plugin_config

bots = nonebot.get_bots()


async def get_group_info(event: Event, bot: Bot) -> Tuple[str | None, str | None]:
    user_id, group_id = event.user_id, event.group_id
    bot_id = bot.self_id
    if int(user_id) == int(bot_id):
        return user_id, group_id
    else:
        return None, None


async def generate_qrcode(text: str) -> str:
    """
    生成文本二维码
    :param text:
    :return: base64 encoded
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="rgb(25,25,25)", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode()


def is_chinese(word: str) -> bool:
    """
    判断中文字符

    :param word: 字符
    :return:
    """
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def remove_color(text: str) -> str:
    """
    去除彩色代码

    :param text: 需要去除的字符串
    :return:
    """
    text = re.sub(r'<color=.*?>', "", text)
    text = re.sub(r'</color>', "", text)
    text = re.sub(r'<b>', "", text)
    text = re.sub(r'</b>', "", text)
    return text


async def get_currency_code(currency: str) -> Optional[str]:
    """
    获取货币代码

    :param currency:
    :return:
    """
    # 打开currency_code.json文件
    file_path = plugin_path / 'src' / 'other' / 'currency_code.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        currency_code = json.load(f)
    # 获取货币代码
    if currency.upper() in list(currency_code.keys()):
        return currency.upper()
    else:
        for c in currency_code.keys():
            if currency in currency_code[c]:
                return c
    return None


def get_wormholes(wormholes_name: str) -> List[str] | None:
    """
    获取虫洞数据

    :param wormholes_name:
    :return:
    """
    with open(data_path + '/wormholes.json', 'r', encoding='utf-8') as f:
        wormholes = json.load(f)
        if wormholes_name in wormholes.keys():
            return wormholes[wormholes_name]
        else:
            return None


def check_files_exist(directory, filenames) -> bool:
    """
    判断文件是否存在
    """
    if not os.path.exists(directory):
        return False
    for filename in filenames:
        if not os.path.isfile(os.path.join(directory, filename)):
            return False
    return True


async def download_file(url, local_path, proxy=None):
    """
    可视化进度条下载文件
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, proxy=proxy) as response:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True, miniters=1)

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, 'wb') as file:
                async for data in response.content.iter_chunked(block_size):
                    file.write(data)
                    progress_bar.update(len(data))
            progress_bar.close()

            if total_size != 0 and progress_bar.n != total_size:
                logger.error("ERROR: Something went wrong")


async def download_sde(directory):
    """
    sde文件更新
    """
    local_zip_path = os.path.join(directory, 'sde.zip')
    await download_file("https://eve-static-data-export.s3-eu-west-1.amazonaws.com/tranquility/sde.zip", local_zip_path)
    with ZipFile(local_zip_path, 'r') as zip_file:
        zip_file.extractall(directory)
    logger.success(f"SDE已下载并解压到 '{directory}'")
    return True


async def load_yaml(file_path):
    """
    读取yaml配置文件
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)


def format_price(price):
    """
    整理价格，千分位
    :param price:
    :return:
    """
    a = format(float(price), '.2f')
    return format(float(a), ',')


def pack_strings(words):
    packed_string = str(''.join([word.strip() for word in words if word.strip()]))
    return packed_string


async def check_id(event) -> dict[str, str]:
    """
    判断用户权限及群聊或者私聊
    """
    result = {}
    if event.sub_type == "normal":
        if event.sender.role == "member":
            result = {
                "type": "c",
                "gid": event.group_id,
                "uid": event.sender.user_id
            }
        else:
            result = {
                "type": "group_admin",
                "gid": event.group_id,
                "uid": event.sender.user_id
            }
    if event.sub_type == "friend":
        result = {
            "type": "friend",
            "gid": event.user_id,
            "uid": event.user_id
        }
    return result


async def time_change(time_str: str) -> str:
    utc_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")

    return utc_time.strftime("%Y-%m-%d %H:%M:%S")


def time_difference(target_time_str: str) -> str:
    """
    返回时间差值
    """
    target_time = parser.parse(target_time_str)

    now = datetime.utcnow()

    difference = now - target_time

    seconds = difference.total_seconds()

    if seconds < 60:
        return f"{int(seconds)} 秒前"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{int(minutes)} 分钟前"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{int(hours)} 小时前"
    else:
        days = seconds / 86400
        return f"{int(days)} 天前"


async def get_lolicon_image() -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.lolicon.app/setu/v2")
    return response.json()["data"][0]["urls"]["original"]


async def get_background_image() -> str | Url:

    match plugin_config.eve_background_png:
        case "LoliAPI":
            background_image = "https://www.loliapi.com/acg/pe/"
        case "Lolicon":
            background_image = await get_lolicon_image()
        case _:
            background_image = "https://www.loliapi.com/acg/pe/"

    return background_image


async def type_word(args: str) -> str:
    """
    整理合同内容
    """
    # 替换所有 \r 为 \n
    args = args.replace('\r', '\n')
    lines = args.split('\n')
    converted_text = ''
    for line in lines:
        fields = line.split('\t')
        converted_text += '\t'.join(fields) + '\n'
    return converted_text

