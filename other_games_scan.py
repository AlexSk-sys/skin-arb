"""Arbitrage scan for games without CS2 trade protection: Dota 2, TF2, Rust.

Sources: Waxpeer (min in thousandths USD) and Skinport (min_price in USD).
No 7-day trade protection applies to these games, so a delivered item can be
relisted immediately.
"""

from __future__ import annotations

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
UNDERCUT = 0.02
FEES = {"wax": 0.05, "skinport": 0.12}
GAMES = {"dota2": 570, "tf2": 440, "rust": 252490}
MIN_VOL = 3
MIN_MARGIN = 0.05
MAX_MARGIN = 0.60


def waxpeer(game: str) -> dict[str, dict]:
    r = requests.get("https://api.waxpeer.com/v1/prices", params={"game": game}, headers=UA, timeout=90)
    out = {}
    for it in r.json().get("items", []):
        name = it.get("name")
        if name:
            out[name] = {"ask": it["min"] / 1000.0, "vol": int(it.get("count") or 0)}
    return out


def skinport(app_id: int) -> dict[str, dict]:
    r = requests.get(
        "https://api.skinport.com/v1/items",
        params={"app_id": app_id, "currency": "USD"},
        headers=UA,
        timeout=120,
    )
    out = {}
    for it in r.json():
        name = it.get("market_hash_name")
        price = it.get("min_price")
        if name and price:
            out[name] = {"ask": float(price), "vol": int(it.get("quantity") or 0)}
    return out


for game, app_id in GAMES.items():
    wax = waxpeer(game)
    skin = skinport(app_id)
    common = set(wax) & set(skin)
    rows = []
    for name in common:
        w, s = wax[name], skin[name]
        if w["vol"] < MIN_VOL or s["vol"] < MIN_VOL or w["ask"] <= 0 or s["ask"] <= 0:
            continue
        # Waxpeer -> Skinport
        proceeds = s["ask"] * (1 - UNDERCUT) * (1 - FEES["skinport"])
        profit = proceeds - w["ask"]
        if profit > 0 and MIN_MARGIN <= profit / w["ask"] <= MAX_MARGIN:
            rows.append((profit, name, "wax->skinport", w["ask"], s["ask"], w["vol"], s["vol"]))
        # Skinport -> Waxpeer
        proceeds = w["ask"] * (1 - UNDERCUT) * (1 - FEES["wax"])
        profit = proceeds - s["ask"]
        if profit > 0 and MIN_MARGIN <= profit / s["ask"] <= MAX_MARGIN:
            rows.append((profit, name, "skinport->wax", s["ask"], w["ask"], s["vol"], w["vol"]))

    rows.sort(reverse=True)
    print(f"\n=== {game}: waxpeer {len(wax)}, skinport {len(skin)}, пересечение {len(common)}, связок {len(rows)}")
    print(f"{'item':<44} {'route':<16} {'buy':>8} {'sell':>8} {'net':>7}")
    for profit, name, route, buy, sell, vb, vs in rows[:12]:
        print(
            f"{name[:44]:<44} {route:<16} ${buy:>7.2f} ${sell:>7.2f} ${profit:>6.2f} "
            f"({profit / buy * 100:>4.0f}%) vol {vb}/{vs}"
        )
