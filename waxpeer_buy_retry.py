import os
import time
import urllib.parse
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
TOKEN = urllib.parse.parse_qs(
    urllib.parse.urlparse(key("STEAM_TRADE_URL")).query
).get("token", [""])[0]
PARTNER = "76561198848755367"

user = requests.get("https://api.waxpeer.com/v1/user", params={"api": WX}, headers=UA, timeout=30).json()
u = user.get("user", {})
status_fields = {k: u.get(k) for k in ("wallet", "can_p2p", "online", "steam_status", "is_online") if k in u}
print("account:", status_fields or {"wallet": u.get("wallet")})

NAME = "Mortar Forge Rocket Cannon"
s = requests.get(
    "https://api.waxpeer.com/v2/search-items-by-name",
    params={"api": WX, "name": NAME, "game": "dota2"},
    headers=UA,
    timeout=30,
).json()
items = (s.get("items") or {}).get(NAME) or []
if not items:
    print("no listings for", NAME)
    raise SystemExit(0)
best = min(items, key=lambda x: x.get("price") or 10**12)
print(f"buying item_id {best['item_id']} price ${best['price']/1000:.3f}")

r = requests.get(
    "https://api.waxpeer.com/v1/buy-one-p2p",
    params={
        "api": WX,
        "item_id": best["item_id"],
        "price": best["price"],
        "partner": PARTNER,
        "token": TOKEN,
        "allow_trade_locked": 1,
    },
    headers=UA,
    timeout=90,
)
print("buy status:", r.status_code)
print("buy response:", r.text[:500])

time.sleep(5)
inv = requests.get(
    "https://api.waxpeer.com/v1/get-my-inventory",
    params={"api": WX, "game": "dota2"},
    headers=UA,
    timeout=40,
).json()
names = [it.get("name") for it in (inv.get("items") or [])]
print("dota2 inventory items:", len(names))
print("target present:", NAME in names)
