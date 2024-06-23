import re
import sys

import jieba
import json
from nonebot import logger

from ..model import plugin_path


eve_word_path = str(plugin_path / 'src' / 'word_handle' / 'text.txt')
read_keyword_path = plugin_path / 'src' / 'word_handle' / "replace.json"
jieba.load_userdict(eve_word_path)
jieba.initialize()
jieba.suggest_freq(('中', '大', '小'), True)
keyword_pairs = []
if sys.platform.startswith('linux'):
    jieba.enable_parallel(12)


async def read_keyword():
    global keyword_pairs
    with open(read_keyword_path, 'r', encoding='utf-8') as file:
        keyword_pairs = json.load(file)


async def replace_word(word):
    global keyword_pairs
    if not keyword_pairs:
        await read_keyword()
    for pair in keyword_pairs:
        for old_word, new_word in pair.items():
            word = word.replace(old_word, new_word)
    return word


async def jieba_cut_word(word):
    word = await replace_word(word)
    words = jieba.lcut(word)
    result = " ".join(words)
    logger.debug(f"jieba分词结果:\n{result}")
    regex = '.*' + '.*'.join(f'(?=.*{re.escape(word)})' for word in result.split()) + '.*'
    return regex


async def new_cut_word(wait_word):
    # 将查询字符串按照中文字符进行分割，并过滤空白字符
    queryWords = re.split(r'(\d+|[a-zA-Z]+|[\u4e00-\u9fa5])', wait_word)
    # 将连续的中文字符拆分成单个字符
    queryWords = [char for word in queryWords for char in word.strip() if char.strip() != '']
    regex = '.*' + '.*'.join(f'(?=.*{re.escape(word)})' for word in queryWords) + '.*'
    return regex



