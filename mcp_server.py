r"""MCP server exposing the skin-arbitrage agent.

Run:  python C:\Users\AgentPC\skin-arb\mcp_server.py
Transport: stdio. Register it in Claude Code with `claude mcp add`.

Safety model:
  - paper mode by default: trades are recorded, no money moves;
  - hard limits in trader_config.json;
  - STOP file freezes every action;
  - live mode needs an explicit confirmation phrase plus platform trade keys.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from mcp.server.mcpserver import MCPServer  # type: ignore  # noqa: E402

import trader  # type: ignore  # noqa: E402

mcp = MCPServer(
    name="skin-trader",
    instructions=(
        "Агент арбитража скинов CS2 между Waxpeer, Market.CSGO и CSFloat. "
        "По умолчанию paper-режим: сделки записываются, деньги не тратятся. "
        "Боевой режим включается только через set_live с подтверждением."
    ),
)


def _safe(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except trader.AgentError as exc:
        return {"error": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"error": f"{type(exc).__name__}: {exc}"}


@mcp.tool(description="Режим, лимиты, открытые позиции и реализованный P&L.")
def status() -> dict:
    cfg = trader.load_config()
    state = trader.load_state()
    return {
        "mode": cfg["mode"],
        "stopped": trader.is_stopped(),
        "limits": {
            "max_trade_usd": cfg["max_trade_usd"],
            "max_total_usd": cfg["max_total_usd"],
            "max_price": cfg["max_price"],
            "min_margin": cfg["min_margin"],
            "max_positions": cfg["max_positions"],
        },
        "open_positions": len(trader.open_positions(state)),
        "committed_usd": round(trader.committed(state), 2),
        "realized_usd": state.get("realized", 0.0),
    }


@mcp.tool(description="Сканирует живые цены и возвращает текущие арбитражные связки.")
def scan(
    limit: int = 15, max_price: float | None = None, min_margin: float | None = None
) -> list | dict:
    return _safe(trader.scan, limit=limit, max_price=max_price, min_margin=min_margin)


@mcp.tool(description="Предлагает набор сделок под указанный капитал, не исполняя их.")
def plan(capital: float | None = None) -> list | dict:
    return _safe(trader.plan, capital=capital)


@mcp.tool(
    description=(
        "Покупает предмет. В paper-режиме только запись. В live нужен "
        "confirm='I UNDERSTAND THE RISK'."
    )
)
def buy(item: str, confirm: str = "") -> dict:
    return _safe(trader.buy, item, confirm)


@mcp.tool(description="Закрывает позицию по цене продажи и считает P&L.")
def sell(position_id: str, sold_price: float) -> dict:
    return _safe(trader.sell, position_id, sold_price)


@mcp.tool(description="Список позиций: открытые и закрытые с результатом.")
def positions() -> dict:
    state = trader.load_state()
    return {
        "open": trader.open_positions(state),
        "closed": [p for p in state["positions"] if p["status"] == "closed"],
        "realized_usd": state.get("realized", 0.0),
    }


@mcp.tool(description="Сводный отчёт: сделки, win rate, реализованный результат.")
def report() -> dict:
    return trader.report()


@mcp.tool(description="Меняет лимиты риска. Аргументы необязательны.")
def set_limits(
    max_trade_usd: float | None = None,
    max_total_usd: float | None = None,
    max_price: float | None = None,
    min_margin: float | None = None,
    max_positions: int | None = None,
) -> dict:
    cfg = trader.load_config()
    if max_trade_usd is not None:
        cfg["max_trade_usd"] = max_trade_usd
    if max_total_usd is not None:
        cfg["max_total_usd"] = max_total_usd
    if max_price is not None:
        cfg["max_price"] = max_price
    if min_margin is not None:
        cfg["min_margin"] = min_margin
    if max_positions is not None:
        cfg["max_positions"] = max_positions
    trader.save_config(cfg)
    return {"limits": cfg}


@mcp.tool(
    description=(
        "Переключает paper/live. Для live передай confirmation='I UNDERSTAND THE RISK' "
        "и убедись, что заданы WAXPEER_API_KEY и MARKET_CSGO_API_KEY."
    )
)
def set_live(enabled: bool, confirmation: str = "") -> dict:
    return _safe(trader.set_live, enabled, confirmation)


@mcp.tool(description="Немедленно замораживает все действия агента.")
def stop() -> str:
    return trader.stop()


@mcp.tool(description="Снимает заморозку.")
def resume() -> str:
    return trader.resume()


if __name__ == "__main__":
    mcp.run()
