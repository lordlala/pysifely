import json, requests
import time
from typing import List, Tuple, Any, Dict, Optional

from ..const import PHONE_SYSTEM_TYPE, APP_ID, APP_SECRET, APP_VERSION, APP_VER, BASE_URL, PHONE_ID, APP_NAME, LOGIN_HEADERS, OLIVE_APP_ID, APP_INFO, SC, SV, UNIQUE_ID, USER_INFO
from ..crypto import olive_create_signature
from ..payload_factory import olive_create_hms_patch_payload, olive_create_hms_payload, \
    olive_create_hms_get_payload, ford_create_payload, olive_create_get_payload, olive_create_post_payload, \
    olive_create_user_info_payload
from ..types import PropertyIDs, Device, Group
from ..utils import check_for_errors_standard, check_for_errors_hms, check_for_errors_lock, \
    check_for_errors_thermostat
from ..sifely_auth_lib import PySifelyAuthLib

class BaseService:
    _devices: Optional[List[Device]] = None
    _lock_groups: Optional[List[Group]] = None
    _user_info = None
    _headers = None

    def __init__(self, auth_lib: PySifelyAuthLib):
        try:
            if auth_lib.should_refresh == "false":
                self._auth_lib = auth_lib
        except Exception:
            self._auth_lib = auth_lib._auth_lib

    async def set_push_info(self, on: bool) -> None:
        await self._auth_lib.refresh_if_should()

        url = "https://api.wyzecam.com/app/user/set_push_info"
        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "push_switch": "1" if on else "2",
            "sc": SC,
            "ts": int(time.time()),
            "sv": SV,
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        response_json = await self._auth_lib.post(url, json=payload)

        check_for_errors_standard(response_json)

    async def get_user_profile(self) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

        headers = self._auth_lib.token.headers

        url = f"{BASE_URL}/user/getUserInfo"

        data = {
            'operatorUid': f"{self._auth_lib.token.uid}"
        }

        response_json = await self._auth_lib.post(url, headers=headers, data=data)

        self._user_info = response_json

        return response_json

    async def get_object_list(self) -> List[Device]:
        await self._auth_lib.refresh_if_should()

        devices = []

        devices += await self._get_gateway_list(Device)

        devices += await self._get_sync_data(Device)

        return devices

    async def _get_property_list(self, device: Device) -> List[Tuple[PropertyIDs, Any]]:
        """
        Wraps the api.wyzecam.com/app/v2/device/get_property_list endpoint

        :param device: Device to get properties for
        :return: List of PropertyIDs and values
        """

        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "device_model": device.product_model,
            "device_mac": device.mac,
            "target_pid_list": []
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/get_property_list",
                                                  json=payload)

        check_for_errors_standard(response_json)
        properties = response_json['data']['property_list']

        property_list = []
        for property in properties:
            try:
                property_id = PropertyIDs(property['pid'])
                property_list.append((
                    property_id,
                    property['value']
                ))
            except ValueError:
                pass

        return property_list

    async def _set_property_list(self, device: Device, plist: List[Dict[str, str]]) -> None:
        """
        Wraps the api.wyzecam.com/app/v2/device/set_property_list endpoint

        :param device: The device for which to set the property(ies)
        :param plist: A list of properties [{"pid": pid, "pvalue": pvalue},...]
        :return:
        """

        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "property_list": plist,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/set_property_list",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _run_action_list(self, device: Device, plist: List[Dict[Any, Any]]) -> None:
        """
        Wraps the api.wyzecam.com/app/v2/auto/run_action_list endpoint

        :param device: The device for which to run the action list
        :param plist: A list of properties [{"pid": pid, "pvalue": pvalue},...]
        """
        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "action_list": [
                {
                    "instance_id": device.mac,
                    "action_params": {
                        "list": [
                            {
                                "mac": device.mac,
                                "plist": plist
                            }
                        ]
                    },
                    "provider_key": device.product_model,
                    "action_key": "set_mesh_property"
                }
            ]
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/auto/run_action_list",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _get_event_list(self, count: int) -> Dict[Any, Any]:
        """
        Wraps the api.wyzecam.com/app/v2/device/get_event_list endpoint

        :param count: Number of events to gather
        :return: Response from the server
        """

        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_id": PHONE_ID,
            "begin_time": int((time.time() - (60 * 60)) * 1000),
            "event_type": "",
            "app_name": APP_NAME,
            "count": count,
            "app_version": APP_VERSION,
            "order_by": 2,
            "event_value_list": [
                "1",
                "13",
                "10",
                "12"
            ],
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "device_mac_list": [],
            "event_tag_list": [],
            "sv": "782ced6909a44d92a1f70d582bbe88be",
            "end_time": int(time.time() * 1000),
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_ver": APP_VER,
            "ts": 1623612037763,
            "device_mac": "",
            "access_token": self._auth_lib.token.access_token
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/get_event_list",
                                                  json=payload)

        check_for_errors_standard(response_json)
        return response_json

    async def _run_action(self, device: Device, action: str) -> None:
        """
        Wraps the api.wyzecam.com/app/v2/auto/run_action endpoint

        :param device: The device for which to run the action
        :param action: The action to run
        :return:
        """

        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "provider_key": device.product_model,
            "instance_id": device.mac,
            "action_key": action,
            "action_params": {},
            "custom_string": "",
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/auto/run_action",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _set_property(self, device: Device, pid: str, pvalue: str) -> None:
        """
        Wraps the api.wyzecam.com/app/v2/device/set_property endpoint

        :param device: The device for which to set the property
        :param pid: The property id
        :param pvalue: The property value
        """
        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "sv": "9d74946e652647e9b6c9d59326aef104",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "pvalue": pvalue,
            "pid": pid,
            "device_model": device.product_model,
            "device_mac": device.mac
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/set_property",
                                                  json=payload)

        check_for_errors_standard(response_json)

    async def _monitoring_profile_active(self, hms_id: str, home: int, away: int) -> None:
        """
        Wraps the hms.api.wyze.com/api/v1/monitoring/v1/profile/active endpoint

        :param hms_id: The hms id
        :param home: 1 for home 0 for not
        :param away: 1 for away 0 for not
        :return:
        """
        await self._auth_lib.refresh_if_should()

        url = "https://hms.api.wyze.com/api/v1/monitoring/v1/profile/active"
        query = olive_create_hms_patch_payload(hms_id)
        signature = olive_create_signature(query, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature,
            'Authorization': self._auth_lib.token.access_token
        }
        payload = [
            {
                "state": "home",
                "active": home
            },
            {
                "state": "away",
                "active": away
            }
        ]
        response_json = await self._auth_lib.patch(url, headers=headers, params=query, json=payload)
        check_for_errors_hms(response_json)

    async def _get_plan_binding_list_by_user(self) -> Dict[Any, Any]:
        """
        Wraps the wyze-membership-service.wyzecam.com/platform/v2/membership/get_plan_binding_list_by_user endpoint

        # :return: The response to gathering the plan for the current user
        """

        if self._auth_lib.should_refresh:
            await self._auth_lib.refresh()

        url = "https://wyze-membership-service.wyzecam.com/platform/v2/membership/get_plan_binding_list_by_user"
        payload = olive_create_hms_payload()
        signature = olive_create_signature(payload, self._auth_lib.token.access_token)
        headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature
        }

        response_json = await self._auth_lib.get(url, headers=headers, params=payload)
        check_for_errors_hms(response_json)
        return response_json

    async def _disable_reme_alarm(self, hms_id: str) -> None:
        """
        Wraps the hms.api.wyze.com/api/v1/reme-alarm endpoint

        :param hms_id: The hms_id for the account
        """
        await self._auth_lib.refresh_if_should()

        url = "https://hms.api.wyze.com/api/v1/reme-alarm"
        payload = {
            "hms_id": hms_id,
            "remediation_id": "emergency"
        }
        headers = {
            "Authorization": self._auth_lib.token.access_token
        }

        response_json = await self._auth_lib.delete(url, headers=headers, json=payload)

        check_for_errors_hms(response_json)

    async def _monitoring_profile_state_status(self, hms_id: str) -> Dict[Any, Any]:
        """
        Wraps the hms.api.wyze.com/api/v1/monitoring/v1/profile/state-status endpoint

        :param hms_id: The hms_id
        :return: The response that includes the status
        """
        if self._auth_lib.should_refresh:
            await self._auth_lib.refresh()

        url = "https://hms.api.wyze.com/api/v1/monitoring/v1/profile/state-status"
        query = olive_create_hms_get_payload(hms_id)
        signature = olive_create_signature(query, self._auth_lib.token.access_token)
        headers = {
            'User-Agent': 'myapp',
            'appid': OLIVE_APP_ID,
            'appinfo': APP_INFO,
            'phoneid': PHONE_ID,
            'access_token': self._auth_lib.token.access_token,
            'signature2': signature,
            'Authorization': self._auth_lib.token.access_token,
            'Content-Type': "application/json"
        }

        response_json = await self._auth_lib.get(url, headers=headers, params=query)

        check_for_errors_hms(response_json)
        return response_json

    async def _get_gateway_list(self, device: Device):

        await self._auth_lib.refresh_if_should()

        headers = self._auth_lib.token.headers

        await self._auth_lib.refresh_if_should()

        payload = {
            "d" : f"{round(time.time())}",
            "pageNo" : "1",
            "pageSize" : "10",
            "operatorUid": f"{self._auth_lib.token.uid}"
        }

        url = f"{BASE_URL}/plug/list"

        response_json = await self._auth_lib.post(url=url,
                                                  headers=headers, data=payload)

        check_for_errors_standard(response_json)

        if len(response_json["list"]) != 0:

            total = response_json["total"]

            for index in range(total):
                response_json["list"][index]['product_type'] = "gateway"
                response_json["list"][index]['mac'] = response_json["list"][index]['networkMac']
                index = index + 1

        BaseService._devices = [Device(device) for device in response_json['list']]

        return BaseService._devices

    async def _get_gateway_lock_list(self, device: Device, gateway: Device):
        await self._auth_lib.refresh_if_should()

        headers = self._auth_lib.token.headers

        payload = {
            "d" : f"{round(time.time())}",
            "pageNo" : "1",
            "operatorUid": f"{self._auth_lib.token.uid}",
            "plugId": f"{gateway.plugId}"

        }

        url = f"{BASE_URL}/plug/getLockList"

        response_json = await self._auth_lib.post(url=url,
                                                  headers=headers, data=payload)

        check_for_errors_standard(response_json)

        if len(response_json["list"]) != 0:

            try:
                total = response_json["total"]
            except:
                total = len(response_json['list'])

            for index in range(total):
                response_json["list"][index]['product_type'] = "Lock"
                response_json["list"][index]['mac'] = response_json["list"][index]['lockMac']
                index = index + 1

        BaseService._devices = [Device(device) for device in response_json['list']]

        return BaseService._devices

    async def _get_lock_groups(self, device: Device):
        devices = []

        await self._auth_lib.refresh_if_should()

        headers = {
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Accept-Language' : 'en-US,en;q=0.9',
            'Authorization': "Bearer {}".format(self._auth_lib.token.access_token)
        }

        response_json = await self._auth_lib.post("https://pro-server.sifely.com/v3/lock/getGroupByForLock",
                                                  headers=headers)

        check_for_errors_standard(response_json)

        if len(response_json["data"]["list"]) != 0:

            total = len(response_json["data"]['list'])

            for index in range(total):
                response_json["data"]["list"][index]['product_type'] = "Lock"
                try:
                    response_json["data"]["list"][index]['mac'] = response_json["data"]["list"][index]['lockMac']
                except:
                    pass
                devices.append(Group(response_json["data"]["list"][index]))
                index = index + 1

        return devices

    async def _get_lock_by_groupid(self, device: Device, groupid = 0):
        devices = []

        await self._auth_lib.refresh_if_should()

        headers = {
            'Accept' : 'application/json, text/plain, */*',
            'Accept-Encoding' : 'gzip, deflate, br',
            'Accept-Language' : 'en-US,en;q=0.9',
            'Authorization': "Bearer {}".format(self._auth_lib.token.access_token)
        }

        payload = {
            'groupId' : groupid,
            'pageNo' : '1',
            'pageSize' : '10'
        }

        response_json = await self._auth_lib.post("https://pro-server.sifely.com/v3/lock/getLockByGroupId",
                                                  headers=headers, data=payload)

        check_for_errors_standard(response_json)

        if len(response_json["data"]["list"]) != 0:

            total = response_json["data"]["total"]

            for index in range(total):
                response_json["data"]["list"][index]['product_type'] = "Lock"
                response_json["data"]["list"][index]['mac'] = response_json["data"]["list"][index]['lockMac']
                devices.append(response_json["data"]["list"][index])
                index = index + 1

        return devices

    async def _get_lock_list(self, device: Device):
        devices = []

        await self._auth_lib.refresh_if_should()

        headers = LOGIN_HEADERS

        payload = {
            "clientId": f"{APP_ID}",
            "accessToken": f"{self._auth_lib.token.access_token}",
            #'Authorization': "Bearer {}".format(self._auth_lib.token.access_token),
            'pageNo' : '1',
            'pageSize' : '10',
            "date": f"{round(time.time())}"
        }

        url = "https://pro-server.sifely.com/v3/lock/list"

        response_json = await self._auth_lib.post(url=url,
                                                  headers=headers, data=payload)

        return response_json

    async def _lock_control(self, device: Device, action: str) -> None:
        await self._auth_lib.refresh_if_should()

        headers = self._auth_lib.token.headers
        headers['Cookie'] = "JSESSIONID=066E60742CE00605710AEE7EA314EF1E"
        headers["signature"] = "wtCR4A9Ce7rrvbSz1+Wpvn5fFs2pKOkBHGBc5khTMKM="

        payload = {
            "d": device.date,
            "keyId": device.keyId,
            "lockId": device.lockId,
            "operatorUid": device.uid,
        }

        payload = {
            "clientId": f"{APP_ID}",
            "accessToken": f"{self._auth_lib.token.access_token}",
            "lockId": device.lockId,
            "date": round(time.time())
        }

        url = f"{BASE_URL}/lock/room/lock"

        response_json = await self._auth_lib.post(url, headers=headers, data=payload)

        check_for_errors_lock(response_json)

        return(response_json)

    async def _get_device_info(self, device: Device) -> Dict[Any, Any]:
        await self._auth_lib.refresh_if_should()

        payload = {
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_version": APP_VERSION,
            "app_ver": APP_VER,
            "device_mac": device.mac,
            "sc": "9f275790cab94a72bd206c8876429f3c",
            "ts": int(time.time()),
            "device_model": device.product_model,
            "sv": "c86fa16fc99d4d6580f82ef3b942e586",
            "access_token": self._auth_lib.token.access_token,
            "phone_id": PHONE_ID,
            "app_name": APP_NAME
        }

        response_json = await self._auth_lib.post("https://api.wyzecam.com/app/v2/device/get_device_Info",
                                                  json=payload)

        check_for_errors_standard(response_json)

        return response_json

    async def _get_sync_data(self, device: Device):
        await self._auth_lib.refresh_if_should()

        headers = self._auth_lib.token.headers

        headers.pop("Cookie")

        url = f"{BASE_URL}/check/syncDataPage"

        userinfo = USER_INFO

        data = {
            "lastUpdateDate": "1694032433864",
            "operatorUid": f"{self._auth_lib.token.uid}",
            "pageNo": "1",
            "uniqueid": f"{UNIQUE_ID}",
            "userInfo": json.dumps(userinfo, separators=(',', ':'))
        }

        response_json = await self._auth_lib.post(url, headers=headers, data=data)
        BaseService._user_info = response_json['userSettings']
        BaseService._devices = [Device(device) for device in response_json['keyInfos']]
        BaseService._lock_groups = [Group(group) for group in response_json['keyGroups']]

        return BaseService._devices