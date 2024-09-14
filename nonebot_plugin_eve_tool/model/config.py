from typing import List, Literal

import nonebot
from nonebot import get_plugin_config
from nonebot.log import logger
from pydantic import BaseModel, field_validator

from ..model.common import data_path


__all__ = ["Config", "plugin_config"]

_driver = nonebot.get_driver()


class FileNotExistError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Config(BaseModel):
    """插件设置"""
    """MYSQL配置"""
    eve_mysql_host: str = 'localhost'
    eve_mysql_port: int = 3306
    eve_mysql_user: str = 'root'
    eve_mysql_password: str
    eve_mysql_db: str = 'eve_tool'

    """Redis配置"""
    eve_redis_url: str = 'redis://localhost:6379/0'

    @field_validator('eve_redis_url')
    def validate_eve_mysql_url(cls, v):
        if not v.startswith('redis://'):
            raise ValueError('URL must start with redis://')
        return v

    """代理配置"""
    eve_proxy: str = None

    """市场设置"""
    eve_market_preference: str = 'esi'
    eve_janice_api_key: str = 'G9KwKq3465588VPd6747t95Zh94q3W2E'
    eve_word_cut: str = 'jieba'
    eve_history_preference: str = 'follow'

    @field_validator('eve_market_preference')
    def check_eve_market_preference(cls, v):
        allowed_values = {'tycoon', 'ceve', 'esi', 'esi_cache'}
        if v not in allowed_values:
            raise ValueError(f'eve_market_preference must be one of {allowed_values}')
        return v

    @field_validator('eve_history_preference')
    def check_eve_history_preference(cls, v):
        allowed_values = {'follow', 'only', 'none'}
        if v not in allowed_values:
            raise ValueError(f'eve_market_preference must be one of {allowed_values}')
        return v

    @field_validator('eve_janice_api_key')
    def check_eve_janice_api_key(cls, v):
        if v == 'G9KwKq3465588VPd6747t95Zh94q3W2E':
            logger.info('请向Janice作者申请专属API_KEY，临时KEY有使用限制。请访问https://github.com/E-351/janice获取')
        return v

    """kill mail偏好"""
    eve_km_speed_limit: int = 0
    eve_km_send_delay: int = 3

    eve_background_png: Literal["LoliAPI", "Lolicon"] = "LoloAPI"

    """SDE存放位置"""
    eve_sde_path: str = data_path / 'sde'

    """语言偏好"""
    eve_lagrange_preference: str = 'zh'

    """常规设置"""
    eve_command_start: List[str] = ["/", "", "！", ".", "!", "#"]

    """作者id"""
    SUPERUSERS: int = 123456


plugin_config = get_plugin_config(Config)
