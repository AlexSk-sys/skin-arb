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

print("=== Waxpeer inventory ===")
try:
    r = requests.get(
        "https://api.waxpeer.com/v1/get-my-inventory",
        params={"api": WX, "game": "dota2"},
        headers=UA,
        timeout=40,
    )
    items = r.json().get("items") or []
    print("items:", len(items))
    for it in items[:10]:
        print("  ", it.get("name"), "| item_id", it.get("item_id"), "| keys", list(it.keys())[:8])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)

print("\n=== ShadowPay inventory ===")
try:
    r = requests.get(
        "https://api.shadowpay.com/api/v2/user/inventory",
        params={"project": "dota2"},
        headers={**UA, "Authorization": f"Bearer {SP}"},
        timeout=40,
    )
    data = r.json().get("data") or []
    print("items:", len(data))
    for it in data[:10]:
        print("  ", it)
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)
