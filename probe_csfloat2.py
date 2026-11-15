import json
import os
import winreg

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


H = {**UA, "Authorization": get_key("CSFLOAT_API_KEY")}
NAME = "AK-47 | Redline (Field-Tested)"

for param in ("market_hash_name", "name", "search"):
    try:
        r = requests.get(
            "https://csfloat.com/api/v1/listings",
            params={"limit": 5, "sort_by": "lowest_price", "type": "buy_now", param: NAME},
            headers=H,
            timeout=40,
        )
        d = r.json()
        data = d.get("data", []) if isinstance(d, dict) else d
        prices = [x.get("price") for x in data]
        names = [x.get("item", {}).get("market_hash_name") for x in data][:3]
        print(f"{param}: status={r.status_code} items={len(data)} prices={prices}")
        print("   names:", names)
    except Exception as e:  # noqa: BLE001
        print(param, "ERR", type(e).__name__, str(e)[:80])
