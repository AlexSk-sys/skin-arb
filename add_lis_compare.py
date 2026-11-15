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
LIS_FEE = 0.07

print(f"{'item':<46} {'wax':>7} {'lis':>7} {'best':>7}")
total_wax = total_lis = 0.0
for it in inv:
    name = it.get("name")
    wax_price = None
    lis_price = None
    if name in lis:
        lis_price = lis[name][0] * (1 - LIS_FEE)
    total_lis += lis_price or 0
    print(
        f"{name[:46]:<46} {'—':>7} {lis_price if lis_price else 0:>7.3f} "
        f"{'lis' if lis_price else '—':>7}"
    )
print(f"\nLIS net total for these items: ${total_lis:.2f}")
