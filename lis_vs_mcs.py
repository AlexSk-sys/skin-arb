"""Compare LIS-SKINS cheapest asks against Market.CSGO asks.

Buy on LIS-SKINS (Russian cards / SBP), sell on Market.CSGO (RUB withdrawal).
Both platforms are reachable from Russia without a foreign card.
"""

from __future__ import annotations

import json
from pathlib import Path

import scan3  # type: ignore

HERE = Path(__file__).resolve().parent
UNDERCUT = 0.02
MCS_FEE = 0.05
MAX_UNIT = 10.0
MIN_MARGIN = 0.10
MIN_UNITS = 5

data = json.loads((HERE / "lis_prices.json").read_text(encoding="utf-8"))
lis = data["items"]
mcs = scan3.fetch_market_csgo()

rows = []
for name, row in lis.items():
    price, count = row[0], row[1]
    lis_id = row[2] if len(row) > 2 else None
    other = mcs.get(name)
    if not other or price <= 0:
        continue
    sell = other["ask"]
    if other["vol"] < MIN_UNITS or count < MIN_UNITS:
        continue
    proceeds = sell * (1 - UNDERCUT) * (1 - MCS_FEE)
    profit = proceeds - price
    if profit <= 0:
        continue
    margin = profit / price
    if margin < MIN_MARGIN or margin > 0.60 or price > MAX_UNIT:
        continue
    rows.append(
        {
            "item": name,
            "buy_lis": round(price, 2),
            "sell_mcs": round(sell, 2),
            "profit": round(profit, 2),
            "margin": round(margin, 3),
            "lis_count": count,
            "mcs_vol": other["vol"],
            "lis_id": lis_id,
        }
    )

rows.sort(key=lambda r: r["profit"], reverse=True)
print(f"LIS-SKINS предметов: {len(lis):,}")
print(f"кандидатов LIS -> Market.CSGO (до ${MAX_UNIT:.0f}, маржа >= {MIN_MARGIN*100:.0f}%): {len(rows)}\n")
print(f"{'item':<44} {'lis_id':>11} {'buy':>7} {'sell':>7} {'net':>7} {'mrg':>6}")
for r in rows[:25]:
    print(
        f"{r['item'][:44]:<44} {str(r['lis_id']):>11} ${r['buy_lis']:>6.2f} ${r['sell_mcs']:>6.2f} "
        f"${r['profit']:>6.2f} {r['margin']*100:>5.1f}%"
    )

if rows:
    budget = 10.0
    spent = 0.0
    picked = []
    for r in rows:
        if len(picked) >= 3:
            break
        if spent + r["buy_lis"] > budget:
            continue
        picked.append(r)
        spent += r["buy_lis"]
    print(
        f"\nна $10: {len(picked)} позиций, вложения ${spent:.2f}, "
        f"ожидаемая прибыль ${sum(x['profit'] for x in picked):.2f}"
    )
    for r in picked:
        print(
            f"  {r['item']} | LIS id {r['lis_id']} | "
            f"${r['buy_lis']:.2f} -> ${r['sell_mcs']:.2f}"
        )
