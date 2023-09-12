import uuid

# Here is where all the *magic* lives
PHONE_SYSTEM_TYPE = "1"
APP_ID = "facccadbaa134cf196545d6299a0452c"
APP_SECRET = "a1a22e33cff96a26056ca552c63d992d"
API_KEY = "WMXHYf79Nr5gIlt3r0r7p9Tcw5bvs6BB4U8O8nGJ"
APP_VERSION = "2.18.43"
APP_VER = ""
APP_NAME = ""
BASE_URL = "https://servlet.ttlock.com"
PHONE_ID = str(uuid.uuid4())
APP_INFO = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188'
CONTENTTYPE = 'application/json;charset=UTF-8'
SC = "9f275790cab94a72bd206c8876429f3c"
SV = "9d74946e652647e9b6c9d59326aef104"
UNIQUE_ID = "65BDFAFE-56FF-42FE-AAA2-DD8A484CFC58"

#Request Constants
LOGIN_HEADERS = {
    'Host': 'servlet.ttlock.com',
    'Accept': '*/*',
    'Expires': '-1',
    'appId': APP_ID,
    'appSecret': APP_SECRET,
    'platform': 'iOS-2.3.0',
    'User-Agent': 'sifely/2.3.0 (iPhone; iOS 16.6.1; Scale/3.00)',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Version': '2.2',
    'packageName': 'com.sifely.smartlock',
    'Cookie': 'JSESSIONID=00AA4FF11F48FDD683B02285894706F8',
    'language': 'en',
    'Accept-Language': "en;q=1",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache,no-store",
    "Accept-Encoding": "gzip, deflate, br"
}

USER_INFO = {
    "deviceSystemVersion":"16.6.1",
    "language":"en",
    "packageName":"com.sifely.smartlock",
    "appVersion":"2.2.0",
    "deviceName":"iPhone13,2"
}

# Crypto secrets
OLIVE_SIGNING_SECRET = 'wyze_app_secret_key_132'  # Required for the thermostat
OLIVE_APP_ID = '9319141212m2ik'  # Required for the thermostat
FORD_APP_KEY = "275965684684dbdaf29a0ed9"  # Required for the locks
FORD_APP_SECRET = "4deekof1ba311c5c33a9cb8e12787e8c"  # Required for the locks