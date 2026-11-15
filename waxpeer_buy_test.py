import os
import urllib.parse
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
TRADE_URL = key("STEAM_TRADE_URL")
TOKEN = urllib.parse.parse_qs(urllib.parse.urlparse(TRADE_URL).query).get("token", [""])[0]

ITEM_ID = "37280635383"
PRICE = 2  # thousandths of USD = $0.002
PARTNER = "76561198848755367"

params = {
    "api": WX,
    "item_id": ITEM_ID,
    "price": PRICE,
    "partner": PARTNER,
    "token": TOKEN,
    "allow_trade_locked": 1,
}
r = requests.get(
    "https://api.waxpeer.com/v1/buy-one-p2p", params=params, headers=UA, timeout=90
)
print("status:", r.status_code)
print("response:", r.text[:600])
