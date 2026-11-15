import json

state = json.loads(open(r"C:\Users\AgentPC\skin-arb\loop_state.json", encoding="utf-8").read())
for p in state["positions"]:
    if p["status"] != "open":
        continue
    print(
        f"{p['item'][:44]:<44} {p['buy_src']}->{p['sell_src']}  "
        f"${p['buy']:.2f} -> ${p['target_sell']:.2f}  "
        f"+${p['profit']:.2f} ({p['margin'] * 100:.0f}%)"
    )
