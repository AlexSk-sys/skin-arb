import json
import os
import winreg
from pathlib import Path

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}
FEES = {"wax": 0.05, "sp": 0.05, "mcs": 0.05, "skinport": 0.12}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
SP = key("SHADOWPAY_API_TOKEN")

inv = requests.get(
    "https://api.waxpeer.com/v1/get-my-inventory",
    params={"api": WX, "game": "csgo"},
    headers=UA,
    timeout=60,
).json().get("items", [])
names = [it["name"] for it in inv]

wax = {
    p["name"]: int(p["min"]) / 1000
    for p in requests.get(
        "https://api.waxpeer.com/v1/prices", params={"game": "csgo"}, headers=UA, timeout=90
    ).json().get("items", [])
    if p.get("name")
}

sp = {}
try:
    for it in requests.get(
        "https://api.shadowpay.com/api/v2/user/items/prices",
        params={"project": "csgo"},
        headers={**UA, "Authorization": f"Bearer {SP}"},
        timeout=90,
    ).json().get("data", []):
        name = it.get("steam_market_hash_name")
        if name and it.get("price"):
            sp[name] = float(it["price"])
except Exception:  # noqa: BLE001
    pass

mcs = {}
try:
    for it in requests.get(
        "https://market.csgo.com/api/v2/prices/USD.json", headers=UA, timeout=90
    ).json().get("items", []):
        mcs[it["market_hash_name"]] = float(it["price"])
except Exception:  # noqa: BLE001
    pass

skin = {}
cache = Path(__file__).resolve().parent / "cache" / "skinport_cs2.json"
if cache.exists():
    data = json.loads(cache.read_text(encoding="utf-8"))
else:
    try:
        r = requests.get(
            "https://api.skinport.com/v1/items",
            params={"app_id": 730, "currency": "USD"},
            headers=UA,
            timeout=120,
        )
        data = r.json() if r.status_code == 200 else []
        if data:
            cache.parent.mkdir(exist_ok=True)
            cache.write_text(json.dumps(data), encoding="utf-8")
    except Exception:  # noqa: BLE001
        data = []
for it in data if isinstance(data, list) else []:
    if isinstance(it, dict) and it.get("min_price") and it.get("market_hash_name"):
        skin[it["market_hash_name"]] = float(it["min_price"])

print(f"prices: wax {len(wax)}, sp {len(sp)}, mcs {len(mcs)}, skinport {len(skin)}")
print(f"\n{'item':<44} {'wax':>7} {'sp':>7} {'mcs':>7} {'skin':>7}  best")
for name in names:
    vals: dict[str, float] = {}
    if name in wax:
        vals["wax"] = wax[name] * (1 - FEES["wax"])
    if name in sp:
        vals["sp"] = sp[name] * (1 - FEES["sp"])
    if name in mcs:
        vals["mcs"] = mcs[name] * (1 - FEES["mcs"])
    if name in skin:
        vals["skin"] = skin[name] * (1 - FEES["skinport"])
    if not vals:
        continue
    best = max(vals, key=lambda k: vals[k])
    row = " ".join(f"{vals.get(k, 0):>7.3f}" for k in ("wax", "sp", "mcs", "skin"))
    print(f"{name[:44]:<44} {row}  {best} ${vals[best]:.3f}")
