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
PID = "31206451"

chk = requests.get(
    "https://api.waxpeer.com/v1/check-many-steam",
    params={"api": WX, "id": PID},
    headers=UA,
    timeout=30,
).json()
print("trade status:", chk.get("trades", [{}])[0] if chk.get("trades") else chk)

inv = requests.get(
    "https://api.waxpeer.com/v1/get-my-inventory",
    params={"api": WX, "game": "dota2"},
    headers=UA,
    timeout=40,
).json()
items = inv.get("items") or []
print("dota2 inventory:", len(items))
for it in items:
    print("  ", it.get("name"), "| item_id", it.get("item_id"), "| keys", list(it.keys()))

user = requests.get("https://api.waxpeer.com/v1/user", params={"api": WX}, headers=UA, timeout=30).json().get("user", {})
print("wallet:", user.get("wallet"))
