#region Imports
from .version import version as __version__

import logging
import time
#endregion Imports

#region begin
_LOGGER = logging.getLogger(__name__)

__author__ = 'Jason Adams'
__license__ = 'MIT'
#endregion begin

#  Copyright (c) 2021. Mulliken, LLC - All Rights Reserved
#  You may use, distribute and modify this code under the terms
#  of the attached license. You should have received a copy of
#  the license with this file. If not, please write to:
#  joshua@mulliken.net to receive a copy
import logging
import time
from typing import Dict, Any, List, Optional, Set
from inspect import iscoroutinefunction

from .const import PHONE_SYSTEM_TYPE, APP_VERSION, SC, APP_VER, SV, PHONE_ID, APP_NAME, OLIVE_APP_ID, APP_INFO
from .crypto import olive_create_signature
from .payload_factory import olive_create_user_info_payload
from .services.base_service import BaseService
from .services.gateway_service import GatewayService
from .services.lock_service import LockService
from .types import MacTypes
#from wyzeapy.services.hms_service import HMSService
#from wyzeapy.services.lock_service import LockService
#from wyzeapy.services.sensor_service import SensorService
#from wyzeapy.services.switch_service import SwitchService
#from wyzeapy.services.thermostat_service import ThermostatService
from .utils import check_for_errors_standard
from .sifely_auth_lib import PySifelyAuthLib, Token
from .exceptions import TwoFactorAuthenticationEnabled

_LOGGER = logging.getLogger(__name__)


class Pysifely:
    """A module to assist developers in interacting with the Wyze service"""
    #_client: Client
    _auth_lib: PySifelyAuthLib

    def __init__(self):
        self._bulb_service = None
        self._switch_service = None
        self._camera_service = None
        self._thermostat_service = None
        self._hms_service = None
        self._lock_service = None
        self._sensor_service = None
        self._email = None
        self._password = None
        self._service: Optional[BaseService] = None
        self._token_callbacks: List[function] = []

    @classmethod
    async def create(cls):
        """
        Creates the Pysifely class in an async way. Although this is not currently utilized

        :return: An instance of the Wyzeapy class
        """
        self = cls()
        return self

    async def login(self, email, password, token: Token = None):
        """
        Logs the user in and retrieves the users token

        :param email: Users email
        :param password: Users password
        :param token: Users existing token from a previous session

        :raises:
            TwoFactorAuthenticationEnabled: indicates that the account has 2fa enabled
        """

        self._email = email
        self._password = password
        try:
            if token:
                # User token supplied, lets go ahead and use it and refresh the access token if needed.
                self._auth_lib = await PySifelyAuthLib.create(email, password, token, token_callback=self.execute_token_callbacks)
                await self._auth_lib.refresh_if_should()
                self._service = PySifelyAuthLib(self._auth_lib)
            else:
                self._auth_lib = await PySifelyAuthLib.create(email, password, token_callback=self.execute_token_callbacks)
                await self._auth_lib.get_token_with_username_password(email, password)
                self._service = BaseService(self._auth_lib)
        except TwoFactorAuthenticationEnabled as error:
            raise error

    async def login_with_2fa(self, verification_code) -> Token:
        """
        Logs the user in and retrieves the users token

        :param verification_code: Users 2fa verification code

        """

        _LOGGER.debug(f"Verification Code: {verification_code}")

        await self._auth_lib.get_token_with_2fa(verification_code)
        self._service = BaseService(self._auth_lib)
        return self._auth_lib.token

    async def execute_token_callbacks(self, token: Token):
        """
        Sends the token to the registered callback functions.

        :param token: Users token object

        """
        for callback in self._token_callbacks:
            if iscoroutinefunction(callback):
                await callback(token)
            else:
                callback(token)

    def register_for_token_callback(self, callback_function):
        """
        Register a callback to be called whenever the user's token is modified

        :param callback_function: A callback function which expects a token object

        """
        self._token_callbacks.append(callback_function)

    def unregister_for_token_callback(self, callback_function):
        """
        Register a callback to be called whenever the user's token is modified

        :param callback_function: A callback function which expects a token object

        """
        self._token_callbacks.remove(callback_function)

    @property
    async def unique_device_ids(self) -> Set[str]:
        """
        Returns a list of all device ids known to the server
        :return: A set containing the unique device ids
        """

        devices = await self._service.get_object_list()
        device_ids = set()
        for device in devices:
            device_ids.add(device.mac)

        return device_ids

    @property
    async def notifications_are_on(self) -> bool:
        """
        Reports the status of the notifications

        :return: True if the notifications are enabled
        """

        response_json = await self._service.get_user_profile()
        return response_json['data']['notification']

    async def enable_notifications(self):
        """Enables notifications on the account"""

        await self._service.set_push_info(True)

    async def disable_notifications(self):
        """Disables notifications on the account"""

        await self._service.set_push_info(False)

    @classmethod
    async def valid_login(cls, email: str, password: str) -> bool:
        """
        Checks to see if a username and password return a valid login

        :param email: The users email
        :param password: The users password
        :return: True if the account can connect
        """

        self = cls()
        await self.login(email, password)
        return not self._auth_lib.should_refresh

