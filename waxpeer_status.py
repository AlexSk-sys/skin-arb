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
PID = "31206451"

for param in ("ids", "id", "waxids", "waxid", "purchase_ids"):
    try:
        r = requests.get(
            "https://api.waxpeer.com/v1/check-many-steam",
            params={"api": WX, param: PID},
            headers=UA,
            timeout=30,
        )
        print(f"check-many-steam ?{param}= : {r.status_code} {r.text[:250]}")
    except Exception as e:  # noqa: BLE001
        print(f"check ?{param} ERR {type(e).__name__}")

for path in ("/v1/my-history", "/v1/buy-order-history"):
    try:
        r = requests.get(
            "https://api.waxpeer.com" + path, params={"api": WX}, headers=UA, timeout=30
        )
        print(f"{path}: {r.status_code} {r.text[:300]}")
    except Exception as e:  # noqa: BLE001
        print(f"{path} ERR {type(e).__name__}")

time.sleep(15)
inv = requests.get(
    "https://api.waxpeer.com/v1/get-my-inventory",
    params={"api": WX, "game": "dota2"},
    headers=UA,
    timeout=40,
).json()
items = inv.get("items") or []
print("dota2 inventory after wait:", len(items))
for it in items[:10]:
    print("  ", it.get("name"), "| item_id", it.get("item_id"))
