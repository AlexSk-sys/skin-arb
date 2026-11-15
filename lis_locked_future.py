from datetime import datetime, timezone

import ijson
import requests

URL = "https://lis-skins.com/market_export_json/api_csgo_full.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
now = datetime.now(timezone.utc)

locked = []
with requests.get(URL, stream=True, timeout=600, headers=UA) as r:
    r.raw.decode_content = True
    for item in ijson.items(r.raw, "items.item"):
        raw = item.get("unlock_at")
        if not raw:
            continue
        try:
            when = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if when <= now:
            continue
        locked.append(
            {
                "name": item.get("name"),
                "price": item.get("price"),
                "unlock_at": raw,
                "delivery_type": item.get("delivery_type"),
                "is_internal": item.get("is_internal"),
            }
        )

print(f"лотов с будущей блокировкой: {len(locked)}")
for row in sorted(locked, key=lambda x: x["unlock_at"])[:40]:
    print(
        f"  {row['name'][:42]:<42} ${row['price']:>7.2f} "
        f"до {row['unlock_at'][:10]} type={row['delivery_type']} internal={row['is_internal']}"
    )

targets = [r for r in locked if "ropz" in r["name"].lower() or "houndstooth" in r["name"].lower()]
print("\nтвои предметы среди них:", targets or "нет")
