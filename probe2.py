import json

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
}


def probe(name, url, params=None, headers=None, peek=700):
    h = dict(UA)
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, params=params, headers=h, timeout=60)
        print(f"=== {name} status={r.status_code} bytes={len(r.content)}")
        if r.status_code != 200:
            print(r.text[:200])
            return None
        try:
            d = r.json()
        except Exception:
            print("not json:", r.text[:200])
            return None
        if isinstance(d, list):
            print("list len", len(d))
            if d:
                print(json.dumps(d[0], indent=2, ensure_ascii=False)[:peek])
        elif isinstance(d, dict):
            print("keys", list(d.keys())[:15])
            for k in list(d.keys())[:2]:
                print(f"-- sample[{k}]:", json.dumps(d[k], indent=2, ensure_ascii=False)[:peek])
        return d
    except Exception as e:  # noqa: BLE001
        print(f"=== {name} ERROR {type(e).__name__}: {e}")
        return None


probe(
    "dmarket_v2",
    "https://api.dmarket.com/marketplace-api/v2/offers",
    {"gameId": "a8db", "currency": "USD", "limit": 5, "orderBy": "price", "orderDir": "asc"},
)
probe("waxpeer", "https://api.waxpeer.com/v1/prices", {"game": "csgo"})
probe("lootfarm", "https://loot.farm/api/prices/730")
probe("csgotrader_v6", "https://prices.csgotrader.app/latest/prices_v6.json", peek=900)
probe("skinport_browser", "https://api.skinport.com/v1/items", {"app_id": 730, "currency": "USD"})
