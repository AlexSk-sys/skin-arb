import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}

URLS = [
    "https://api.tradeit.gg/api/v2/meta/item-search?query=Autumn%20Thicket",
    "https://tradeit.gg/api/v2/meta/item-search?query=Autumn%20Thicket",
    "https://api.tradeit.gg/api/v2/meta/top-items",
    "https://tradeit.gg/api/v2/meta/top-items",
    "https://api.cs.deals/api/v1/items",
    "https://api.cs.deals/api/items",
]

for url in URLS:
    try:
        r = requests.get(url, headers=UA, timeout=25)
        print(f"{r.status_code} {url[:75]:<75} {r.text[:160].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {url[:75]} {type(e).__name__}")
