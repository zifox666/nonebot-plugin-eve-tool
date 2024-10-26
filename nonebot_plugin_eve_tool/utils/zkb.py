import json
from datetime import datetime
from typing import Dict, Any, Tuple

from urllib3.util import Url

from . import remove_color, get_background_image
from ..api import get_zkb_info, get_char_title, get_alliance_name, get_corp_name


class CharacterInfo:
    def __init__(self):
        pass


async def get_character_kb(char_id: str) -> tuple[dict[str | Any, str | None | Any], str]:
    data = await get_zkb_info(char_id)
    char_info = CharacterInfo()
    char_info.charId = char_id
    char_info.charUrl = f"https://zkillboard.com/api/stats/characterID/{str(char_id)}/"

    char_info.charBirthday = data.get("info").get("birthday", "1999-01-01T00:00:00Z")
    dt = datetime.strptime(char_info.charBirthday, "%Y-%m-%dT%H:%M:%SZ")
    char_info.charBirthday = dt.strftime("%Y-%m-%d")

    char_info.charName = data.get('info').get('name', 0)
    char_info.iskDestroyed = data.get('iskDestroyed', 0)
    char_info.iskDestroyed = f"{char_info.iskDestroyed:,.2f}"
    char_info.shipsDestroyed = data.get('shipsDestroyed', 0)
    char_info.pointsDestroyed = data.get('pointsDestroyed', 0)
    char_info.shipsLost = data.get('shipsLost', 0)
    char_info.iskLost = data.get('iskLost', 0)
    char_info.iskLost = f"{char_info.iskLost:,.2f}"
    char_info.pointsLost = data.get('pointsLost', 0)
    char_info.soloKills = data.get('soloKills', 0)
    char_info.gangRatio = data.get('gangRatio', 0)
    char_info.shipsLost = data.get('shipsLost', 0)
    char_info.shipsDestroyed = data.get('shipsDestroyed', 0)
    char_info.qrCode = f"https://www.olzz.com/qr/?text=https://zkillboard.com/character/{char_id}/&size=80"
    try:
        char_info.pointb = round(char_info.pointsDestroyed / char_info.shipsDestroyed, 2)
    except:
        char_info.pointb = "0"
    alliance_id = data.get('info').get('allianceID')
    corporation_id = data.get('info').get('corporationID')
    try:
        char_info.sec_status = round(data.get('info').get('secStatus'), 2)
    except:
        char_info.sec_status = "未知"
    char_info.corporation_name, char_info.corporation_ticker = await get_corp_name(corporation_id)
    char_info.alliance_name, char_info.alliance_ticker = await get_alliance_name(alliance_id)
    char_info.nick_title = await get_char_title(int(char_id))
    if char_info.nick_title:
        char_info.nick_title = char_info.nick_title
    else:
        char_info.nick_title = "无头衔"

    try:
        values = data.get('topLists', [])[3].get('values', [])
        char_info.top_ships = values[:3]
        char_info.kills_all = sum(ship.get('kills', 0) for ship in values[:3])
    except:
        char_info.top_ships = None
        char_info.kills_all = 0

    char_info.dangerRatio = data.get('dangerRatio', 0)
    char_info.css = """body {
          background-image: url('https://www.loliapi.com/acg/');
          background-size: cover;
          background-repeat: no-repeat;
          background-position: center;
          margin: auto;
          backdrop-filter: blur(5px);
          }"""

    char_json = {
        "avatar": f"https://images.evetech.net/characters/{char_info.charId}/portrait?size=128",
        "name": char_info.charName,
        "title": char_info.nick_title,
        "org": f"[{char_info.alliance_ticker}]{char_info.corporation_name}",
        "birthday": char_info.charBirthday,
        "sec": char_info.sec_status,
        "topShips": char_info.top_ships,
        "pointb": char_info.pointb,
        "shipDestroyed": char_info.shipsDestroyed,
        "iskDestroyed": char_info.iskDestroyed,
        "shipsLost": char_info.shipsLost,
        "iskLost": char_info.iskLost,
        "background_image": await get_background_image(),
        "dangerRatio": char_info.dangerRatio,
        "gangRatio": char_info.gangRatio,
        "solo": char_info.soloKills,
        "killsAll": char_info.kills_all

    }

    return char_json, char_id




