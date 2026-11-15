from collections import Counter

import ijson
import requests

URL = "https://lis-skins.com/market_export_json/api_csgo_full.json"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

stats = Counter()
examples = {}

with requests.get(URL, stream=True, timeout=600, headers=UA) as r:
    r.raw.decode_content = True
    for i, item in enumerate(ijson.items(r.raw, "items.item")):
        pass
        key = (
            "locked" if item.get("unlock_at") else "free",
            item.get("delivery_type"),
            item.get("is_internal"),
        )
        stats[key] += 1
        if key not in examples:
            examples[key] = {
                "name": item.get("name"),
                "price": item.get("price"),
                "unlock_at": item.get("unlock_at"),
            }

print(f"{'lock':<7} {'delivery':>8} {'internal':>9} {'count':>8}  example")
for key, count in stats.most_common(12):
    ex = examples[key]
    print(
        f"{key[0]:<7} {str(key[1]):>8} {str(key[2]):>9} {count:>8}  "
        f"{ex['name'][:34]} ${ex['price']} unlock={ex['unlock_at']}"
    )
