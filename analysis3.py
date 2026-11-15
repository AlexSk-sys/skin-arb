import json
import statistics
from collections import Counter

ROWS = json.loads(
    open(r"C:\Users\AgentPC\skin-arb\last_scan3.json", encoding="utf-8").read()
)

# Keep only plausible spreads, then one best route per item to avoid
# counting the same inventory twice.
best = {}
for r in ROWS:
    if r["margin"] > 0.60:
        continue
    if r["item"] not in best or r["profit"] > best[r["item"]]["profit"]:
        best[r["item"]] = r

items = list(best.values())
cap5 = sum(r["profit"] * min(r["vol_buy"], r["vol_sell"], 5) for r in items)
capital5 = sum(r["buy"] * min(r["vol_buy"], r["vol_sell"], 5) for r in items)
median = statistics.median(r["margin"] for r in items)

print(f"уникальных предметов: {len(items)}")
print(f"медианная маржа: {median * 100:.2f}%")
print(f"ёмкость по 5 шт: ${cap5:,.0f}")
print(f"капитал под неё: ${capital5:,.0f}")
print(f"доходность цикла: {cap5 / capital5 * 100:.2f}%")
print("\nмаршруты:")
for (b, s), n in Counter((r["buy_src"], r["sell_src"]) for r in items).most_common():
    print(f"  {b:>12} -> {s:<12} {n:>4} предметов")

print("\nтоп-15 после дедупликации:")
print(f"{'item':<44} {'route':<26} {'buy':>8} {'net':>7} {'mrg':>6} {'vol':>9}")
for r in sorted(items, key=lambda x: x["profit"] * min(x["vol_buy"], x["vol_sell"], 5), reverse=True)[:15]:
    print(
        f"{r['item'][:44]:<44} {r['buy_src'] + '->' + r['sell_src']:<26} "
        f"{r['buy']:>8.2f} {r['profit']:>7.2f} {r['margin']*100:>5.1f}% "
        f"{r['vol_buy']:>4}/{r['vol_sell']:<4}"
    )
