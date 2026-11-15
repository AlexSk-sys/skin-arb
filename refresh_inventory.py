import os
import time
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")

r = requests.get(
    "https://api.waxpeer.com/v1/fetch-my-inventory",
    params={"api": WX, "game": "csgo"},
    headers=UA,
    timeout=40,
)
print("fetch:", r.status_code, r.text[:200])
time.sleep(3)

r = requests.get(
    "https://api.waxpeer.com/v1/get-my-inventory",
    params={"api": WX, "game": "csgo"},
    headers=UA,
    timeout=40,
)
items = r.json().get("items", [])
print("items:", len(items))
for it in items:
    print(f"  {it.get('name')} | item_id {it.get('item_id')}")
