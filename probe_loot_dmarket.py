import json

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0", "Accept": "application/json"}

print("=== Loot.farm price endpoints ===")
for path in (
    "/api/prices/570",
    "/api/prices/730",
    "/api/prices/252490",
    "/api/prices/dota2",
    "/api/prices",
):
    try:
        r = requests.get("https://loot.farm" + path, headers=UA, timeout=30)
        print(f"{path:<24} {r.status_code} {r.headers.get('content-type','')[:20]:<20} {len(r.content):>8} {r.text[:90]}")
    except Exception as e:  # noqa: BLE001
        print(f"{path:<24} ERR {type(e).__name__}")

print("\n=== DMarket public endpoints ===")
for url in (
    "https://api.dmarket.com/price-aggregator/v1/aggregated-prices?gameId=a8db",
    "https://api.dmarket.com/marketplace-api/v2/offers?gameId=a8db&limit=1",
    "https://api.dmarket.com/exchange/v1/market/items?gameId=a8db&limit=1",
):
    try:
        r = requests.get(url, headers=UA, timeout=30)
        print(f"{r.status_code} {url[:78]:<78} {r.text[:90]}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {url[:78]} {type(e).__name__}")
