import asyncio
import hashlib
import logging
import json
import time
from typing import Dict, Any, Optional

import aiohttp
from aiohttp import TCPConnector, ClientSession, ContentTypeError

from .const import API_KEY, PHONE_ID, APP_NAME, APP_VERSION, SC, SV, PHONE_SYSTEM_TYPE, APP_VER, APP_INFO, CONTENTTYPE, LOGIN_HEADERS, BASE_URL
from .exceptions import UnknownApiError, AccessTokenError, TwoFactorAuthenticationEnabled
from .utils import create_password, check_for_errors_standard

_LOGGER = logging.getLogger(__name__)


class Token:
    # Token is good for 216,000 seconds (60 hours) but 48 hours seems like a reasonable refresh interval
    REFRESH_INTERVAL = 172800

    def __init__(self, access_token, refresh_time: float = None):
        self._access_token: str = access_token
        #self._refresh_token: str = refresh_token
        if refresh_time:
            self._refresh_time: float = refresh_time
        else:
            self._refresh_time: float = time.time() + Token.REFRESH_INTERVAL

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._access_token = access_token
        self._refresh_time = time.time() + Token.REFRESH_INTERVAL

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, refresh_token):
        self._refresh_token = refresh_token

    @property
    def refresh_time(self):
        return self._refresh_time


class PySifelyAuthLib:
    token: Optional[Token] = None
    SANITIZE_FIELDS = ["username", "password", "access_token", "refresh_token"]
    SANITIZE_STRING = "**Sanitized**"

    def __init__(self, username=None, password=None, token: Token = None, token_callback=None):
        self._username = username
        self._password = password
        self.token = token
        self.session_id = ""
        self.verification_id = ""
        self.two_factor_type = None
        self.refresh_lock = asyncio.Lock()
        self.token_callback = token_callback

    @classmethod
    async def create(cls, username=None, password=None, token: Token = None, token_callback=None):
        self = cls(username=username, password=password, token=token, token_callback=token_callback)

        if self._username is None and self._password is None and self.token is None:
            raise AttributeError("Must provide a username, password or token")
        elif self.token is None and self._username is not None and self._password is not None:
            assert self._username != ""
            assert self._password != ""

        return self

    async def get_token_with_username_password(self, username, password) -> Token:
        self._username = username
        self._password = password

        headers = LOGIN_HEADERS

        url = f"{BASE_URL}/user/login"

        hashpass = hashlib.md5(password.encode('utf8')).hexdigest()

        login_payload = {

            'loginType': 1,
            'password': hashpass,
            'platId': 2,
            'uniqueid': '65BDFAFE-56FF-42FE-AAA2-DD8A484CFC58',
            'username': username

        }

        response_json = await self.post(url=url, headers=headers,
                                        data=login_payload)

        if response_json.get('errorCode') is not None:
            _LOGGER.error(f"Unable to login with response from Sifely: {response_json}")
            raise UnknownApiError(response_json)

        self.token = Token(response_json['accessToken'])
        await self.token_callback(self.token)
        return self.token

    async def get_token_with_2fa(self, verification_code) -> Token:
        headers = {
            'Phone-Id': PHONE_ID,
            'User-Agent': APP_INFO,
            'X-API-Key': API_KEY,
        }
        # TOTP Payload
        if self.two_factor_type == "TOTP":
            payload = {
                "email": self._username,
                "password": self._password,
                "mfa_type": "TotpVerificationCode",
                "verification_id": self.verification_id,
                "verification_code": verification_code
            }
        # SMS Payload
        else:
            payload = {
                "email": self._username,
                "password": self._password,
                "mfa_type": "PrimaryPhone",
                "verification_id": self.session_id,
                "verification_code": verification_code
            }

        response_json = await self.post(
            'https://auth-prod.api.wyze.com/user/login',
            headers=headers, json=payload)

        self.token = Token(response_json['access_token'], response_json['refresh_token'])
        await self.token_callback(self.token)
        return self.token

    @property
    def should_refresh(self) -> bool:
        return time.time() >= self.token.refresh_time

    async def refresh_if_should(self):
        if self.should_refresh:
            async with self.refresh_lock:
                if self.should_refresh:
                    _LOGGER.debug("Should refresh. Refreshing...")
                    await self.refresh()

    async def refresh(self) -> None:
        payload = {
            "phone_id": PHONE_ID,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "sc": SC,
            "sv": SV,
            "phone_system_type": PHONE_SYSTEM_TYPE,
            "app_ver": APP_VER,
            "ts": int(time.time()),
            "refresh_token": self.token.refresh_token
        }

        headers = {
            "X-API-Key": API_KEY
        }

        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.post("https://api.wyzecam.com/app/user/refresh_token", headers=headers,
                                                json=payload)
        response_json = await response.json()
        check_for_errors_standard(response_json)

        self.token.access_token = response_json['data']['access_token']
        self.token.refresh_token = response_json['data']['refresh_token']
        await self.token_callback(self.token)

    def sanitize(self, data):
        if data and type(data) is dict:
            # value is unused, but it prevents us from having to split the tuple to check against SANITIZE_FIELDS
            for key, value in data.items():
                if key in self.SANITIZE_FIELDS:
                    data[key] = self.SANITIZE_STRING
        return data

    async def post(self, url, json=None, headers=None, data=None, params=None) -> Dict[Any, Any]:
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.post(url, json=json, headers=headers, data=data)
            # Relocated these below as the sanitization seems to modify the data before it goes to the post.
            _LOGGER.debug("Request:")
            _LOGGER.debug(f"url: {url}")
            _LOGGER.debug(f"json: {self.sanitize(json)}")
            _LOGGER.debug(f"headers: {self.sanitize(headers)}")
            _LOGGER.debug(f"data: {self.sanitize(data)}")
            _LOGGER.debug(f"params: {self.sanitize(params)}")
            # Log the response.json() if it exists, if not log the response.
            try:
                response_json = await response.json()
                _LOGGER.debug(f"Response Json: {response_json}")
            except ContentTypeError:
                _LOGGER.debug(f"Response: {response}")
            return await response.json()

    async def get(self, url, headers=None, params=None) -> Dict[Any, Any]:
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.get(url, params=params, headers=headers)
            return await response.json()

    async def patch(self, url, headers=None, params=None, json=None) -> Dict[Any, Any]:
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.patch(url, headers=headers, params=params, json=json)
            return await response.json()

    async def delete(self, url, headers=None, json=None) -> Dict[Any, Any]:
        async with ClientSession(connector=TCPConnector(ttl_dns_cache=(30 * 60))) as _session:
            response = await _session.delete(url, headers=headers, json=json)
            return await response.json()