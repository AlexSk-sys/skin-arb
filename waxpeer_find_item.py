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

for game in ("dota2", "csgo"):
    try:
        r = requests.get(
            "https://api.waxpeer.com/v1/get-steam-items",
            params={"api": WX, "game": game},
            headers=UA,
            timeout=60,
        )
        items = r.json().get("items") or []
        print(f"{game}: {r.status_code}, items {len(items)}")
        hits = [it for it in items if "Mortar Forge" in (it.get("name") or "")]
        print("  Mortar Forge found:", hits or "нет")
        if items:
            print("  sample:", json.dumps(items[0], ensure_ascii=False)[:200])
    except Exception as e:  # noqa: BLE001
        print(f"{game} ERR {type(e).__name__}")
