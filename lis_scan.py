"""Stream the LIS-SKINS public export and keep the cheapest price per item.

The export is ~1.3 GB gzipped, so it is parsed incrementally and reduced to a
small name -> (min_price, count) map written next to this script.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import ijson
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "lis_prices.json"
URL = "https://lis-skins.com/market_export_json/api_csgo_full.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

agg: dict[str, list] = {}
started = time.time()
count = 0

with requests.get(URL, stream=True, timeout=600, headers=UA) as r:
    r.raise_for_status()
    r.raw.decode_content = True
    for item in ijson.items(r.raw, "items.item"):
        name = item.get("name")
        price = item.get("price")
        if not name or price is None:
            continue
        count += 1
        row = agg.get(name)
        # Only listings that are tradable right now. Locked items cannot be
        # moved to another marketplace until unlock_at passes.
        if item.get("unlock_at"):
            continue
        if row is None:
            agg[name] = [float(price), 1, item.get("id")]
        else:
            row[1] += 1
            if float(price) < row[0]:
                row[0] = float(price)
                row[2] = item.get("id")
        if count % 200_000 == 0:
            print(f"  {count:,} лотов, {len(agg):,} предметов, {time.time()-started:.0f}s", flush=True)

OUT.write_text(json.dumps({"updated": time.time(), "items": agg}), encoding="utf-8")
print(f"готово: {count:,} лотов, {len(agg):,} уникальных предметов за {time.time()-started:.0f}s")
print(f"файл: {OUT} ({OUT.stat().st_size/1024/1024:.1f} MB)")
