import nonebot
from nonebot import get_plugin_config
from nonebot.log import logger
from pydantic import BaseModel, field_validator

from ..model.common import data_path

import os
from zipfile import ZipFile

import requests
from tqdm import tqdm

__all__ = ["Config", "plugin_config"]

plugin_config_path = data_path / "config.json"
"""插件数据文件默认路径"""
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
    eve_redis_url: str = 'redis://127.0.0.1:6379/0'

    @field_validator('eve_redis_url')
    def validate_eve_mysql_url(cls, v):
        if not v.startswith('redis://'):
            raise ValueError('URL must start with redis://')
        return v

    """代理配置"""
    eve_proxy: str = None

    """市场设置"""
    eve_market_preference: str = 'mix'
    eve_janice_api_key: str = 'G9KwKq3465588VPd6747t95Zh94q3W2E'

    @field_validator('eve_market_preference')
    def check_eve_market_preference(cls, v):
        allowed_values = {'mix', 'ceve'}
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

    """SDE存放位置"""
    eve_sde_path: str = data_path / 'sde'

    @field_validator('eve_sde_path')
    def check_eve_sde_path(cls, v):
        files = ["types.yaml", "marketGroups.yaml", "metaGroups.yaml", "groups.yaml", "categories.yaml"]
        if check_files_exist(v, files):
            logger.info('SDE文件已导入')
        else:
            logger.info('SDE文件不存在，开始下载')
            if download_sde(v):
                return v
            else:
                raise FileNotFoundError(f'SDE自动下载失败，请手动放置SDE文件到{v}下')


def check_files_exist(directory, filenames):
    if not os.path.exists(directory):
        return False
    fsd_directory = directory / 'fsd'
    for filename in filenames:
        file_path = os.path.join(fsd_directory, filename)
        if not os.path.isfile(file_path):
            return False

    return True


def download_file(url, local_path):
    response = requests.get(url, stream=True)
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
    local_zip_path = os.path.join(directory, 'sde.zip')
    if not os.path.isfile(local_zip_path):
        download_file("https://eve-static-data-export.s3-eu-west-1.amazonaws.com/tranquility/sde.zip", local_zip_path)
    with ZipFile(local_zip_path, 'r') as zip_file:
        zip_file.extractall(directory)
    logger.success(f"SDE已下载并解压到 '{directory}'")
    return True


plugin_config = get_plugin_config(Config)
