#!/usr/bin/env python3
"""
strategy.py — the ceiling on "high-probability profit" with a fixed bankroll.

Any bet on an upgrader with house edge e and multiplier m wins with
p = (1-e)/m and loses the stake. This computes, exactly, the probability of
reaching a profit target +T before losing the whole bankroll B, and the EV.

Gambler's ruin:  P(hit +T) = (1 - r^b) / (1 - r^(a+b)),  r = (1-p)/p
                 a = T/s, b = B/s
"""
from __future__ import annotations
import argparse


def ruin(B: float, s: float, T: float, p: float) -> tuple[float, float, float]:
    """Return (P(success), P(ruin), EV)."""
    a, b = T / s, B / s
    r = (1 - p) / p
    if abs(r - 1) < 1e-12:
        ps = b / (a + b)                       # fair game
    else:
        ps = (1 - r ** b) / (1 - r ** (a + b))
    ps = max(0.0, min(1.0, ps))
    return ps, 1 - ps, ps * T - (1 - ps) * B


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bankroll", type=float, default=500.0)
    ap.add_argument("--edge", type=float, default=0.10, help="house edge, e.g. 0.10")
    ap.add_argument("--mult", type=float, default=2.0, help="upgrade multiplier")
    ap.add_argument("--min-bet", type=float, default=1.0)
    args = ap.parse_args()

    B, e, m = args.bankroll, args.edge, args.mult
    p = (1 - e) / m
    print(f"bankroll {B:,.0f} | edge {e:.0%} | x{m:g} -> p(win) = {p:.2%}")
    print(f"{'bet':>6} {'target':>8} {'P(profit)':>10} {'P(ruin)':>9} {'EV':>9}")
    print("-" * 48)

    targets = [1, 5, 10, 25, 50, 100, 250, 500]
    bets = [args.min_bet, 5, 10, 25, 50, 100, B]
    for s in bets:
        if s > B:
            continue
        printed = False
        for T in targets:
            if s > T:          # a bet bigger than the target overshoots; ruin model invalid
                continue
            ps, pr, ev = ruin(B, s, T, p)
            print(f"{s:>6.0f} {T:>8.0f} {ps:>9.2%} {pr:>8.2%} {ev:>9.1f}")
            printed = True
        if printed:
            print()

    # the two extremes, side by side
    ps1, _, ev1 = ruin(B, args.min_bet, 1, p)
    psall, _, evall = ruin(B, B, B, p)
    print(f"max probability : +{args.min_bet:g}₽ at {args.min_bet:g}₽/bet -> "
          f"{ps1:.2%} chance, EV {ev1:+.1f}₽, risk {B:,.0f}₽ on the tail")
    print(f"least bad EV    : one all-in -> {psall:.2%} chance of +{B:,.0f}₽, "
          f"EV {evall:+.1f}₽")


if __name__ == "__main__":
    main()
