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

inv = requests.get(
    "https://api.waxpeer.com/v1/get-my-inventory",
    params={"api": WX, "game": "csgo"},
    headers=UA,
    timeout=60,
).json().get("items", [])

prices = requests.get(
    "https://api.waxpeer.com/v1/prices", params={"game": "csgo"}, headers=UA, timeout=90
).json().get("items", [])
price_map = {p["name"]: int(p["min"]) for p in prices if p.get("name")}

payload = []
print(f"{'item':<48} {'market':>9} {'list':>9}")
for it in inv:
    name = it.get("name")
    market = price_map.get(name)
    if not market:
        print(f"{name[:48]:<48} {'—':>9} {'skip':>9}")
        continue
    list_price = max(1, market - 1)  # 1 milli below the lowest ask
    payload.append({"item_id": str(it["item_id"]), "price": list_price})
    print(f"{name[:48]:<48} ${market/1000:>8.3f} ${list_price/1000:>8.3f}")

print(f"\nlisting {len(payload)} items...")
r = requests.post(
    "https://api.waxpeer.com/v1/list-items-steam",
    params={"api": WX, "game": "csgo"},
    json={"items": payload},
    headers=UA,
    timeout=90,
)
print("status", r.status_code)
print(r.text[:1500])
