import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal, NamedTuple, no_type_check, Union, Dict, Any, TypeVar, Tuple

from pydantic import BaseModel

root_path = Path(__name__).parent.absolute()
'''NoneBot2 机器人根目录'''

data_path = root_path / "eve_tool_data"
'''插件数据保存目录'''

plugin_path = Path(__file__).resolve().parent.parent
'''插件目录'''

__all__ = ["root_path", "data_path", "plugin_path", "CommandUsage"]


class CommandUsage(BaseModel):
    """
    插件命令用法信息
    """
    name: Optional[str]
    description: Optional[str]
    usage: Optional[str]
