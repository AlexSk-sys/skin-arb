import json

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb-probe/0.1"}


def probe(name, url, params=None, headers=None):
    h = dict(UA)
    if headers:
        h.update(headers)
    try:
        r = requests.get(url, params=params, headers=h, timeout=40)
        print(f"=== {name} status={r.status_code} bytes={len(r.content)}")
        if r.status_code != 200:
            print(r.text[:400])
            return
        try:
            d = r.json()
        except Exception:
            print("not json:", r.text[:300])
            return
        if isinstance(d, list):
            print("list len", len(d))
            if d:
                print(json.dumps(d[0], indent=2, ensure_ascii=False)[:900])
        elif isinstance(d, dict):
            print("keys", list(d.keys())[:25])
            print(json.dumps(d, indent=2, ensure_ascii=False)[:900])
    except Exception as e:  # noqa: BLE001
        print(f"=== {name} ERROR {type(e).__name__}: {e}")


probe("skinport", "https://api.skinport.com/v1/items", {"app_id": 730, "currency": "USD"})
probe(
    "dmarket",
    "https://api.dmarket.com/exchange/v1/market/items",
    {
        "side": "market",
        "orderBy": "price",
        "orderDir": "asc",
        "gameId": "a8db",
        "currency": "USD",
        "limit": 5,
        "offset": 0,
    },
)
probe("csfloat", "https://csfloat.com/api/v1/listings", {"limit": 5, "sort_by": "lowest_price"})
probe(
    "steam",
    "https://steamcommunity.com/market/priceoverview/",
    {"appid": 730, "currency": 1, "market_hash_name": "AK-47 | Redline (Field-Tested)"},
)
