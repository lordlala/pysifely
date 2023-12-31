import base64
import hashlib
import hmac
import urllib.parse
from typing import Dict, Union, Any

from .const import FORD_APP_SECRET, OLIVE_SIGNING_SECRET, APP_SECRET

def generate_signature(appSecret: str = APP_SECRET, lockKey: str = None):
    raw = appSecret.encode("utf-8")
    key = lockKey.encode('utf-8')
    hashed = hmac.new(key, raw, hashlib.sha1)
    decoded = base64.encodebytes(hashed.digest()).decode('utf-8')
    return base64.encodebytes(hashed.digest()).decode('utf-8')

def olive_create_signature(payload: Union[Dict[Any, Any], str], access_token: str) -> str:
    if isinstance(payload, dict):
        body = ""
        for item in sorted(payload):
            body += item + "=" + str(payload[item]) + "&"

        body = body[:-1]

    else:
        body = payload

    access_key = "{}{}".format(access_token, OLIVE_SIGNING_SECRET)

    secret = hashlib.md5(access_key.encode()).hexdigest()
    return hmac.new(secret.encode(), body.encode(), hashlib.md5).hexdigest()


def ford_create_signature(url_path: str, request_method: str, payload: Dict[Any, Any]) -> str:
    string_buf = request_method + url_path
    for entry in sorted(payload.keys()):
        string_buf += entry + "=" + payload[entry] + "&"

    string_buf = string_buf[:-1]
    string_buf += APP_SECRET
    urlencoded = urllib.parse.quote_plus(string_buf)
    return hashlib.md5(urlencoded.encode()).hexdigest()