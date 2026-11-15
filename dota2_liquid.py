import json
import time
from pathlib import Path

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
CACHE = Path(__file__).resolve().parent / "cache" / "skinport_570.json"
CACHE_TTL = 1800
UNDERCUT = 0.02
FEES = {"wax": 0.05, "skinport": 0.12}
MIN_VOL = 10
MIN_MARGIN = 0.08
MAX_MARGIN = 0.40


def waxpeer() -> dict[str, dict]:
    r = requests.get(
        "https://api.waxpeer.com/v1/prices", params={"game": "dota2"}, headers=UA, timeout=90
    )
    return {
        it["name"]: {"ask": it["min"] / 1000.0, "vol": int(it.get("count") or 0)}
        for it in r.json().get("items", [])
        if it.get("name")
    }


def skinport() -> dict[str, dict]:
    data = None
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        data = json.loads(CACHE.read_text(encoding="utf-8"))
    if data is None:
        for _attempt in range(3):
            r = requests.get(
                "https://api.skinport.com/v1/items",
                params={"app_id": 570, "currency": "USD"},
                headers=UA,
                timeout=120,
            )
            body = r.json()
            if r.status_code == 200 and isinstance(body, list):
                data = body
                CACHE.parent.mkdir(exist_ok=True)
                CACHE.write_text(json.dumps(data), encoding="utf-8")
                break
            print(f"skinport {r.status_code}: {str(body)[:120]}")
            time.sleep(60)
    if not isinstance(data, list):
        return {}
    out = {}
    for it in data:
        if not isinstance(it, dict):
            continue
        name, price = it.get("market_hash_name"), it.get("min_price")
        if name and price:
            out[name] = {"ask": float(price), "vol": int(it.get("quantity") or 0)}
    return out


wax, skin = waxpeer(), skinport()
rows = []
for name in set(wax) & set(skin):
    w, s = wax[name], skin[name]
    if w["vol"] < MIN_VOL or s["vol"] < MIN_VOL:
        continue
    p = s["ask"] * (1 - UNDERCUT) * (1 - FEES["skinport"]) - w["ask"]
    if p > 0 and MIN_MARGIN <= p / w["ask"] <= MAX_MARGIN:
        rows.append((p, name, "wax->skinport", w["ask"], s["ask"], w["vol"], s["vol"]))
    p = w["ask"] * (1 - UNDERCUT) * (1 - FEES["wax"]) - s["ask"]
    if p > 0 and MIN_MARGIN <= p / s["ask"] <= MAX_MARGIN:
        rows.append((p, name, "skinport->wax", s["ask"], w["ask"], s["vol"], w["vol"]))

rows.sort(reverse=True)
print(f"ликвидных связок Dota 2 (объём >= {MIN_VOL} с обеих сторон): {len(rows)}")
print(f"{'item':<44} {'route':<16} {'buy':>8} {'sell':>8} {'net':>7} {'vol':>10}")
for profit, name, route, buy, sell, vb, vs in rows[:15]:
    print(
        f"{name[:44]:<44} {route:<16} ${buy:>7.2f} ${sell:>7.2f} ${profit:>6.2f} "
        f"({profit / buy * 100:>4.0f}%) {vb:>3}/{vs:<3}"
    )
