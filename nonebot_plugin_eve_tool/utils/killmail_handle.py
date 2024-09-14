import json
import traceback
from decimal import Decimal

from typing import List, Dict, Any, Tuple

from nonebot import logger

from .common import time_difference
from ..model.config import plugin_config
from ..utils import time_change, generate_qrcode
from ..api import get_names, get_region_name, get_constellation_name, get_system_name, get_char_name, get_corp_name, \
    get_alliance_name, get_type_name, get_group_name
from ..database.redis.search import get_names_for_redis
from ..database.redis.RedisArray import RedisArray
from ..model import KillMailDetails, SlotHtml, PersonalLocationFlagEnumV4


RA = RedisArray(plugin_config.eve_redis_url)


async def do_attackers(attackers_data: List[Dict[str, Any]], kill_mail_details: KillMailDetails) -> KillMailDetails:
    flag = 0
    _move_flag = False
    kill_mail_details.Attackers = []
    for attacker in attackers_data:
        final_blow = attacker['final_blow']
        kill_mail_details.attacker_number += 1
        if flag == 0:
            kill_mail_details.TopDamageAttacker = attacker
            flag = 1
            _move_flag = True
        if final_blow:
            kill_mail_details.LastDamageAttacker = attacker
            _move_flag = True

        kill_mail_details.Attackers.append(attacker)

    return kill_mail_details


async def check_and_append_listener(kill_mail_details, entity_id, total_value, value_type, push_list):
    if entity_id:
        redis_key = f"listener:{entity_id}"
        data = await RA.hget('listenerIdx', redis_key)
        if data:
            data = json.loads(data)
            logger.debug(f"订阅流事件：\n{data}")
            for item in data:
                if total_value >= Decimal(item[value_type]):
                    kill_mail_details.listener_ids.append(redis_key)
                    push_list.append(item)
                    logger.debug(f"------------------\n{push_list}")


async def judgment_listener(kill_mail_details):
    high_listener_keys = await RA.hkeys('highListenerIdx')
    total_value = Decimal(kill_mail_details.total_value)
    for key in high_listener_keys:
        data = await RA.hget('highListenerIdx', key)
        item = json.loads(data)
        if total_value >= Decimal(item['high_value_limit']):
            kill_mail_details.high_value_push.append(item)

    victim = kill_mail_details.victim
    last_damage_attacker = kill_mail_details.LastDamageAttacker

    if victim:
        char_id = str(victim.get('character_id'))
        corp_id = str(victim.get('corporation_id'))

        await check_and_append_listener(kill_mail_details, char_id, total_value, 'victim_value_limit',
                                        kill_mail_details.victim_char_push)
        await check_and_append_listener(kill_mail_details, corp_id, total_value, 'victim_value_limit',
                                        kill_mail_details.victim_corp_push)

    if last_damage_attacker:
        char_id = str(last_damage_attacker.get('character_id'))
        corp_id = str(last_damage_attacker.get('corporation_id'))

        await check_and_append_listener(kill_mail_details, char_id, total_value, 'attack_value_limit',
                                        kill_mail_details.attacker_char_push)
        await check_and_append_listener(kill_mail_details, corp_id, total_value, 'attack_value_limit',
                                        kill_mail_details.attacker_corp_push)

    if (kill_mail_details.victim_char_push or
            kill_mail_details.victim_corp_push or
            kill_mail_details.attacker_char_push or
            kill_mail_details.attacker_corp_push or
            kill_mail_details.high_value_push):
        return kill_mail_details
    else:
        return None


async def extract_item_ids(items) -> list[int] | None:
    item_ids = []
    black_list_id = []
    for item in items:
        if item['item_type_id'] in black_list_id:
            logger.debug('物品黑名单')
            return
        item_ids.append(item['item_type_id'])
        if 'items' in item:
            nested_item_ids = await extract_item_ids(item['items'])
            if nested_item_ids:
                item_ids.extend(nested_item_ids)
            else:
                return
    return item_ids


async def generate_equipment_html(items: list) -> str | None:
    item_ids = await extract_item_ids(items)
    if not item_ids:
        return
    unique_item_ids = list(set(item_ids))
    all_item_info = await get_names_for_redis(unique_item_ids)
    item_info_dict = {item_id: name for item_id, name in zip(unique_item_ids, all_item_info)}

    slot_items = {
        'HiSlot': [],
        'MedSlot': [],
        'LoSlot': [],
        'RigSlot': [],
        'SubSystemSlot': [],
        'DroneBay': [],
        'Cargo': [],
        'Other': []
    }

    slot_html_templates = {
        'HiSlot': SlotHtml.hi_slot_html,
        'MedSlot': SlotHtml.mid_slot_html,
        'LoSlot': SlotHtml.low_slot_html,
        'RigSlot': SlotHtml.rig_slot_html,
        'SubSystemSlot': SlotHtml.sub_system_slot_html,
        'DroneBay': SlotHtml.drone_bay_html,
        'Cargo': SlotHtml.cargo_slot_html,
        'Other': SlotHtml.other_slot_html
    }

    for item in items:
        flag_name = PersonalLocationFlagEnumV4.get_name_by_flag(item['flag'])
        item_id = item['item_type_id']
        item_name = item_info_dict.get(item_id, "Unknown Item")

        if "quantity_destroyed" in item:
            drop = False
            item_number = item['quantity_destroyed']
        else:
            drop = True
            item_number = item['quantity_dropped']

        if "items" in item:
            nested_items = item["items"]
            for nested_item in nested_items:
                nested_item_id = nested_item["item_type_id"]
                nested_item_name = item_info_dict.get(nested_item_id, "Unknown Item")

                if "quantity_destroyed" in nested_item:
                    nested_drop = False
                    nested_item_number = nested_item['quantity_destroyed']
                else:
                    nested_drop = True
                    nested_item_number = nested_item['quantity_dropped']

                slot_items[flag_name].append([nested_item_id, nested_item_name, nested_item_number, nested_drop])

        found = False
        for existing_item in slot_items[flag_name]:
            if existing_item[0] == item_id and existing_item[3] == drop:
                existing_item[2] += item_number
                found = True
                break
        if not found:
            slot_items[flag_name].append([item_id, item_name, item_number, drop])

    equipment_html = ""

    for slot_name, items in slot_items.items():
        slot_html = ""
        if items:
            slot_html += slot_html_templates.get(slot_name, "")
        for item_id, item_name, item_number, drop in items:
            slot_html += await generate_slot_template(item_id, item_name, item_number, drop)
        equipment_html += slot_html

    return equipment_html


async def generate_slot_template(item_id, item_name, item_number, drop):
    if drop:
        drop = 'drop'
    else:
        drop = ''
    return f"""
            <div class="clear equip-line {drop}">
                <img src="https://images.evetech.net/types/{item_id}/icon?size=32">
                <span class="chinese">{item_name}</span>
                <span class="pull-right">{item_number}</span>
            </div>
    """


async def generate_attacker_template(attacker, damage_taken, attacker_info, following='following') -> str:
    damage_done = Decimal(attacker.get('damage_done', 0))
    damage_percent = (damage_done / Decimal(damage_taken)) * 100 if damage_taken != 0 else 0
    damage_percent = round(damage_percent, 2)
    damage_done = f"{damage_done:,.0f}"

    attacker_id = attacker.get('character_id', 0)
    ship_type_id = attacker.get('ship_type_id', 0)
    weapon_type_id = attacker.get('weapon_type_id', ship_type_id)

    attacker_name = attacker_info['characters'].get(attacker_id, 'Unknown')
    attacker_corp = attacker_info['corporations'].get(attacker.get('corporation_id', 0), 'Unknown')
    attacker_alliance = attacker_info['alliances'].get(attacker.get('alliance_id', 0), '')

    margin_top = '20' if not attacker_alliance else '5'
    following = '' if following != 'following' else following

    return f"""
        <div class="clear {following}" style="font-weight: 900;">
            <img src="https://images.evetech.net/characters/{attacker_id}/portrait?size=64" />
            <div>
                <img src="https://images.evetech.net/types/{ship_type_id}/icon?size=32" />
                <img class="clear" src="https://images.evetech.net/types/{weapon_type_id}/icon?size=32" />
            </div>
            <div style="font-size: 11px; margin-left: 5px;">
                <span>{attacker_name[:20]}</span>
                <span class="clear" style="margin-top: 1px;">{attacker_corp[:20]}</span>
                <span class="clear" style="margin-top: 0px;">{attacker_alliance[:20]}</span>
                <span class="clear" style="margin-top: {margin_top}px; font-weight: 500;">{damage_done} ({damage_percent}%)</span>
            </div>
        </div>
    """


# 生成攻击者列表
async def generate_attacker_list(attackers, damage_taken, following='following') -> Tuple[str, dict[str, dict]]:
    try:
        for idx, attacker in enumerate(attackers):
            if not isinstance(attacker, dict):
                logger.info(f"Error: Element at index {idx} in attackers is not a dict, it is a {type(attacker)}")

        character_ids = {attacker.get('character_id') for attacker in attackers if
                         isinstance(attacker, dict) and attacker.get('character_id')}
        corporation_ids = {attacker.get('corporation_id') for attacker in attackers if
                           isinstance(attacker, dict) and attacker.get('corporation_id')}
        alliance_ids = {attacker.get('alliance_id') for attacker in attackers if
                        isinstance(attacker, dict) and attacker.get('alliance_id')}

        all_ids = list(character_ids | corporation_ids | alliance_ids)

        all_names = await get_names(all_ids)

        character_names = {item['id']: item['name'] for item in all_names if
                           isinstance(item, dict) and item['category'] == 'character'}
        corporation_names = {item['id']: item['name'] for item in all_names if
                             isinstance(item, dict) and item['category'] == 'corporation'}
        alliance_names = {item['id']: item['name'] for item in all_names if
                          isinstance(item, dict) and item['category'] == 'alliance'}

        attacker_info = {
            'characters': character_names,
            'corporations': corporation_names,
            'alliances': alliance_names
        }

        attacker_list_html = ''
        for idx, attacker in enumerate(attackers):
            if idx == 0 or not isinstance(attacker, dict):
                continue
            attacker_list_html += await generate_attacker_template(attacker, damage_taken, attacker_info, following)

        return attacker_list_html, attacker_info
    except Exception as e:
        logger.error(f"An error occurred:{e}")
        traceback.print_exc()
        return "", {}


async def get_sec_color(sec):
    match str(sec):
        case '1.0':
            return '--10sec-color'
        case '0.9':
            return '--09sec-color'
        case '0.8':
            return '--08sec-color'
        case '0.7':
            return '--07sec-color'
        case '0.6':
            return '--06sec-color'
        case '0.5':
            return '--05sec-color'
        case '0.4':
            return '--04sec-color'
        case '0.3':
            return '--03sec-color'
        case '0.2':
            return '--02sec-color'
        case '0.1':
            return '--01sec-color'
        case _:
            return '--00sec-color'


async def kill_mail_handle(
        message_json,
        judge: bool = True
) -> KillMailDetails | None:
    kill_mail_details = KillMailDetails()
    kill_mail_details.esi_url = message_json['zkb']['esi']
    kill_mail_details.kill_mail_id = message_json['killmail_id']
    kill_mail_details.victim = message_json['victim']
    kill_mail_details.total_value = message_json['zkb']['totalValue']
    kill_mail_details = await do_attackers(
        attackers_data=message_json['attackers'],
        kill_mail_details=kill_mail_details)
    if judge:
        echo = await judgment_listener(kill_mail_details)
        if echo is None:
            return
        kill_mail_details = echo

    kill_mail_details.solar_system, constellation_id, kill_mail_details.sec = await get_system_name(
        message_json['solar_system_id'])
    if constellation_id:
        kill_mail_details.constellation, region_id = await get_constellation_name(int(constellation_id))
        if region_id:
            kill_mail_details.region = await get_region_name(int(region_id))
    kill_mail_details.equipment_html = await generate_equipment_html(message_json['victim']['items'])
    if not kill_mail_details.equipment_html:
        return
    kill_mail_details.damage_taken = message_json['victim']['damage_taken']
    if kill_mail_details.Attackers:
        kill_mail_details.attacker_list_html, kill_mail_details.attacker_info = await generate_attacker_list(
            kill_mail_details.Attackers, kill_mail_details.damage_taken)
    else:
        kill_mail_details.attacker_list_html, kill_mail_details.attacker_number = '', 1

    kill_mail_details.killmail_id = message_json['killmail_id']

    try:
        kill_mail_details.victim_id = message_json['victim']['character_id']
        kill_mail_details.victim_name = await get_char_name(kill_mail_details.victim_id)
    except:
        kill_mail_details.victim_id, kill_mail_details.victim_name = None, None

    try:
        kill_mail_details.victim_corp_id = message_json['victim']['corporation_id']
        kill_mail_details.victim_corp, t = await get_corp_name(kill_mail_details.victim_corp_id)
    except:
        kill_mail_details.victim_corp_id, kill_mail_details.victim_corp = '0', ''
    try:
        kill_mail_details.victim_alliance_id = message_json['victim']['alliance_id']
        kill_mail_details.victim_alliance_name, t = await get_alliance_name(kill_mail_details.victim_alliance_id)
    except:
        kill_mail_details.victim_alliance_id, kill_mail_details.victim_alliance_name = '0', ''

    kill_mail_details.ship_type_id = message_json['victim']['ship_type_id']
    kill_mail_details.ship_type_name, kill_mail_details.ship_group_id = await get_type_name(
        kill_mail_details.ship_type_id)
    kill_mail_details.ship_group_name = await get_group_name(kill_mail_details.ship_group_id)
    kill_mail_details.ship_group_name = f"({kill_mail_details.ship_group_name})"

    if kill_mail_details.victim_name is None:
        kill_mail_details.victim_name = f'{kill_mail_details.ship_type_name} {kill_mail_details.ship_group_name}'
        kill_mail_details.ship_type_name, kill_mail_details.ship_group_name = "", ""

    # 获取星系类
    kill_mail_details.solar_system_id = message_json['solar_system_id']
    kill_mail_details.solar_system, kill_mail_details.constellation_id, kill_mail_details.sec \
        = await get_system_name(kill_mail_details.solar_system_id)
    kill_mail_details.sec = round(kill_mail_details.sec, 1)
    kill_mail_details.sec_color = await get_sec_color(kill_mail_details.sec)
    if kill_mail_details.constellation_id:
        kill_mail_details.constellation, kill_mail_details.region_id \
            = await get_constellation_name(int(kill_mail_details.constellation_id))
    if kill_mail_details.region_id:
        kill_mail_details.region = await get_region_name(int(kill_mail_details.region_id))

    kill_mail_details.qrcode = await generate_qrcode(f'https://zkillboard.com/kill/{kill_mail_details.kill_mail_id}')
    kill_mail_details.drop_value = message_json['zkb']['droppedValue']

    kill_mail_details.time = await time_change(message_json['killmail_time'])
    kill_mail_details.time_difference = time_difference(kill_mail_details.time)

    kill_mail_details.LastDamageAttackerHtml = await generate_attacker_template(
        kill_mail_details.LastDamageAttacker,
        kill_mail_details.damage_taken,
        kill_mail_details.attacker_info,
        following=''
    )
    kill_mail_details.TopDamageAttackerHtml = await generate_attacker_template(
        kill_mail_details.TopDamageAttacker,
        kill_mail_details.damage_taken,
        kill_mail_details.attacker_info,
        following=''
    )

    kill_mail_details.total_value = f"{kill_mail_details.total_value:,.2f}"
    kill_mail_details.drop_value = f"{kill_mail_details.drop_value:,.2f}"
    kill_mail_details.damage_taken = f"{kill_mail_details.damage_taken:,.0f}"

    return kill_mail_details
