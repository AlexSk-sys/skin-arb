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

# Pick a live listing to inspect.
s = requests.get(
    "https://api.waxpeer.com/v2/search-items-by-name",
    params={"api": WX, "name": "The Iron Bear's Set", "game": "dota2"},
    headers=UA,
    timeout=30,
).json()
items = (s.get("items") or {}).get("The Iron Bear's Set") or []
print("listings:", len(items))
if items:
    best = min(items, key=lambda x: x.get("price") or 10**12)
    print("sample listing:", json.dumps(best, ensure_ascii=False)[:400])
    r = requests.get(
        "https://api.waxpeer.com/v1/check-availability",
        params={"api": WX, "item_id": best["item_id"]},
        headers=UA,
        timeout=30,
    )
    print("check-availability:", r.status_code, r.text[:500])
