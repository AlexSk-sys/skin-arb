"""Three-marketplace CS2 arbitrage scanner: Waxpeer, Market.CSGO, CSFloat.

For every item priced on at least two marketplaces it evaluates all ordered
buy->sell pairs after the seller commission and a 2% undercut.

CSFloat needs an API key (HKCU\\Environment\\CSFLOAT_API_KEY). It is queried
per item name, so only a liquid candidate subset is pulled.
"""

from __future__ import annotations

import json
import os
import time
import winreg
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
CACHE.mkdir(exist_ok=True)

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

FEES = {"waxpeer": 0.05, "market_csgo": 0.05, "csfloat": 0.02}
UNDERCUT = 0.02
MIN_PRICE = 3.0
MIN_VOLUME = 10
MAX_CSFLOAT_NAMES = 120
CSFLOAT_PAUSE = 0.8
CACHE_TTL = 600


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


def cached(name: str, url: str, params: dict | None = None) -> dict:
    path = CACHE / f"{name}.json"
    if path.exists() and time.time() - path.stat().st_mtime < CACHE_TTL:
        return json.loads(path.read_text(encoding="utf-8"))
    r = requests.get(url, params=params, headers=UA, timeout=90)
    r.raise_for_status()
    data = r.json()
    path.write_text(json.dumps(data), encoding="utf-8")
    return data


def fetch_waxpeer() -> dict[str, dict]:
    d = cached("waxpeer", "https://api.waxpeer.com/v1/prices", {"game": "csgo"})
    out = {}
    for it in d.get("items", []):
        name = it.get("name")
        if name:
            out[name] = {"ask": it["min"] / 1000.0, "vol": int(it.get("count") or 0)}
    return out


def fetch_market_csgo() -> dict[str, dict]:
    d = cached("market_csgo", "https://market.csgo.com/api/v2/prices/USD.json")
    out = {}
    for it in d.get("items", []):
        name = it.get("market_hash_name")
        try:
            price = float(it["price"])
        except (KeyError, TypeError, ValueError):
            continue
        if name:
            out[name] = {"ask": price, "vol": int(it.get("volume") or 0)}
    return out


def fetch_csfloat(names: list[str]) -> dict[str, dict]:
    """Query CSFloat per item. Cache is flushed every 20 requests so an
    interrupted run keeps everything it already paid for."""
    path = CACHE / "csfloat_items.json"
    cache: dict[str, dict] = {}
    if path.exists():
        cache = json.loads(path.read_text(encoding="utf-8"))

    headers = {**UA, "Authorization": get_key("CSFLOAT_API_KEY")}
    out: dict[str, dict] = {}
    fetched = 0

    def flush() -> None:
        path.write_text(json.dumps(cache), encoding="utf-8")

    for name in names:
        if name in cache:
            out[name] = cache[name]
            continue
        if fetched >= MAX_CSFLOAT_NAMES:
            break

        r = None
        for _attempt in range(2):
            try:
                r = requests.get(
                    "https://csfloat.com/api/v1/listings",
                    params={
                        "limit": 1,
                        "sort_by": "lowest_price",
                        "type": "buy_now",
                        "market_hash_name": name,
                    },
                    headers=headers,
                    timeout=30,
                )
            except requests.RequestException:
                r = None
                break
            if r.status_code == 429:
                time.sleep(10)
                continue
            break

        fetched += 1
        if fetched % 20 == 0:
            flush()
            print(f"    csfloat: {fetched} запросов, в кэше {len(cache)}", flush=True)

        if r is None or r.status_code != 200:
            continue
        data = r.json().get("data", [])
        if not data:
            continue
        row = data[0]
        rec = {
            "ask": row["price"] / 100.0,
            "vol": int(row.get("reference", {}).get("quantity") or 1),
        }
        out[name] = rec
        cache[name] = rec
        time.sleep(CSFLOAT_PAUSE)

    flush()
    return out


def build_table(wax, mcs, csf) -> dict[str, dict]:
    table: dict[str, dict] = {}
    for name in set(wax) | set(mcs) | set(csf):
        table[name] = {}
        if name in wax:
            table[name]["waxpeer"] = wax[name]
        if name in mcs:
            table[name]["market_csgo"] = mcs[name]
        if name in csf:
            table[name]["csfloat"] = csf[name]
    return table


def evaluate(table: dict[str, dict]) -> list[dict]:
    rows = []
    for name, srcs in table.items():
        if len(srcs) < 2:
            continue
        for buy_src, buy in srcs.items():
            if buy["ask"] < MIN_PRICE or buy["vol"] < MIN_VOLUME:
                continue
            for sell_src, sell in srcs.items():
                if sell_src == buy_src or sell["vol"] < MIN_VOLUME:
                    continue
                proceeds = sell["ask"] * (1 - UNDERCUT) * (1 - FEES[sell_src])
                profit = proceeds - buy["ask"]
                if profit <= 0:
                    continue
                rows.append(
                    {
                        "item": name,
                        "buy_src": buy_src,
                        "sell_src": sell_src,
                        "buy": buy["ask"],
                        "sell": sell["ask"],
                        "profit": profit,
                        "margin": profit / buy["ask"],
                        "vol_buy": buy["vol"],
                        "vol_sell": sell["vol"],
                        "depth": profit * min(buy["vol"], sell["vol"], 5),
                    }
                )
    rows.sort(key=lambda r: r["profit"] * min(r["vol_buy"], r["vol_sell"], 5), reverse=True)
    return rows


def main() -> None:
    print("Загружаю Waxpeer и Market.CSGO...")
    wax = fetch_waxpeer()
    mcs = fetch_market_csgo()
    print(f"  waxpeer {len(wax)}, market.csgo {len(mcs)}")

    common = set(wax) & set(mcs)
    liquid = [
        n
        for n in common
        if wax[n]["ask"] >= MIN_PRICE
        and mcs[n]["ask"] >= MIN_PRICE
        and wax[n]["vol"] >= MIN_VOLUME
        and mcs[n]["vol"] >= MIN_VOLUME
    ]
    liquid.sort(key=lambda n: -min(wax[n]["vol"], mcs[n]["vol"]))
    names = liquid[:MAX_CSFLOAT_NAMES]
    print(f"  опрашиваю CSFloat по {len(names)} ликвидным предметам...")
    csf = fetch_csfloat(names)
    print(f"  csfloat ответил по {len(csf)}")

    table = build_table(wax, mcs, csf)
    rows = evaluate(table)

    print(f"\nНайдено пар с положительным спредом: {len(rows)}")
    print(f"{'item':<46} {'buy':>12} {'sell':>12} {'net $':>8} {'margin':>7} {'vol':>10}")
    for r in rows[:40]:
        print(
            f"{r['item'][:46]:<46} {r['buy_src']:>12} {r['sell_src']:>12} "
            f"{r['profit']:>8.2f} {r['margin'] * 100:>6.1f}% "
            f"{r['vol_buy']:>4}/{r['vol_sell']:<5}"
        )

    if rows:
        rows5 = [r for r in rows if r["margin"] <= 0.60]
        cap = sum(r["depth"] for r in rows5)
        med = sorted(r["margin"] for r in rows5)[len(rows5) // 2]
        print(
            f"\nБез аномалий (>60% отброшено): {len(rows5)} пар, "
            f"медиана {med * 100:.1f}%, ёмкость по 5 шт ${cap:,.0f}"
        )

    (HERE / "last_scan3.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("\nПолный результат: last_scan3.json")


if __name__ == "__main__":
    main()
