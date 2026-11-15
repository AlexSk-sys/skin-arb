"""Closed-loop arbitrage runner.

Each step:
  1. closes paper positions older than hold_hours at their target price;
  2. scans LIS-SKINS / Market.CSGO / Waxpeer;
  3. buys the best opportunity while free cash and position slots remain;
  4. writes state and a one-line log record.

Paper by default. Live execution is deliberately not wired here yet: the LIS
buy side is manual and the Market.CSGO order path still needs ID verification.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import scan3  # type: ignore

HERE = Path(__file__).resolve().parent
STATE = HERE / "loop_state.json"
CONFIG = HERE / "loop_config.json"
LOG = HERE / "loop.log"

UNDERCUT = 0.02
SELL_FEES = {"mcs": 0.05, "wax": 0.05, "csf": 0.02}

DEFAULT_CONFIG = {
    "capital": 10.0,
    "min_margin": 0.08,
    "max_margin": 0.35,
    "min_sell_vol": 15,
    "max_positions": 3,
    "min_trade": 1.0,
    "max_trade": 5.0,
    "hold_hours": 72,
    "mode": "margin",  # "margin" = manual LIS buys, "auto" = API-only loop
    "execution": "paper",  # "paper" | "live"
    "max_queue": 5,
    # Auto mode may only buy where the user can actually fund an account.
    "auto_buy_sources": ["mcs"],
}


def now() -> datetime:
    return datetime.now(timezone.utc)


def load_json(path: Path, default):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    stored = load_json(CONFIG, None)
    if stored:
        cfg.update(stored)
    save_json(CONFIG, cfg)
    return cfg


def load_state(cfg: dict) -> dict:
    state = load_json(STATE, None)
    if state is None:
        state = {
            "cash": cfg["capital"],
            "positions": [],
            "history": [],
            "buy_queue": [],
            "started": now().isoformat(),
        }
        save_json(STATE, state)
    state.setdefault("buy_queue", [])
    return state


def build_sources() -> dict[str, dict[str, dict]]:
    lis = json.loads((HERE / "lis_prices.json").read_text(encoding="utf-8"))["items"]
    mcs = scan3.fetch_market_csgo()
    wax = scan3.fetch_waxpeer()
    sources: dict[str, dict[str, dict]] = {}
    for name, row in lis.items():
        sources.setdefault(name, {})["lis"] = {"ask": row[0], "vol": row[1]}
    for name, d in mcs.items():
        sources.setdefault(name, {})["mcs"] = d
    for name, d in wax.items():
        sources.setdefault(name, {})["wax"] = d
    return sources


def opportunities(sources: dict, cfg: dict) -> list[dict]:
    rows = []
    for name, srcs in sources.items():
        for buy_src, buy in srcs.items():
            if buy["ask"] <= 0:
                continue
            if cfg["mode"] == "auto" and buy_src not in cfg["auto_buy_sources"]:
                # Unattended runs only buy where the user can fund an account.
                continue
            for sell_src, sell in srcs.items():
                if sell_src == buy_src or sell_src == "lis" or sell["vol"] < cfg["min_sell_vol"]:
                    continue
                proceeds = sell["ask"] * (1 - UNDERCUT) * (1 - SELL_FEES[sell_src])
                profit = proceeds - buy["ask"]
                if profit <= 0:
                    continue
                margin = profit / buy["ask"]
                if cfg["min_margin"] <= margin <= cfg["max_margin"]:
                    rows.append(
                        {
                            "item": name,
                            "buy_src": buy_src,
                            "sell_src": sell_src,
                            "buy": round(buy["ask"], 2),
                            "sell": round(sell["ask"], 2),
                            "profit": round(profit, 2),
                            "margin": round(margin, 3),
                            "vol_buy": buy["vol"],
                            "vol_sell": sell["vol"],
                        }
                    )
    rows.sort(key=lambda r: r["profit"], reverse=True)
    return rows


def close_due(state: dict, cfg: dict) -> list[str]:
    closed = []
    for pos in state["positions"]:
        if pos["status"] != "open":
            continue
        age_h = (now() - datetime.fromisoformat(pos["opened_at"])).total_seconds() / 3600
        if age_h < cfg["hold_hours"]:
            continue
        proceeds = pos["target_sell"] * (1 - UNDERCUT) * (1 - SELL_FEES[pos["sell_src"]])
        pnl = proceeds - pos["buy"]
        pos["status"] = "sold"
        pos["sold_price"] = pos["target_sell"]
        pos["pnl"] = round(pnl, 2)
        pos["closed_at"] = now().isoformat()
        state["cash"] = round(state["cash"] + proceeds, 2)
        state["history"].append({"item": pos["item"], "pnl": pos["pnl"], "closed_at": pos["closed_at"]})
        closed.append(pos["item"])
    return closed


def step(cfg: dict, state: dict, rows: list[dict]) -> dict:
    closed = close_due(state, cfg)
    open_count = sum(1 for p in state["positions"] if p["status"] == "open")
    bought: list[str] = []
    queued: list[str] = []

    if cfg["mode"] == "margin":
        # Present mode: the agent never spends. It only proposes buys (manual
        # on LIS, API elsewhere) and reserves cash so the queue stays affordable.
        pending = [q for q in state["buy_queue"] if q["status"] == "pending"]
        reserved = sum(q["buy"] for q in pending)
        for r in rows:
            if len(pending) >= cfg["max_queue"]:
                break
            if r["buy"] < cfg["min_trade"] or r["buy"] > cfg["max_trade"]:
                continue
            if any(p["item"] == r["item"] and p["status"] == "open" for p in state["positions"]):
                continue
            if any(q["item"] == r["item"] for q in pending):
                continue
            if reserved + r["buy"] > state["cash"]:
                continue
            state["buy_queue"].append({**r, "status": "pending", "added_at": now().isoformat()})
            pending.append(state["buy_queue"][-1])
            reserved += r["buy"]
            queued.append(r["item"])
        return {"closed": closed, "bought": [], "queued": queued}

    # Auto mode: only API-buyable sources remain after the LIS filter.
    for r in rows:
        if open_count >= cfg["max_positions"]:
            break
        if r["buy"] < cfg["min_trade"] or r["buy"] > cfg["max_trade"]:
            continue
        if any(p["item"] == r["item"] and p["status"] == "open" for p in state["positions"]):
            continue
        if state["cash"] < r["buy"]:
            continue
        state["cash"] = round(state["cash"] - r["buy"], 2)
        state["positions"].append(
            {
                **r,
                "id": f"p{len(state['positions']) + 1}",
                "status": "open",
                "opened_at": now().isoformat(),
                "target_sell": r["sell"],
            }
        )
        open_count += 1
        bought.append(r["item"])
    return {"closed": closed, "bought": bought, "queued": queued}


def status_line(cfg: dict, state: dict) -> str:
    open_pos = [p for p in state["positions"] if p["status"] == "open"]
    unrealized = sum(
        p["target_sell"] * (1 - UNDERCUT) * (1 - SELL_FEES[p["sell_src"]]) - p["buy"] for p in open_pos
    )
    realized = sum(h["pnl"] for h in state["history"])
    return (
        f"cash ${state['cash']:.2f} | open {len(open_pos)}/{cfg['max_positions']} | "
        f"unrealized ${unrealized:.2f} | realized ${realized:.2f} | "
        f"equity ${state['cash'] + sum(p['buy'] for p in open_pos):.2f}"
    )


def run_once() -> None:
    cfg = load_config()
    state = load_state(cfg)
    rows = opportunities(build_sources(), cfg)
    result = step(cfg, state, rows)
    save_json(STATE, state)
    line = (
        f"{now().isoformat(timespec='seconds')} | mode {cfg['mode']} | opps {len(rows)} | "
        f"bought {len(result['bought'])} | queued {len(result['queued'])} | "
        f"closed {len(result['closed'])} | {status_line(cfg, state)}"
    )
    print(line)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def show_queue(state: dict) -> None:
    pending = [q for q in state["buy_queue"] if q["status"] == "pending"]
    if not pending:
        print("очередь пуста")
        return
    for q in pending:
        print(
            f"{q['item']} | {q['buy_src']}->{q['sell_src']} | "
            f"${q['buy']:.2f} -> ${q['sell']:.2f} | "
            f"+${q['profit']:.2f} ({q['margin'] * 100:.0f}%)"
        )


def confirm(item: str, price: float | None = None) -> None:
    cfg = load_config()
    state = load_state(cfg)
    q = next((x for x in state["buy_queue"] if x["item"] == item and x["status"] == "pending"), None)
    if q is None:
        print(f"нет в очереди: {item}")
        return
    buy = float(price) if price is not None else q["buy"]
    if state["cash"] < buy:
        print(f"недостаточно cash: ${state['cash']:.2f} < ${buy:.2f}")
        return
    state["cash"] = round(state["cash"] - buy, 2)
    state["positions"].append(
        {
            "item": q["item"],
            "buy_src": q["buy_src"],
            "sell_src": q["sell_src"],
            "buy": buy,
            "sell": q["sell"],
            "profit": q["profit"],
            "margin": q["margin"],
            "vol_buy": q["vol_buy"],
            "vol_sell": q["vol_sell"],
            "id": f"p{len(state['positions']) + 1}",
            "status": "open",
            "opened_at": now().isoformat(),
            "target_sell": q["sell"],
        }
    )
    q["status"] = "confirmed"
    save_json(STATE, state)
    print(f"подтверждено: {item} по ${buy:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=1800)
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--mode", choices=["margin", "auto"])
    parser.add_argument("--execution", choices=["paper", "live"])
    parser.add_argument("--queue", action="store_true")
    parser.add_argument("--confirm")
    parser.add_argument("--price", type=float)
    args = parser.parse_args()

    cfg = load_config()
    if args.mode:
        cfg["mode"] = args.mode
        save_json(CONFIG, cfg)
    if args.execution:
        cfg["execution"] = args.execution
        save_json(CONFIG, cfg)

    if args.reset and STATE.exists():
        STATE.unlink()
    if args.queue:
        show_queue(load_state(cfg))
        return
    if args.confirm:
        confirm(args.confirm, args.price)
        return
    if args.status:
        print(status_line(cfg, load_state(cfg)))
        return
    if args.once:
        run_once()
        return
    while True:
        run_once()
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
