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

for name in ("Urushin Huntsman", "Order of the Wandering Flame", "Genuine Skittering Desolation"):
    for params in (
        {"api": WX, "name": name, "game": "dota2"},
        {"api": WX, "name": name},
    ):
        try:
            r = requests.get(
                "https://api.waxpeer.com/v2/search-items-by-name",
                params=params,
                headers=UA,
                timeout=30,
            )
            d = r.json()
            items = (d.get("items") or {}).get(name) or []
            print(f"{name[:32]:<32} game={params.get('game')} -> {r.status_code} items={len(items)}")
            if items:
                best = min(items, key=lambda x: x.get("price") or 10**12)
                print("   ", json.dumps(best, ensure_ascii=False)[:220])
        except Exception as e:  # noqa: BLE001
            print(f"{name[:32]:<32} ERR {type(e).__name__}")
