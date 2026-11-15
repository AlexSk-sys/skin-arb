import json
import statistics

ROWS = json.loads(
    open(r"C:\Users\AgentPC\skin-arb\last_scan3.json", encoding="utf-8").read()
)

best = {}
for r in ROWS:
    if r["margin"] > 0.60:
        continue
    if r["item"] not in best or r["profit"] > best[r["item"]]["profit"]:
        best[r["item"]] = r
items = sorted(best.values(), key=lambda r: r["profit"], reverse=True)

print("=== доступно на $100 ===")
for cap in (50, 100, 200):
    spent = 0.0
    prof = 0.0
    picked = []
    for r in items:
        units = min(r["vol_buy"], r["vol_sell"], 5)
        for _ in range(units):
            if spent + r["buy"] > cap:
                break
            spent += r["buy"]
            prof += r["profit"]
            picked.append(r)
        if spent >= cap:
            break
    print(
        f"капитал ${cap}: {len(picked)} шт, прибыль ${prof:.2f} "
        f"({prof / spent * 100 if spent else 0:.1f}%), средний чек ${spent / len(picked) if picked else 0:.0f}"
    )

print("\n=== дешёвые предметы: buy <= $25, маржа >= 10%, объём >= 20 ===")
cheap = [r for r in items if r["buy"] <= 25 and r["margin"] >= 0.10 and r["vol_buy"] >= 20]
print(f"найдено: {len(cheap)}")
for r in sorted(cheap, key=lambda x: x["profit"], reverse=True)[:15]:
    print(
        f"  {r['item'][:46]:<46} {r['buy_src'] + '->' + r['sell_src']:<24} "
        f"${r['buy']:>6.2f} +${r['profit']:>5.2f} {r['margin']*100:>5.1f}% vol {r['vol_buy']}/{r['vol_sell']}"
    )

print("\n=== самый дешёвый прибыльный предмет ===")
cheapest = sorted(items, key=lambda r: r["buy"])[:10]
for r in cheapest:
    print(
        f"  {r['item'][:46]:<46} {r['buy_src'] + '->' + r['sell_src']:<24} "
        f"${r['buy']:>6.2f} +${r['profit']:>5.2f} {r['margin']*100:>5.1f}%"
    )

if cheap:
    print(f"\nмедианная маржа дешёвых: {statistics.median(r['margin'] for r in cheap)*100:.1f}%")
    print(f"медианная прибыль на штуку: ${statistics.median(r['profit'] for r in cheap):.2f}")
