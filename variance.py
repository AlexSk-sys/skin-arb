#!/usr/bin/env python3
"""
variance.py — what "a friend hit 200k" actually means.

Simulates a realistic case-opening economy (RTP ~89%, right-skewed payouts)
and reports the tail: how rare the win is, and what the median player gets.
"""
import random
import statistics as st

random.seed(42)

# (probability, payout multiple of case price) — sums to ~0.891 RTP
TABLE = [
    (0.8500, 0.35),
    (0.1200, 1.80),
    (0.0250, 6.00),
    (0.0045, 25.0),
    (0.0005, 230.0),
]
RTP = sum(p * m for p, m in TABLE)

PLAYERS = 20_000
CASES = 500
PRICE = 1.0


def spin() -> float:
    r = random.random()
    acc = 0.0
    for p, m in TABLE:
        acc += p
        if r < acc:
            return m * PRICE
    return TABLE[-1][1] * PRICE


def main() -> None:
    profits = []
    best_drop = 0.0
    longest_dry = 0
    jackpots = 0

    for _ in range(PLAYERS):
        bank = 0.0
        dry = 0
        for _ in range(CASES):
            win = spin()
            bank += win
            best_drop = max(best_drop, win)
            if win >= 100 * PRICE:
                jackpots += 1
            if win < PRICE:
                dry += 1
                longest_dry = max(longest_dry, dry)
            else:
                dry = 0
        profits.append(bank - CASES * PRICE)

    profits.sort()
    total_staked = PLAYERS * CASES * PRICE
    up = sum(1 for p in profits if p > 0)

    print(f"economy: RTP {RTP:.1%}, {CASES} cases/player, {PLAYERS:,} players")
    print(f"total staked ${total_staked:,.0f} -> total returned ${sum(profits) + total_staked:,.0f}")
    print(f"mean profit   ${st.mean(profits):>10,.0f}  ({st.mean(profits)/CASES:.1%} of stake)")
    print(f"median profit ${st.median(profits):>10,.0f}")
    print(f"players in profit      {up:,} of {PLAYERS:,}  = {up/PLAYERS:.2%}")
    print(f"players 2x+ stake      {sum(1 for p in profits if p > CASES):,}  "
          f"= {sum(1 for p in profits if p > CASES)/PLAYERS:.2%}")
    print(f"players 5x+ stake      {sum(1 for p in profits if p > 4*CASES):,}  "
          f"= {sum(1 for p in profits if p > 4*CASES)/PLAYERS:.2%}")
    print(f"top 1% profit floor    ${profits[int(PLAYERS*0.99)]:,.0f}")
    print(f"worst single player    ${profits[0]:,.0f}")
    print(f"jackpot drops (>=100x) {jackpots:,} over {PLAYERS*CASES:,} cases "
          f"= 1 in {PLAYERS*CASES/max(jackpots,1):,.0f}")
    print(f"longest losing streak  {longest_dry} cases in a row")
    print()
    print(f"to have a 50% chance of ONE >=100x drop you need "
          f"{-1/__import__('math').log(1-0.0005) * 0.6931:,.0f} cases")
    print(f"price of that: ${-1/__import__('math').log(1-0.0005) * 0.6931:,.0f} staked "
          f"for a 0.05% shot, and it pays 230x = ${230*PRICE:,.0f}")


if __name__ == "__main__":
    main()
