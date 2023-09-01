from typing import Dict, Any


class ActionNotSupported(Exception):
    def __init__(self, device_type: str):
        message = "The action specified is not supported by device type: {}".format(device_type)

        super().__init__(message)


class ParameterError(Exception):
    pass


class AccessTokenError(Exception):
    pass


class LoginError(Exception):
    pass


class UnknownApiError(Exception):
    def __init__(self, response_json: Dict[str, Any]):
        super(UnknownApiError, self).__init__(str(response_json))


class TwoFactorAuthenticationEnabled(Exception):
    pass
