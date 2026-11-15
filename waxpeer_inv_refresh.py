import os
import time
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")

f = requests.get(
    "https://api.waxpeer.com/v1/fetch-my-inventory",
    params={"api": WX, "game": "dota2"},
    headers=UA,
    timeout=60,
)
print("fetch:", f.status_code, f.text[:200])
time.sleep(5)

for attempt in range(3):
    inv = requests.get(
        "https://api.waxpeer.com/v1/get-my-inventory",
        params={"api": WX, "game": "dota2"},
        headers=UA,
        timeout=40,
    ).json()
    items = inv.get("items") or []
    print(f"attempt {attempt + 1}: {len(items)} items")
    for it in items:
        print("  ", it.get("name"), "| item_id", it.get("item_id"))
    if items:
        break
    time.sleep(10)
