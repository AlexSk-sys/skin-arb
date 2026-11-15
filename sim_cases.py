#!/usr/bin/env python3
"""Why "most drops beat the case price" and "the case is -12%" are both true."""
import random
import statistics as st

random.seed(7)
COST = 39.0
# (probability, payout in rubles) — 70% of drops exceed the 39 ₽ case price
TABLE = [
    (0.620, 41.0),
    (0.300, 9.0),
    (0.070, 70.0),
    (0.009, 100.0),
    (0.001, 400.0),
]
MEAN = sum(p * v for p, v in TABLE)
ABOVE = sum(p for p, v in TABLE if v > COST)


def spin() -> float:
    r = random.random()
    acc = 0.0
    for p, v in TABLE:
        acc += p
        if r < acc:
            return v
    return TABLE[-1][1]


def main() -> None:
    print(f"case costs {COST:.0f} rub | mean drop {MEAN:.2f} rub | RTP {MEAN / COST:.1%}")
    print(f"drops worth MORE than the case: {ABOVE:.0%} of openings")
    print()
    header = f"{'cases':>6} {'P(profit)':>10} {'median':>9} {'mean':>9}"
    print(header)
    print("-" * len(header))

    for n in (1, 10, 50, 100, 500, 1000, 5000, 20000):
        trials, up, nets = 20000, 0, []
        for _ in range(trials):
            got = sum(spin() for _ in range(n)) - COST * n
            nets.append(got)
            if got > 0:
                up += 1
        print(f"{n:>6} {up / trials:>9.2%} {st.median(nets):>9.0f} {st.mean(nets):>9.0f}")


if __name__ == "__main__":
    main()
