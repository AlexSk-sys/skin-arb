import json

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}
BASE = "https://tradeit.gg"

for params in ({"query": "Autumn Thicket"}, {"search": "Autumn Thicket"}, {"q": "Autumn Thicket"}):
    r = requests.get(BASE + "/api/v2/meta/item-search", params=params, headers=UA, timeout=25)
    d = r.json()
    items = (d.get("data") or {}).get("items") or []
    print(f"params {list(params)[0]}: {r.status_code}, items {len(items)}")
    for it in items[:2]:
        print("  ", json.dumps(it, ensure_ascii=False)[:300])

print("\n=== item detail ===")
for url in (
    BASE + "/api/v2/meta/item?id=36394",
    BASE + "/api/v2/meta/item?itemId=36394",
    BASE + "/api/v2/meta/item?slug=blueberries-buckshot-nswc-seal",
):
    try:
        r = requests.get(url, headers=UA, timeout=25)
        print(r.status_code, url[-60:], r.text[:300].replace("\n", " "))
    except Exception as e:  # noqa: BLE001
        print("ERR", type(e).__name__)
