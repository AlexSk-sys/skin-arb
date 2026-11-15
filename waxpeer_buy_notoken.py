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
u = requests.get("https://api.waxpeer.com/v1/user", params={"api": WX}, headers=UA, timeout=30).json().get("user", {})
interesting = {k: v for k, v in u.items() if any(s in k.lower() for s in ("token", "online", "p2p", "steam", "wallet"))}
print("user fields:", interesting)

NAME = "Mortar Forge Rocket Cannon"
s = requests.get(
    "https://api.waxpeer.com/v2/search-items-by-name",
    params={"api": WX, "name": NAME, "game": "dota2"},
    headers=UA,
    timeout=30,
).json()
items = (s.get("items") or {}).get(NAME) or []
if not items:
    print("no listings")
    raise SystemExit(0)
best = min(items, key=lambda x: x.get("price") or 10**12)
print("item", best["item_id"], "$", best["price"] / 1000)

base = {
    "api": WX,
    "item_id": best["item_id"],
    "price": best["price"],
    "partner": "76561198848755367",
    "allow_trade_locked": 1,
}
for label, extra in (("no token", {}), ("empty token", {"token": ""})):
    try:
        r = requests.get(
            "https://api.waxpeer.com/v1/buy-one-p2p",
            params={**base, **extra},
            headers=UA,
            timeout=90,
        )
        print(f"{label}: {r.status_code} {r.text[:300]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label}: ERR {type(e).__name__}")
