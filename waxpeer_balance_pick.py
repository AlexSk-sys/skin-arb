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

r = requests.get("https://api.waxpeer.com/v1/user", params={"api": WX}, headers=UA, timeout=30)
d = r.json()
user = d.get("user", {})
print("balance USD:", user.get("wallet"), "| pending:", user.get("wallet_pending"))
print("id64:", user.get("id64"))

for name in (
    "Mortar Forge Rocket Cannon",
    "Inscribed Iceborn Trinity",
    "Jingle Fist Bundle",
):
    try:
        s = requests.get(
            "https://api.waxpeer.com/v2/search-items-by-name",
            params={"api": WX, "name": name, "game": "dota2"},
            headers=UA,
            timeout=30,
        )
        items = (s.json().get("items") or {}).get(name) or []
        if not items:
            print(f"{name:<28} нет лотов")
            continue
        best = min(items, key=lambda x: x.get("price") or 10**12)
        print(
            f"{name:<28} item_id {best['item_id']} | "
            f"${best['price']/1000:.3f} | лотов {len(items)}"
        )
    except Exception as e:  # noqa: BLE001
        print(f"{name:<28} ERR {type(e).__name__}")
