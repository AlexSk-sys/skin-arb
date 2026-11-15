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

r = requests.get(
    "https://csfloat.com/api/v1/listings",
    params={"limit": 5, "sort_by": "lowest_price", "type": "buy_now"},
    headers=H,
    timeout=40,
)
print("status", r.status_code, "bytes", len(r.content))
d = r.json()
if isinstance(d, dict):
    print("top keys:", list(d.keys()))
    print("cursor:", d.get("cursor"))
    data = d.get("data", [])
else:
    data = d
print("items:", len(data))
if data:
    first = data[0]
    print("item keys:", list(first.keys()))
    print(json.dumps(first, ensure_ascii=False, indent=2)[:1800])
