from enum import Enum
from typing import Union, List, Dict, Any


class Group:
    groupId: str
    groupName: str

    def __init__(self, dictionary: Dict[Any, Any]):
        for k, v in dictionary.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return "<Group: {}, {}>".format(self.groupId, self.groupName)


class DeviceTypes(Enum):
    LIGHT = "Light"
    PLUG = "Plug"
    OUTDOOR_PLUG = "OutdoorPlug"
    MESH_LIGHT = "MeshLight"
    CAMERA = "Camera"
    CHIME_SENSOR = "ChimeSensor"
    CONTACT_SENSOR = "ContactSensor"
    MOTION_SENSOR = "MotionSensor"
    WRIST = "Wrist"
    BASE_STATION = "BaseStation"
    SCALE = "WyzeScale"
    LOCK = "Lock"
    GATEWAY = "gateway"
    COMMON = "Common"
    VACUUM = "JA_RO2"
    HEADPHONES = "JA.SC"
    THERMOSTAT = "Thermostat"
    GATEWAY_V2 = "GateWay"
    UNKNOWN = "Unknown"
    SENSE_V2_GATEWAY = "S1Gateway"
    KEYPAD = "Keypad"


class Device:
    product_type: str
    product_model: str
    mac: str
    nickname: str
    device_params: Dict[str, Any]
    raw_dict: Dict[str, Any]

    def __init__(self, dictionary: Dict[Any, Any]):
        self.available = False

        self.raw_dict = dictionary
        for k, v in dictionary.items():
            setattr(self, k, v)

    @property
    def type(self) -> DeviceTypes:
        try:
            return DeviceTypes(self.product_type)
        except ValueError:
            return DeviceTypes.UNKNOWN

    def __repr__(self) -> str:
        return "<Device: {}, {}>".format(DeviceTypes(self.product_type), self.mac)


class Sensor(Device):
    def __init__(self, dictionary: Dict[Any, Any]):
        super().__init__(dictionary)

    @property
    def activity_detected(self) -> int:
        if self.type is DeviceTypes.CONTACT_SENSOR:
            return int(self.device_params['open_close_state'])
        elif self.type is DeviceTypes.MOTION_SENSOR:
            return int(self.device_params['motion_state'])
        else:
            raise AssertionError("Device must be of type CONTACT_SENSOR or MOTION_SENSOR")

    @property
    def is_low_battery(self) -> int:
        return int(self.device_params['is_low_battery'])


class PropertyIDs(Enum):
    NOTIFICATION = "P1"
    ON = "P3"
    AVAILABLE = "P5"
    BRIGHTNESS = "P1501"  # From 0-100
    COLOR_TEMP = "P1502"  # In Kelvin
    COLOR = "P1507"  # As a hex string RrGgBb
    DOOR_OPEN = "P2001"  # 0 if the door is closed
    CONTACT_STATE = "P1301"
    MOTION_STATE = "P1302"


class ThermostatProps(Enum):
    APP_VERSION = "app_version"
    IOT_STATE = "iot_state"  # Connection state: connected, disconnected
    SETUP_STATE = "setup_state"
    CURRENT_SCENARIO = "current_scenario"  # home, away
    PROTECT_TIME = "protect_time"
    COOL_SP = "cool_sp"  # Cool stop point
    EMHEAT = "emheat"
    TIME2TEMP_VAL = "time2temp_val"
    SAVE_COMFORT_BALANCE = "save_comfort_balance"  # savings, comfort, or balance value
    QUERY_SCHEDULE = "query_schedule"
    WORKING_STATE = "working_state"  # idle, etc.
    WIRING_LOGIC_ID = "wiring_logic_id"
    W_CITY_ID = "w_city_id"
    FAN_MODE = "fan_mode"  # auto, on, off
    TEMPERATURE = "temperature"  # current temp
    HUMIDITY = "humidity"  # current humidity
    KID_LOCK = "kid_lock"
    CALIBRATE_HUMIDITY = "calibrate_humidity"
    HEAT_SP = "heat_sp"  # heat stop point
    CALIBRATE_TEMPERATURE = "calibrate_temperature"
    MODE_SYS = "mode_sys"  # auto, heat, cool
    W_LAT = "w_lat"
    CONFIG_SCENARIO = "config_scenario"
    FANCIRC_TIME = "fancirc_time"
    W_LON = "w_lon"
    DEV_HOLD = "dev_hold"
    TEMP_UNIT = "temp_unit"
    ASW_HOLD = "asw_hold"


class ResponseCodes(Enum):
    SUCCESS = 200
    PARAMETER_ERROR = "1001"
    ACCESS_TOKEN_ERROR = "2001"
    DEVICE_OFFLINE = '3019'


class ResponseCodesLock(Enum):
    SUCCESS = 0


class File:
    file_id: str
    type: Union[int, str]
    url: str
    status: int
    en_algorithm: int
    en_password: str
    is_ai: int
    ai_tag_list: List[Any]
    ai_url: str
    file_params: Dict[Any, Any]

    def __init__(self, dictionary: Dict[Any, Any]):
        for k, v in dictionary.items():
            setattr(self, k, v)

        if self.type == 1:
            self.type = "Image"
        else:
            self.type = "Video"


class Event:
    event_id: str
    device_mac: str
    device_model: str
    event_category: int
    event_value: str
    event_ts: int
    event_ack_result: int
    is_feedback_correct: int
    is_feedback_face: int
    is_feedback_person: int
    file_list: List[Dict[Any, Any]]
    event_params: Dict[Any, Any]
    recognized_instance_list: List[Any]
    tag_list: List[Any]
    read_state: int

    def __init__(self, dictionary: Dict[Any, Any]):
        for k, v in dictionary.items():
            setattr(self, k, v)


class HMSStatus(Enum):
    DISARMED = 'disarmed'
    HOME = 'home'
    AWAY = 'away'

class MacTypes(Enum):
    locks = 'lockMac'
    gateways = 'gatewayMac'

class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """
    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]