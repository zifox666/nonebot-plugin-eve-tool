import yaml

from .common import data_path, plugin_path

file_path = plugin_path / "src" / "other"


class KillMailDetails:
    def __init__(self):
        self.img = None
        self.kill_mail_id = None
        self.TopDamageAttacker = None
        self.Attackers = []
        self.attacker = None
        self.total_value = None
        self.LastDamageAttacker = None
        self.victim = None
        self.listener_ids = []
        self.victim_char_push = []
        self.victim_corp_push = []
        self.attacker_char_push = []
        self.attacker_corp_push = []
        self.high_value_push = []
        self.solar_system = 'unkown'
        self.constellation = 'unkown'
        self.region = 'unkown'
        self.attacker_number = 0
        self.sec = 0.0
        self.title = ''
        self.pic = None


class PersonalLocationFlagEnumV4:
    """Maps location names to IDs."""
    _flag_map = {}

    @classmethod
    def load_from_yaml(cls, yaml_file=file_path / "invFlags.yaml"):
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
            for item in data:
                flag_id = item['flagID']
                flag_name = item['flagName']
                cls._flag_map[flag_id] = flag_name

    @classmethod
    def get_name_by_flag(cls, flag: int) -> str | None:
        flag_name = cls._flag_map.get(flag)
        if flag_name:
            if flag_name.startswith('LoSlot'):
                return 'LoSlot'
            elif flag_name.startswith('MedSlot'):
                return 'MedSlot'
            elif flag_name.startswith('HiSlot'):
                return 'HiSlot'
            elif flag_name.startswith('RigSlot'):
                return 'RigSlot'
            elif flag_name.startswith('SubSystem'):
                return 'SubSystemSlot'
            elif flag_name == 'DroneBay':
                return 'DroneBay'
            elif flag_name == 'Cargo':
                return 'Cargo'
            else:
                return 'Other'
        return None


PersonalLocationFlagEnumV4.load_from_yaml()


class SlotHtml:
    hi_slot_html = f'''
                <div class="clear slot-line chinese">
                    <img src="https://wiki.eveuniversity.org/images/3/3c/Icon_fit_high.png">
                    <span class="chinese">高能量槽</span>
                </div>\n
        '''
    mid_slot_html = f'''
                <div class="clear slot-line chinese" >
                    <img src="https://wiki.eveuniversity.org/images/9/9a/Icon_fit_medium.png" >
                    <span class="chinese">中能量槽</span>
                </div>\n
        '''
    low_slot_html = f'''
                <div class="clear slot-line chinese" >
                    <img src="https://wiki.eveuniversity.org/images/e/e6/Icon_fit_low.png" >
                    <span class="chinese">低能量槽</span>
                </div>\n
        '''
    rig_slot_html = f'''
                <div class="clear slot-line chinese" >
                    <img src="https://wiki.eveuniversity.org/images/e/eb/Icon_fit_rig.png" >
                    <span class="chinese">改装件安装座</span>
                </div>\n
        '''
    sub_system_slot_html = f'''
            <div class="clear slot-line chinese" >
                <img src="https://wiki.eveuniversity.org/images/e/e3/EVE_SubIcon.png" >
                <span class="chinese">子系统槽位</span>
            </div>\n
        '''
    drone_bay_html = f'''
            <div class="clear slot-line chinese" >
                <img src="https://wiki.eveuniversity.org/images/thumb/0/07/Icon_fit_drone.png/48px-Icon_fit_drone.png" >
                <span class="chinese">无人机挂仓</span>
            </div>\n
        '''
    cargo_slot_html = f'''
            <div class="clear slot-line chinese" >
                <img src="https://wiki.eveuniversity.org/images/thumb/8/82/Icon_capacity.png/48px-Icon_capacity.png" >
                <span class="chinese">货柜仓</span>
            </div>\n
        '''
    other_slot_html = f'''
            <div class="clear slot-line chinese" >
                <img src="https://wiki.eveuniversity.org/images/thumb/8/82/Icon_capacity.png/48px-Icon_capacity.png" >
                Other
            </div>\n
        '''
