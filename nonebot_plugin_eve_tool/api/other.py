from .aioclient import aioClient

from nonebot import logger
from typing import *

from ..utils import is_chinese, get_currency_code


async def get_short_url(long_url: str, call_qq: str, send_group: str = "private") -> str:
    """
    获取带标记的短链接
    :param long_url: 原链接
    :param call_qq: 请求链接的QQ
    :param send_group: 请求链接的群
    :return:返回短链接code
    """
    payload = {
        "long_url": long_url,
        "call_qq": call_qq,
        "send_group": send_group
    }
    data = await aioClient.post(uri="http://192.168.0.110:18000/shorten/", data=payload)
    return data["short_url"]


async def get_exchange_rate(value, currency):
    if is_chinese(currency):
        currency = await get_currency_code(currency)
        if currency is None:
            return "查询失败,请确认货币代码是否正确或者是否支持该货币"
    currency_url = f"http://freecurrencyrates.com/api/action.php?do=cvals&iso=CNY&f={currency}&v={value}"
    data = await aioClient.get(currency_url)
    if data:
        obj = format(data.json["CNY"], '.3f')
        text = f"{value} {currency} = {obj} CNY(人民币)"
        return text
    else:
        return "查询失败,请确认货币代码是否正确或者是否支持该货币"

