import json
import os
import winreg
from pathlib import Path

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}
HERE = Path(__file__).resolve().parent


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
lis = json.loads((HERE / "lis_prices.json").read_text(encoding="utf-8"))["items"]

rows = []
for it in inv:
    name = it.get("name")
    if name in lis:
        rows.append((lis[name][0], name))
rows.sort(reverse=True)

print(f"{'#':>2}  {'item':<48} {'LIS price':>10}")
for i, (price, name) in enumerate(rows, 1):
    print(f"{i:>2}  {name[:48]:<48} ${price:>9.2f}")
print(f"\nитого по LIS: ${sum(p for p, _ in rows):.2f}")
