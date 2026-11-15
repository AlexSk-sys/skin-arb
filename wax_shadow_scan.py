"""Double-API Dota 2 arbitrage: Waxpeer (buy side) vs ShadowPay (sell side).

Both have public APIs and Dota 2 has no CS2 trade protection.
Fees are assumptions until confirmed: Waxpeer 5%, ShadowPay 5%.
"""

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
SP = key("SHADOWPAY_API_TOKEN")
UNDERCUT = 0.02
FEES = {"wax": 0.05, "sp": 0.05}
MIN_VOL = 5


def waxpeer() -> dict[str, dict]:
    r = requests.get(
        "https://api.waxpeer.com/v1/prices", params={"game": "dota2"}, headers=UA, timeout=90
    )
    return {
        it["name"]: {"ask": it["min"] / 1000.0, "vol": int(it.get("count") or 0)}
        for it in r.json().get("items", [])
        if it.get("name")
    }


def shadowpay() -> dict[str, dict]:
    r = requests.get(
        "https://api.shadowpay.com/api/v2/user/items/prices",
        params={"project": "dota2"},
        headers={**UA, "Authorization": f"Bearer {SP}"},
        timeout=90,
    )
    out = {}
    for it in r.json().get("data", []):
        name = it.get("steam_market_hash_name")
        if name and it.get("price"):
            out[name] = {"ask": float(it["price"]), "vol": int(it.get("volume") or 0)}
    return out


wax, sp = waxpeer(), shadowpay()
print(f"waxpeer dota2: {len(wax)}, shadowpay dota2: {len(sp)}, common: {len(set(wax) & set(sp))}")

rows = []
for name in set(wax) & set(sp):
    w, s = wax[name], sp[name]
    if w["vol"] < MIN_VOL or s["vol"] < MIN_VOL:
        continue
    # Waxpeer -> ShadowPay
    proceeds = s["ask"] * (1 - UNDERCUT) * (1 - FEES["sp"])
    profit = proceeds - w["ask"]
    if profit > 0 and 0.05 <= profit / w["ask"] <= 0.40:
        rows.append((profit, name, "wax->sp", w["ask"], s["ask"], w["vol"], s["vol"]))
    # ShadowPay -> Waxpeer
    proceeds = w["ask"] * (1 - UNDERCUT) * (1 - FEES["wax"])
    profit = proceeds - s["ask"]
    if profit > 0 and 0.05 <= profit / s["ask"] <= 0.40:
        rows.append((profit, name, "sp->wax", s["ask"], w["ask"], s["vol"], w["vol"]))

rows.sort(reverse=True)
print(f"связок: {len(rows)}\n")
print(f"{'item':<44} {'route':<10} {'buy':>7} {'sell':>7} {'net':>6} {'mrg':>5} {'vol':>9}")
for profit, name, route, buy, sell, vb, vs in rows[:20]:
    print(
        f"{name[:44]:<44} {route:<10} ${buy:>6.2f} ${sell:>6.2f} ${profit:>5.2f} "
        f"{profit/buy*100:>4.0f}% {vb:>4}/{vs:<4}"
    )
