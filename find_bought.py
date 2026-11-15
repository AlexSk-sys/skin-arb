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
r = requests.get(
    "https://api.waxpeer.com/v1/get-my-inventory",
    params={"api": WX, "game": "csgo"},
    headers=UA,
    timeout=40,
)
data = r.json()
items = data.get("items", [])
print("items in Waxpeer view:", len(items))

targets = ["ropz", "Houndstooth"]
for it in items:
    name = it.get("name", "")
    if any(t.lower() in name.lower() for t in targets):
        print("FOUND:", name, "| item_id", it.get("item_id"), "| price", it.get("price"))

print("\nfirst 15 names:")
for it in items[:15]:
    print("  ", it.get("name"), "| price", it.get("price"))
