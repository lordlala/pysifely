import hashlib
from typing import Dict, Any, List, Optional

from .exceptions import ParameterError, AccessTokenError, UnknownApiError
from .types import ResponseCodes, PropertyIDs, Device, Event


def create_password(password: str) -> str:
    hex1 = hashlib.md5(password.encode()).hexdigest()
    hex2 = hashlib.md5(hex1.encode()).hexdigest()
    return hashlib.md5(hex2.encode()).hexdigest()


def check_for_errors_standard(response_json: Dict[str, Any]) -> None:
    if ('code' in response_json) and (response_json['code']) != ResponseCodes.SUCCESS.value:
        if response_json['code'] == ResponseCodes.PARAMETER_ERROR.value:
            raise ParameterError(response_json)
        elif response_json['code'] == ResponseCodes.ACCESS_TOKEN_ERROR.value:
            raise AccessTokenError
        elif response_json['code'] == ResponseCodes.DEVICE_OFFLINE.value:
            return
        else:
            raise UnknownApiError(response_json)


def check_for_errors_lock(response_json: Dict[str, Any]) -> None:
    if (('ErrNo' in response_json) and (response_json['ErrNo'] != 0)):
        if response_json.get('code') == ResponseCodes.PARAMETER_ERROR.value:
            raise ParameterError
        elif response_json.get('code') == ResponseCodes.ACCESS_TOKEN_ERROR.value:
            raise AccessTokenError
        else:
            raise UnknownApiError(response_json)


def check_for_errors_thermostat(response_json: Dict[Any, Any]) -> None:
    if response_json['code'] != 1:
        raise UnknownApiError(response_json)


def check_for_errors_hms(response_json: Dict[Any, Any]) -> None:
    if response_json['message'] is None:
        raise AccessTokenError


def return_event_for_device(device: Device, events: List[Event]) -> Optional[Event]:
    for event in events:
        if event.device_mac == device.mac:
            return event

    return None


def create_pid_pair(pid_enum: PropertyIDs, value: str) -> Dict[str, str]:
    return {"pid": pid_enum.value, "pvalue": value}

def parse_dict_cookies(cookies):
    result = {}
    for item in cookies.split(';'):
        item = item.strip()
        if not item:
            continue
        if '=' not in item:
            result[item] = None
            continue
        name, value = item.split('=', 1)
        result[name] = value
    return result