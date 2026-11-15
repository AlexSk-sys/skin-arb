import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
for params in (
    {"api": WX, "game": "csgo", "include_hold": 1},
    {"api": WX, "game": "csgo", "include_hold": "1"},
):
    r = requests.get(
        "https://api.waxpeer.com/v1/get-my-inventory", params=params, headers=UA, timeout=40
    )
    data = r.json()
    items = data.get("items", [])
    print(f"params {params} -> {r.status_code}, items {len(items)}")
    for it in items:
        name = it.get("name", "")
        if "ropz" in name.lower() or "houndstooth" in name.lower():
            print("  FOUND:", {k: it.get(k) for k in ("item_id", "name", "lock", "tradable", "unlock_at")})
    if items:
        print("  sample fields:", list(items[0].keys()))
    break
