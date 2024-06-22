import json

from . import remove_color
from ..api import get_zkb_info, get_char_title, get_alliance_name, get_corp_name


class CharacterInfo:
    def __init__(self):
        pass


async def get_character_kb(char_id: str) -> CharacterInfo:
    data = await get_zkb_info(char_id)
    char_info = CharacterInfo()
    char_info.charId = char_id
    char_info.charUrl = f"https://zkillboard.com/api/stats/characterID/{str(char_id)}/"
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
        char_info.sec_status = round(data.get('info').get('secStatus'), 3)
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
        char_info.top_ships = data.get('topLists', [])[3]['values'][0].get('shipName', None)
    except:
        char_info.top_ships = "七天内无活跃km"

    char_info.dangerRatio = data.get('dangerRatio', 0)
    char_info.css = """body {
          background-image: url('https://www.loliapi.com/acg/');
          background-size: cover;
          background-repeat: no-repeat;
          background-position: center;
          margin: auto;
          backdrop-filter: blur(5px);
          }"""

    return char_info


