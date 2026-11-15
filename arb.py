"""Cross-marketplace CS2 skin arbitrage scanner.

Sources (public, no auth):
  - Waxpeer      https://api.waxpeer.com/v1/prices?game=csgo
  - Market.CSGO  https://market.csgo.com/api/v2/prices/USD.json
  - Steam        https://steamcommunity.com/market/priceoverview/ (reference only, rate-limited)

The scanner compares lowest asks and computes what you would actually keep if you
bought on one marketplace and sold on the other, after seller commission and a
2% undercut to sit at the top of the destination book.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
CACHE.mkdir(exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

# Seller commission per marketplace (fraction of sale price).
FEES = {
    "waxpeer": 0.05,
    "market_csgo": 0.05,
    "steam": 0.15,
}

UNDERCUT = 0.02      # sit 2% below the destination's lowest ask
MIN_PRICE_USD = 1.0  # below this, fixed fees and rounding eat everything
MIN_VOLUME = 5       # need at least this many listings on both sides
CACHE_TTL = 300      # seconds

# Spreads above this are almost always stale listings or name mismatches,
# not executable arbitrage. Kept separate and flagged.
MARGIN_FLOOR = 0.03
MARGIN_CEILING = 0.60
MIN_VOL_LIQUID = 20  # volume required on the buy side for an "executable" row


def _cached(name: str, url: str, params: dict | None = None) -> dict:
    path = CACHE / f"{name}.json"
    if path.exists() and time.time() - path.stat().st_mtime < CACHE_TTL:
        return json.loads(path.read_text(encoding="utf-8"))
    r = requests.get(url, params=params, headers=UA, timeout=90)
    r.raise_for_status()
    data = r.json()
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def fetch_waxpeer() -> dict[str, dict]:
    d = _cached("waxpeer", "https://api.waxpeer.com/v1/prices", {"game": "csgo"})
    out = {}
    for it in d.get("items", []):
        name = it.get("name")
        if not name:
            continue
        # Waxpeer reports prices in thousandths of a USD (verified: median
        # waxpeer/1000 vs Market.CSGO ask = 0.97 across 15.5k items).
        out[name] = {
            "ask": it["min"] / 1000.0,
            "steam": (it.get("steam_price") or 0) / 1000.0,
            "volume": int(it.get("count") or 0),
        }
    return out


def fetch_market_csgo() -> dict[str, dict]:
    d = _cached("market_csgo", "https://market.csgo.com/api/v2/prices/USD.json")
    out = {}
    for it in d.get("items", []):
        name = it.get("market_hash_name")
        if not name:
            continue
        try:
            price = float(it["price"])
        except (KeyError, TypeError, ValueError):
            continue
        out[name] = {"ask": price, "volume": int(it.get("volume") or 0)}
    return out


def net_sale(ask_dest: float, fee: float) -> float:
    """What you keep selling into `ask_dest` after undercut and commission."""
    return ask_dest * (1.0 - UNDERCUT) * (1.0 - fee)


def scan(a: str, b: str, src_a: dict, src_b: dict) -> list[dict]:
    rows = []
    for name, da in src_a.items():
        db = src_b.get(name)
        if not db:
            continue
        buy, sell_at = da["ask"], db["ask"]
        if buy < MIN_PRICE_USD or da["volume"] < MIN_VOLUME or db["volume"] < MIN_VOLUME:
            continue
        proceeds = net_sale(sell_at, FEES[b])
        profit = proceeds - buy
        if profit <= 0:
            continue
        rows.append(
            {
                "item": name,
                "buy_at": a,
                "sell_at": b,
                "buy": buy,
                "sell": sell_at,
                "proceeds": proceeds,
                "profit": profit,
                "margin": profit / buy,
                "vol_buy": da["volume"],
                "vol_sell": db["volume"],
                "depth_usd": min(da["volume"], db["volume"]) * profit,
            }
        )
    rows.sort(key=lambda r: r["profit"], reverse=True)
    return rows


def steam_gap(src: dict, name_key: str = "ask") -> list[dict]:
    """Third-party ask vs Steam reference price after Steam's 15% commission.

    Selling on Steam yields Steam wallet balance, not cash — listed separately.
    """
    rows = []
    for name, d in src.items():
        steam = d.get("steam") or 0
        if steam < MIN_PRICE_USD or d["volume"] < MIN_VOLUME:
            continue
        proceeds = net_sale(steam, FEES["steam"])
        profit = proceeds - d[name_key]
        if profit > 0:
            rows.append({"item": name, "buy": d[name_key], "steam": steam,
                         "proceeds": proceeds, "profit": profit,
                         "margin": profit / d[name_key], "vol": d["volume"]})
    rows.sort(key=lambda r: r["profit"], reverse=True)
    return rows


def classify(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Split positive spreads into plausible and likely-stale buckets."""
    executable = [
        r
        for r in rows
        if MARGIN_FLOOR <= r["margin"] <= MARGIN_CEILING
        and r["vol_buy"] >= MIN_VOL_LIQUID
        and r["vol_sell"] >= MIN_VOL_LIQUID
    ]
    stale = [r for r in rows if r["margin"] > MARGIN_CEILING]
    return executable, stale


def show(title: str, rows: list[dict], n: int = 25) -> None:
    print(f"\n{'=' * 112}\n{title}  ({len(rows)} шт.)\n{'=' * 112}")
    if not rows:
        print("  нет кандидатов при текущих комиссиях и фильтрах")
        return
    print(f"{'#':>3}  {'item':<50} {'buy $':>9} {'sell $':>9} {'net $':>9} {'margin':>7} {'vol':>5}")
    for i, r in enumerate(rows[:n], 1):
        sell = r.get("sell", r.get("steam", 0.0))
        print(
            f"{i:>3}  {r['item'][:50]:<50} {r['buy']:>9.2f} {sell:>9.2f} "
            f"{r['profit']:>9.2f} {r['margin'] * 100:>6.1f}% {r.get('vol_buy', 0):>5}"
        )


def main() -> None:
    print("Загружаю каталоги...")
    wax = fetch_waxpeer()
    mcs = fetch_market_csgo()
    print(f"  waxpeer:      {len(wax):>6} предметов")
    print(f"  market.csgo:  {len(mcs):>6} предметов")
    print(f"  пересечение:  {len(set(wax) & set(mcs)):>6} предметов")

    w2m = scan("waxpeer", "market_csgo", wax, mcs)
    m2w = scan("market_csgo", "waxpeer", mcs, wax)

    for label, rows in (("Waxpeer -> Market.CSGO", w2m), ("Market.CSGO -> Waxpeer", m2w)):
        ex, stale = classify(rows)
        show(
            f"{label}: исполнимые спреды (маржа 3-60%, объём >= {MIN_VOL_LIQUID} с обеих сторон)",
            ex,
        )
        print(f"  отброшено как устаревшие лоты (маржа >60%): {len(stale)}")

    print("\nСПРАВОЧНО: поле Waxpeer.steam_price — кэш и часто устаревшее;")
    print("в расчёт арбитража не включено, потому что маржа по нему завышена в разы.")

    (HERE / "last_scan.json").write_text(
        json.dumps(
            {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "waxpeer_to_market_csgo": w2m,
                "market_csgo_to_waxpeer": m2w,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("\nПолный результат: last_scan.json")


if __name__ == "__main__":
    main()
