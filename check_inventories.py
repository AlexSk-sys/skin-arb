import json
import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


MC = key("MARKET_CSGO_API_KEY")
WX = key("WAXPEER_API_KEY")

MCS_PATHS = ["/api/v2/get-inventory", "/api/v2/load-inventory", "/api/v2/get-my-inventory"]
WAX_PATHS = ["/v1/get-my-inventory", "/v1/fetch-my-inventory", "/v1/get-items-list"]

print("=== Market.CSGO ===")
for path in MCS_PATHS:
    try:
        r = requests.get("https://market.csgo.com" + path, params={"key": MC}, headers=UA, timeout=30)
        body = r.text[:300].replace("\n", " ")
        print(f"{path:<28} {r.status_code} {body}")
    except Exception as e:  # noqa: BLE001
        print(f"{path:<28} ERR {type(e).__name__}")

print("\n=== Waxpeer ===")
for path in WAX_PATHS:
    try:
        r = requests.get(
            "https://api.waxpeer.com" + path,
            params={"api": WX, "game": "csgo"},
            headers=UA,
            timeout=30,
        )
        body = r.text[:300].replace("\n", " ")
        print(f"{path:<28} {r.status_code} {body}")
    except Exception as e:  # noqa: BLE001
        print(f"{path:<28} ERR {type(e).__name__}")
