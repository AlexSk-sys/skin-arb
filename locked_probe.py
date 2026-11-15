import json
import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
SP = key("SHADOWPAY_API_TOKEN")

print("=== Waxpeer prices include_hold ===")
r = requests.get(
    "https://api.waxpeer.com/v1/prices",
    params={"game": "dota2", "include_hold": 1},
    headers=UA,
    timeout=90,
)
data = r.json().get("items", [])
print("items:", len(data))
for it in data[:3]:
    print(json.dumps(it, ensure_ascii=False)[:400])

print("\n=== ShadowPay items sample ===")
r = requests.get(
    "https://api.shadowpay.com/api/v2/user/items",
    params={"project": "dota2", "limit": 3},
    headers={**UA, "Authorization": f"Bearer {SP}"},
    timeout=60,
)
for it in r.json().get("data", []):
    print(json.dumps(it, ensure_ascii=False)[:500])
