"""Dry run: build the exact live orders from real listings, send nothing.

Shows:
  1. the Waxpeer buy-one-p2p request that would be sent,
  2. the Market.CSGO sell request that would follow,
  3. the expected P&L after fees.
"""

from __future__ import annotations

import csv
import os
import urllib.parse
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
TARGET = "StatTrak™ M4A4 | Desolate Space (Battle-Scarred)"
MAX_LINES = 2_000_000


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = get_key("WAXPEER_API_KEY")
MC = get_key("MARKET_CSGO_API_KEY")
TRADE_URL = get_key("STEAM_TRADE_URL")
q = urllib.parse.parse_qs(urllib.parse.urlparse(TRADE_URL).query)
PARTNER64 = "76561198848755367"
TRADE_TOKEN = q.get("token", [""])[0]


def find_listing(name: str) -> tuple[str, int, str, str] | None:
    """Lowest-priced Waxpeer listing for an exact market_hash_name."""
    url = "https://api.waxpeer.com/v1/prices/snapshot"
    params = {"api": WX, "format": "csv", "search": name}
    best = None
    with requests.get(url, params=params, stream=True, timeout=180) as r:
        r.raise_for_status()
        for i, line in enumerate(r.iter_lines(decode_unicode=True)):
            if i > MAX_LINES:
                break
            if not line or line.startswith("item_id,"):
                continue
            row = next(csv.reader([line]), [])
            if len(row) < 9 or row[1] != name:
                continue
            try:
                price = int(row[2])
            except ValueError:
                continue
            if best is None or price < best[1]:
                best = (row[0], price, row[7], row[8])
    return best


def mcs_price(name: str, rate: float) -> tuple[int, float] | None:
    r = requests.get(
        "https://market.csgo.com/api/v2/search-item-by-hash-name",
        params={"key": MC, "hash_name": name, "currency": "USD"},
        headers=UA,
        timeout=40,
    )
    data = r.json().get("data") or []
    if not data:
        return None
    lowest = min(int(x["price"]) for x in data)
    return lowest, lowest / 100 / rate


def usd_rub() -> float:
    try:
        d = requests.get("https://www.cbr-xml-daily.ru/daily_json.js", timeout=20).json()
        return float(d["Valute"]["USD"]["Value"])
    except Exception:  # noqa: BLE001
        return 0.0


listing = find_listing(TARGET)
item_id = price_milli = class_id = instance_id = None
print("=== Waxpeer listing ===")
if not listing:
    print("не найден в снапшоте")
else:
    item_id, price_milli, class_id, instance_id = listing
    print(f"item_id     : {item_id}")
    print(f"price       : {price_milli} (={price_milli / 1000:.2f} USD)")
    print(f"class/inst  : {class_id}/{instance_id}")

rate = usd_rub()
print(f"\nUSD/RUB     : {rate:.2f}")
mcs = mcs_price(TARGET, rate) if rate else None
if mcs:
    print(f"Market.CSGO : {mcs[0]} kopecks = {mcs[0] / 100:.2f} RUB = ${mcs[1]:.2f}")

if listing and mcs:
    buy = listing[1] / 1000
    sell = mcs[1]
    proceeds = sell * 0.98 * 0.95
    profit = proceeds - buy
    print(f"\nкупить ${buy:.2f} -> продать ${sell:.2f}")
    print(f"после подреза 2% и комиссии 5%: ${proceeds:.2f}, прибыль ${profit:.2f} ({profit / buy * 100:.1f}%)")

if listing:
    item_id, price_milli, class_id, instance_id = listing
    buy_url = "https://api.waxpeer.com/v1/buy-one-p2p?" + urllib.parse.urlencode(
        {
            "api": "***REDACTED***",
            "item_id": item_id,
            "price": price_milli,
            "partner": PARTNER64,
            "token": TRADE_TOKEN or "***TRADE_TOKEN***",
            "allow_trade_locked": 1,
        }
    )
    print("\n=== БУДЕТ ОТПРАВЛЕНО (не отправлено) ===")
    print("GET", buy_url)
    print(
        "\nPOST https://market.csgo.com/api/v2/add-to-sale"
        f"?key=***REDACTED***&id=<inventory_id>&price=<{int(mcs[1] * rate * 100) if mcs and rate else '...'}>"
        "&cur=RUB"
    )
    print("\nПокупка не отправлена. Ни один доллар не потрачен.")
