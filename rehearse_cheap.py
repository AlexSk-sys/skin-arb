"""Dry run on a $10 budget: pick cheap live spreads and build real orders."""

from __future__ import annotations

import os
import urllib.parse
import winreg

import requests

import scan3  # type: ignore

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
BUDGET = 10.0
MAX_UNIT = 5.0
TOP = 3


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = get_key("WAXPEER_API_KEY")
MC = get_key("MARKET_CSGO_API_KEY")
TRADE_URL = get_key("STEAM_TRADE_URL")
TRADE_TOKEN = urllib.parse.parse_qs(urllib.parse.urlparse(TRADE_URL).query).get("token", [""])[0]
PARTNER64 = "76561198848755367"


def usd_rub() -> float:
    try:
        d = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=20).json()
        return float(d["Valute"]["USD"]["Value"])
    except Exception:  # noqa: BLE001
        return 82.0


RATE = usd_rub()


def find_listing(name: str):
    """Cheapest Waxpeer listing for an exact name, via the search endpoint."""
    r = requests.get(
        "https://api.waxpeer.com/v2/search-items-by-name",
        params={"api": WX, "name": name},
        headers=UA,
        timeout=30,
    )
    items = (r.json().get("items") or {}).get(name) or []
    if not items:
        return None
    best = min(items, key=lambda x: x.get("price") or 10**12)
    return str(best["item_id"]), int(best["price"])


def mcs_lowest(name: str):
    r = requests.get(
        "https://market.csgo.com/api/v2/search-item-by-hash-name",
        params={"key": MC, "hash_name": name, "currency": "USD"},
        headers=UA,
        timeout=40,
    )
    data = r.json().get("data") or []
    if not data:
        return None
    return min(int(x["price"]) for x in data)


wax = scan3.fetch_waxpeer()
mcs = scan3.fetch_market_csgo()
rows = scan3.evaluate(scan3.build_table(wax, mcs, {}))
cheap = [
    r
    for r in rows
    if r["buy"] <= MAX_UNIT
    and r["margin"] >= 0.10
    and r["margin"] <= 0.60
    and r["vol_buy"] >= 20
    and r["vol_sell"] >= 20
]
cheap.sort(key=lambda r: r["profit"], reverse=True)

print(f"курс USD/RUB {RATE:.2f}, бюджет ${BUDGET}, кандидатов до ${MAX_UNIT}: {len(cheap)}\n")
spent = 0.0
for r in cheap[:TOP]:
    if spent + r["buy"] > BUDGET:
        break
    listing = find_listing(r["item"])
    kop = mcs_lowest(r["item"])
    if not listing or not kop:
        continue
    item_id, milli = listing
    buy = milli / 1000
    sell = kop / 100 / RATE
    proceeds = sell * 0.98 * 0.95
    profit = proceeds - buy
    spent += buy
    print(f"{r['item']}")
    print(f"  item_id {item_id} | купить ${buy:.2f} | продать {kop} коп = ${sell:.2f}")
    print(f"  чистыми ${proceeds:.2f}, прибыль ${profit:.2f} ({profit / buy * 100:.1f}%)")
    print(
        "  GET /v1/buy-one-p2p?"
        + urllib.parse.urlencode(
            {
                "api": "***",
                "item_id": item_id,
                "price": milli,
                "partner": PARTNER64,
                "token": TRADE_TOKEN or "***",
                "allow_trade_locked": 1,
            }
        )
    )
    print()

print(f"итого вложений: ${spent:.2f} из ${BUDGET}")
print("Ничего не отправлено.")
