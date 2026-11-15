import os
import time
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}
NAME = "The Iron Bear's Set"


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
s = requests.get(
    "https://api.waxpeer.com/v2/search-items-by-name",
    params={"api": WX, "name": NAME, "game": "dota2"},
    headers=UA,
    timeout=30,
).json()
items = (s.get("items") or {}).get(NAME) or []
print("listings:", len(items))
if not items:
    raise SystemExit(0)
best = min(items, key=lambda x: x.get("price") or 10**12)
print(f"cheapest item_id {best['item_id']} price ${best['price']/1000:.3f}")

# No allow_trade_locked: Waxpeer must refuse locked listings.
r = requests.get(
    "https://api.waxpeer.com/v1/buy-one-p2p",
    params={
        "api": WX,
        "item_id": best["item_id"],
        "price": best["price"],
        "partner": "76561198848755367",
    },
    headers=UA,
    timeout=90,
)
print("buy:", r.status_code, r.text[:400])

try:
    pid = r.json().get("id")
except Exception:  # noqa: BLE001
    pid = None
if pid:
    for attempt in range(8):
        time.sleep(10)
        chk = requests.get(
            "https://api.waxpeer.com/v1/check-many-steam",
            params={"api": WX, "id": pid},
            headers=UA,
            timeout=30,
        ).json()
        trade = (chk.get("trades") or [{}])[0]
        print(f"attempt {attempt + 1}: status {trade.get('status')} done {trade.get('done')} reason {trade.get('reason')}")
        if trade.get("status") in (5, 6):
            break
