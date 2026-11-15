# skin-arb

Cross-marketplace **CS2 skin arbitrage scanner**. It compares the lowest asks on Waxpeer and
Market.CSGO, uses Steam only as a rate-limited reference, and computes what you actually keep
after seller commission and a 2% undercut. Additional scripts compare LIS-SKINS, Shadowpay,
CSFloat and Dota venues.

## What it does

- **Fee-aware executable spreads**: buy on one marketplace, sell on another, subtract the seller
  commission and a 2% undercut to sit at the top of the destination book.
- **Demand-first filters**: minimum listings on both sides, a liquidity floor on the buy side,
  and a margin floor/ceiling that flags stale listings or name mismatches instead of reporting
  fake arbitrage.
- **Politeness**: 5-minute cache and a Steam 429 workaround; Steam is never treated as an
  executable venue.
- **Paper mode**: `trader_config.json` and `loop_config.json` default to paper execution with
  small caps; this snapshot contains no live orders and no credentials.

## Run

```powershell
python -m pip install requests
python arb.py
```

The scanner writes cached venue snapshots under `cache/` (gitignored).

## Layout

- `arb.py` — the core scanner (Waxpeer + Market.CSGO + Steam reference)
- `add_lis_compare.py`, `waxpeer_status.py`, `steam_profile_status.py` — venue checks
- `analysis*.py`, `check_*.py` — exploratory checks kept for the record
- `trader_config.json`, `loop_config.json` — paper-mode settings

## Note

This is a personal research snapshot, paused in November 2026. It is not financial advice and it
does not place orders.
