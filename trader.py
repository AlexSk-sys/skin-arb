"""Core trading logic for the skin-arbitrage agent.

Starts in paper mode: every buy/sell is recorded but no money moves.
Live mode is gated behind explicit confirmation and platform trade keys.

Hard limits live in trader_config.json and are enforced on every action.
A file named STOP in this directory freezes all trading immediately.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.parse
import uuid
import winreg

import requests
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "trader_config.json"
STATE_PATH = HERE / "trader_state.json"
STOP_PATH = HERE / "STOP"

sys.path.insert(0, str(HERE))
import scan3  # type: ignore  # noqa: E402

DEFAULT_CONFIG = {
    "mode": "paper",
    "max_trade_usd": 25.0,
    "max_total_usd": 100.0,
    "min_margin": 0.10,
    "max_price": 25.0,
    "min_volume": 20,
    "max_positions": 5,
    "fees": {"waxpeer": 0.05, "market_csgo": 0.05, "csfloat": 0.02},
    "undercut": 0.02,
    "include_csfloat": False,
}

LIVE_CONFIRMATION = "I UNDERSTAND THE RISK"
LIVE_ENV_KEYS = ("WAXPEER_API_KEY", "MARKET_CSGO_API_KEY")


class AgentError(RuntimeError):
    """User-facing refusal; the message is safe to show in chat."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_config() -> dict:
    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    else:
        cfg = dict(DEFAULT_CONFIG)
        CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return cfg


def save_config(cfg: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"positions": [], "realized": 0.0, "created_at": _now()}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def is_stopped() -> bool:
    return STOP_PATH.exists()


def require_running() -> None:
    if is_stopped():
        raise AgentError("Торговля остановлена: удали STOP, чтобы продолжить.")


def committed(state: dict) -> float:
    return sum(p["buy_price"] * p["qty"] for p in state["positions"] if p["status"] == "open")


def open_positions(state: dict) -> list[dict]:
    return [p for p in state["positions"] if p["status"] == "open"]


def _fetch_table(include_csfloat: bool) -> dict:
    wax = scan3.fetch_waxpeer()
    mcs = scan3.fetch_market_csgo()
    csf = {}
    if include_csfloat:
        common = set(wax) & set(mcs)
        liquid = [
            n
            for n in common
            if wax[n]["ask"] >= scan3.MIN_PRICE
            and mcs[n]["ask"] >= scan3.MIN_PRICE
            and wax[n]["vol"] >= scan3.MIN_VOLUME
            and mcs[n]["vol"] >= scan3.MIN_VOLUME
        ]
        liquid.sort(key=lambda n: -min(wax[n]["vol"], mcs[n]["vol"]))
        csf = scan3.fetch_csfloat(liquid[:40])
    return scan3.build_table(wax, mcs, csf)


def scan(limit: int = 15, max_price: float | None = None, min_margin: float | None = None) -> list[dict]:
    cfg = load_config()
    table = _fetch_table(cfg.get("include_csfloat", False))
    rows = scan3.evaluate(table)
    floor = cfg["min_margin"] if min_margin is None else min_margin
    ceiling_price = cfg["max_price"] if max_price is None else max_price
    out = [
        r
        for r in rows
        if r["margin"] >= floor
        and r["margin"] <= 0.60
        and r["buy"] <= ceiling_price
        and r["vol_buy"] >= cfg["min_volume"]
        and r["vol_sell"] >= cfg["min_volume"]
    ]
    return out[:limit]


def plan(capital: float | None = None) -> list[dict]:
    cfg = load_config()
    state = load_state()
    free = cfg["max_total_usd"] - committed(state)
    budget = min(free, capital if capital is not None else free)
    if budget <= 0:
        raise AgentError("Лимит капитала исчерпан: все позиции открыты.")

    picks: list[dict] = []
    spent = 0.0
    for r in scan(limit=200):
        if len(picks) + len(open_positions(state)) >= cfg["max_positions"]:
            break
        price = r["buy"]
        if price > cfg["max_trade_usd"]:
            continue
        if spent + price > budget:
            continue
        picks.append(
            {
                "item": r["item"],
                "buy_src": r["buy_src"],
                "sell_src": r["sell_src"],
                "buy_price": round(price, 2),
                "target_sell": round(r["sell"], 2),
                "expected_profit": round(r["profit"], 2),
                "margin": round(r["margin"], 3),
                "vol_buy": r["vol_buy"],
                "vol_sell": r["vol_sell"],
            }
        )
        spent += price
    return picks


def buy(item: str, confirm: str = "") -> dict:
    require_running()
    cfg = load_config()
    state = load_state()

    match = next((r for r in scan(limit=300, max_price=cfg["max_price"]) if r["item"] == item), None)
    if match is None:
        raise AgentError(f"Предмет не найден в текущем скане: {item}")

    if match["buy"] > cfg["max_trade_usd"]:
        raise AgentError(
            f"Цена ${match['buy']:.2f} выше лимита на сделку ${cfg['max_trade_usd']:.2f}"
        )
    if committed(state) + match["buy"] > cfg["max_total_usd"]:
        raise AgentError(
            f"Сделка превысит общий лимит ${cfg['max_total_usd']:.2f}"
        )
    if len(open_positions(state)) >= cfg["max_positions"]:
        raise AgentError(f"Достигнут лимит открытых позиций: {cfg['max_positions']}")

    live_result = None
    if cfg["mode"] == "live":
        if confirm != LIVE_CONFIRMATION:
            raise AgentError(f"Боевая покупка требует confirm='{LIVE_CONFIRMATION}'")
        live_result = _live_buy(match)

    pos = {
        "id": "pos_" + uuid.uuid4().hex[:8],
        "item": match["item"],
        "buy_src": match["buy_src"],
        "sell_src": match["sell_src"],
        "buy_price": round(match["buy"], 2),
        "target_sell": round(match["sell"], 2),
        "qty": 1,
        "status": "open",
        "mode": cfg["mode"],
        "opened_at": _now(),
        "closed_at": None,
        "sold_price": None,
        "pnl": None,
        "live_result": live_result,
    }
    state["positions"].append(pos)
    save_state(state)
    return pos


def sell(position_id: str, sold_price: float) -> dict:
    require_running()
    cfg = load_config()
    state = load_state()
    pos = next((p for p in state["positions"] if p["id"] == position_id), None)
    if pos is None:
        raise AgentError(f"Позиция не найдена: {position_id}")
    if pos["status"] != "open":
        raise AgentError(f"Позиция уже закрыта: {position_id}")

    if cfg["mode"] == "live":
        _live_sell(pos)

    fee = cfg["fees"].get(pos["sell_src"], 0.05)
    proceeds = sold_price * (1 - cfg["undercut"]) * (1 - fee)
    pnl = proceeds - pos["buy_price"] * pos["qty"]

    pos["status"] = "closed"
    pos["closed_at"] = _now()
    pos["sold_price"] = round(sold_price, 2)
    pos["proceeds"] = round(proceeds, 2)
    pos["pnl"] = round(pnl, 2)
    state["realized"] = round(state.get("realized", 0.0) + pnl, 2)
    save_state(state)
    return pos


def report() -> dict:
    state = load_state()
    open_pos = open_positions(state)
    closed = [p for p in state["positions"] if p["status"] == "closed"]
    wins = [p for p in closed if (p.get("pnl") or 0) > 0]
    return {
        "mode": load_config()["mode"],
        "stopped": is_stopped(),
        "open_positions": len(open_pos),
        "committed_usd": round(committed(state), 2),
        "closed_trades": len(closed),
        "win_rate": round(len(wins) / len(closed), 3) if closed else None,
        "realized_usd": round(state.get("realized", 0.0), 2),
    }


def _has_key(name: str) -> bool:
    """Keys may live in the process env or in HKCU\\Environment."""
    if os.environ.get(name):
        return True
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            winreg.QueryValueEx(key, name)
            return True
    except OSError:
        return False


def set_live(enabled: bool, confirmation: str = "") -> dict:
    cfg = load_config()
    if enabled and confirmation != LIVE_CONFIRMATION:
        raise AgentError(f"Для включения боевого режима передай confirmation='{LIVE_CONFIRMATION}'")
    if enabled:
        missing = [k for k in LIVE_ENV_KEYS if not _has_key(k)]
        if missing:
            raise AgentError(
                "Нет ключей для боевой торговли: " + ", ".join(missing) +
                ". Без них агент может только симулировать."
            )
    cfg["mode"] = "live" if enabled else "paper"
    save_config(cfg)
    return {"mode": cfg["mode"]}


def stop() -> str:
    STOP_PATH.write_text(_now(), encoding="utf-8")
    return "STOP установлен. Все действия заблокированы до удаления файла."


def resume() -> str:
    if STOP_PATH.exists():
        STOP_PATH.unlink()
    return "STOP снят."


WAXPEER_API = "https://api.waxpeer.com"


def _waxpeer_account() -> dict:
    r = requests.get(
        f"{WAXPEER_API}/v1/user",
        params={"api": scan3.get_key("WAXPEER_API_KEY")},
        timeout=30,
    )
    data = r.json()
    if not data.get("success"):
        raise AgentError(f"Waxpeer не подтвердил ключ: {data}")
    return data["user"]


def _waxpeer_listing(name: str) -> tuple[str, int] | None:
    """Cheapest live listing for an exact name: (item_id, price in milli-USD)."""
    r = requests.get(
        f"{WAXPEER_API}/v2/search-items-by-name",
        params={"api": scan3.get_key("WAXPEER_API_KEY"), "name": name},
        timeout=30,
    )
    items = (r.json().get("items") or {}).get(name) or []
    if not items:
        return None
    best = min(items, key=lambda x: x.get("price") or 10**12)
    return str(best["item_id"]), int(best["price"])


def _live_buy(match: dict) -> dict:
    account = _waxpeer_account()
    partner = account.get("id64")
    if not partner:
        raise AgentError("Waxpeer не вернул Steam ID64 аккаунта")

    listing = _waxpeer_listing(match["item"])
    if not listing:
        raise AgentError(f"Лот не найден на Waxpeer: {match['item']}")
    item_id, price_milli = listing
    live_price = price_milli / 1000
    if live_price > match["buy"] * 1.02:
        raise AgentError(
            f"Цена изменилась: в скане ${match['buy']:.2f}, сейчас ${live_price:.2f}. Покупка отменена."
        )

    trade_url = scan3.get_key("STEAM_TRADE_URL")
    token = urllib.parse.parse_qs(urllib.parse.urlparse(trade_url).query).get("token", [""])[0]
    if not token:
        raise AgentError("В STEAM_TRADE_URL нет параметра token")

    r = requests.get(
        f"{WAXPEER_API}/v1/buy-one-p2p",
        params={
            "api": scan3.get_key("WAXPEER_API_KEY"),
            "item_id": item_id,
            "price": price_milli,
            "partner": partner,
            "token": token,
            "allow_trade_locked": 1,
        },
        timeout=90,
    )
    data = r.json()
    if not data.get("success"):
        raise AgentError(f"Waxpeer отклонил покупку: {data}")
    return data


def _live_sell(_pos: dict) -> None:
    raise AgentError(
        "Боевая продажа не реализована: нужны ключи площадки и Steam trade URL."
    )
