"""All-to-all marketplace scan: LIS-SKINS, Market.CSGO, Waxpeer, CSFloat.

Evaluates every ordered buy->sell pair, one best route per item, across the
full price range, then reports capacity by price bucket and by capital.
"""

from __future__ import annotations

import json
import statistics
from collections import Counter
from pathlib import Path

import scan3  # type: ignore

HERE = Path(__file__).resolve().parent
UNDERCUT = 0.02
SELL_FEES = {"mcs": 0.05, "wax": 0.05, "csf": 0.02}
MIN_SELL_VOL = 5
MIN_MARGIN = 0.03
MAX_MARGIN = 0.60

lis = json.loads((HERE / "lis_prices.json").read_text(encoding="utf-8"))["items"]
mcs = scan3.fetch_market_csgo()
wax = scan3.fetch_waxpeer()
csf_path = HERE / "cache" / "csfloat_items.json"
csf = json.loads(csf_path.read_text(encoding="utf-8")) if csf_path.exists() else {}

sources: dict[str, dict[str, dict]] = {}
for name, row in lis.items():
    sources.setdefault(name, {})["lis"] = {"ask": row[0], "vol": row[1]}
for name, d in mcs.items():
    sources.setdefault(name, {})["mcs"] = d
for name, d in wax.items():
    sources.setdefault(name, {})["wax"] = d
for name, d in csf.items():
    sources.setdefault(name, {})["csf"] = d

best: dict[str, dict] = {}
for name, srcs in sources.items():
    for buy_src, buy in srcs.items():
        if buy["ask"] <= 0:
            continue
        for sell_src, sell in srcs.items():
            if sell_src == buy_src or sell_src == "lis":
                continue
            if sell["vol"] < MIN_SELL_VOL:
                continue
            proceeds = sell["ask"] * (1 - UNDERCUT) * (1 - SELL_FEES[sell_src])
            profit = proceeds - buy["ask"]
            if profit <= 0:
                continue
            margin = profit / buy["ask"]
            if not (MIN_MARGIN <= margin <= MAX_MARGIN):
                continue
            row = {
                "item": name,
                "buy_src": buy_src,
                "sell_src": sell_src,
                "buy": buy["ask"],
                "sell": sell["ask"],
                "profit": profit,
                "margin": margin,
                "vol_buy": buy["vol"],
                "vol_sell": sell["vol"],
            }
            if name not in best or profit > best[name]["profit"]:
                best[name] = row

rows = sorted(best.values(), key=lambda r: r["profit"], reverse=True)

print(f"предметов с положительной связкой: {len(rows)}")
print(f"маршруты: {dict(Counter((r['buy_src'], r['sell_src']) for r in rows).most_common())}\n")

print("=== ТОП-20 по абсолютной прибыли (включая дорогие) ===")
print(f"{'item':<42} {'route':<14} {'buy':>9} {'sell':>9} {'net':>8} {'mrg':>6}")
for r in rows[:20]:
    print(
        f"{r['item'][:42]:<42} {r['buy_src'] + '->' + r['sell_src']:<14} "
        f"${r['buy']:>8.2f} ${r['sell']:>8.2f} ${r['profit']:>7.2f} {r['margin']*100:>5.1f}%"
    )

print("\n=== по ценовым корзинам ===")
buckets = [0, 10, 50, 200, 1000, 10**9]
labels = ["<$10", "$10-50", "$50-200", "$200-1k", ">$1k"]
for i, label in enumerate(labels):
    part = [r for r in rows if buckets[i] <= r["buy"] < buckets[i + 1]]
    if part:
        med = statistics.median(r["margin"] for r in part)
        print(f"{label:<10} {len(part):>5} шт, медиана {med*100:>5.1f}%")

print("\n=== доходность под капитал ===")
for cap in (10, 100, 1000, 5000):
    spent = profit = 0.0
    n = 0
    for r in rows:
        if spent + r["buy"] > cap:
            continue
        spent += r["buy"]
        profit += r["profit"]
        n += 1
        if spent >= cap * 0.98:
            break
    if spent:
        print(
            f"${cap:<6} {n:>3} позиций, вложено ${spent:>8.2f}, "
            f"прибыль ${profit:>7.2f} ({profit/spent*100:>5.1f}%)"
        )

(HERE / "unified_scan.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
print("\nполный результат: unified_scan.json")
