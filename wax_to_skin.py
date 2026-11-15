import json
import time
from pathlib import Path

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}
CACHE = Path(__file__).resolve().parent / "cache" / "skinport_570.json"
UNDERCUT = 0.02
SP_FEE = 0.12
BUDGET = 4.99
MIN_VOL = 3


def skinport() -> dict:
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    for _ in range(3):
        r = requests.get(
            "https://api.skinport.com/v1/items",
            params={"app_id": 570, "currency": "USD"},
            headers=UA,
            timeout=120,
        )
        if r.status_code == 200:
            data = r.json()
            CACHE.parent.mkdir(exist_ok=True)
            CACHE.write_text(json.dumps(data), encoding="utf-8")
            return data
        print("skinport", r.status_code, r.text[:100])
        time.sleep(45)
    return []


def waxpeer() -> dict:
    r = requests.get(
        "https://api.waxpeer.com/v1/prices", params={"game": "dota2"}, headers=UA, timeout=90
    )
    return {
        it["name"]: {"ask": it["min"] / 1000.0, "vol": int(it.get("count") or 0)}
        for it in r.json().get("items", [])
        if it.get("name")
    }


sp_raw = skinport()
sp = {
    it["market_hash_name"]: {"ask": float(it["min_price"]), "vol": int(it.get("quantity") or 0)}
    for it in sp_raw
    if isinstance(it, dict) and it.get("min_price") and it.get("market_hash_name")
}
wax = waxpeer()
print(f"skinport items: {len(sp)}, waxpeer items: {len(wax)}")

rows = []
for name in set(sp) & set(wax):
    w, s = wax[name], sp[name]
    if w["vol"] < MIN_VOL or s["vol"] < MIN_VOL or w["ask"] > BUDGET:
        continue
    proceeds = s["ask"] * (1 - UNDERCUT) * (1 - SP_FEE)
    profit = proceeds - w["ask"]
    if profit <= 0:
        continue
    margin = profit / w["ask"]
    if 0.10 <= margin <= 0.40:
        rows.append((profit, name, w["ask"], s["ask"], margin, w["vol"], s["vol"]))

rows.sort(reverse=True)
print(f"кандидатов Waxpeer -> Skinport до ${BUDGET}: {len(rows)}")
for profit, name, buy, sell, margin, vb, vs in rows[:12]:
    print(
        f"{name[:44]:<44} ${buy:>6.2f} -> ${sell:>6.2f}  "
        f"+${profit:>5.2f} ({margin*100:>4.0f}%) vol {vb}/{vs}"
    )
