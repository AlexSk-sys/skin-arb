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
PURCHASE_ID = "31206451"

u = requests.get("https://api.waxpeer.com/v1/user", params={"api": WX}, headers=UA, timeout=30).json().get("user", {})
print("wallet:", u.get("wallet"), "| can_p2p:", u.get("can_p2p"))

for attempt in range(3):
    inv = requests.get(
        "https://api.waxpeer.com/v1/get-my-inventory",
        params={"api": WX, "game": "dota2"},
        headers=UA,
        timeout=40,
    ).json()
    items = inv.get("items") or []
    hit = [it for it in items if "Mortar Forge" in (it.get("name") or "")]
    print(f"attempt {attempt + 1}: dota2 inventory {len(items)} items, target found: {bool(hit)}")
    if hit:
        print("  ", {k: hit[0].get(k) for k in ("item_id", "name", "lock", "tradable")})
        break
    time.sleep(10)

try:
    chk = requests.get(
        "https://api.waxpeer.com/v1/check-many-steam",
        params={"api": WX, "waxids": PURCHASE_ID},
        headers=UA,
        timeout=30,
    )
    print("check-many-steam:", chk.status_code, chk.text[:400])
except Exception as e:  # noqa: BLE001
    print("check ERR", type(e).__name__)
