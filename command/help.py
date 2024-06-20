from typing import Union

from nonebot import on_command
from nonebot.internal.params import ArgStr
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..command.common import CommandRegistry
from ..model import plugin_config, CommandUsage
