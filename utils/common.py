import io
import json
import os
import random
import re
from pathlib import Path
from typing import (Dict, Literal,
                    Union, Optional, Tuple, Iterable, List, Any)
import yaml
from qrcode import QRCode
from nonebot.log import logger


import os
from zipfile import ZipFile

import requests
from tqdm import tqdm


try:
    from loguru import Logger
except ImportError:
    Logger = None
    pass

from ..model import plugin_config, data_path


def generate_qr_img(data: str):
    """
    生成二维码图片

    :param data: 二维码数据
    """
    qr_code = QRCode(border=2)
    qr_code.add_data(data)
    qr_code.make()
    image = qr_code.make_image()
    image_bytes = io.BytesIO()
    image.save(image_bytes)
    return image_bytes.getvalue()


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
    with open(data_path + '/currency_code.json', 'r', encoding='utf-8') as f:
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


def download_file(url, local_path):
    """
    可视化进度条下载文件
    """
    response = requests.get(
        url,
        stream=True,
        proxies={
            "http": plugin_config.eve_proxy,
            "https": plugin_config.eve_proxy
        })
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)

    with open(local_path, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()

    if total_size != 0 and progress_bar.n != total_size:
        logger.error("ERROR: Something went wrong")


def download_sde(directory):
    """
    sde文件更新
    """
    local_zip_path = os.path.join(directory, 'sde.zip')
    if not os.path.isfile(local_zip_path):
        download_file("https://eve-static-data-export.s3-eu-west-1.amazonaws.com/tranquility/sde.zip", local_zip_path)
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

