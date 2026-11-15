import json

rows = json.load(open(r"C:\Users\AgentPC\skin-arb\last_scan3.json", encoding="utf-8"))
c = [
    r
    for r in rows
    if r["buy_src"] == "market_csgo"
    and r["buy"] <= 5
    and 0.10 <= r["margin"] <= 0.60
    and r["vol_buy"] >= 20
    and r["vol_sell"] >= 20
]
c.sort(key=lambda r: r["profit"], reverse=True)
print(f"кандидатов market_csgo -> waxpeer до $5: {len(c)}")
for r in c[:8]:
    print(
        f"  {r['item'][:44]:<44} ${r['buy']:.2f} -> ${r['sell']:.2f}  "
        f"+${r['profit']:.2f} ({r['margin'] * 100:.0f}%) vol {r['vol_buy']}/{r['vol_sell']}"
    )
