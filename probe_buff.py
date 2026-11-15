import requests

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0",
    "Accept": "application/json",
}

CANDIDATES = [
    "https://api.buff.market/",
    "https://api.buff.market/api/market/goods?game=csgo&page_num=1&page_size=5",
    "https://api.buff.market/api/market/goods?game=dota2&page_num=1&page_size=5",
    "https://api.buff.market/api/market/goods?game=rust&page_num=1&page_size=5",
    "https://api.tradeit.gg/api/v1/items?appId=730&limit=3",
    "https://api.tradeit.gg/api/items?appId=730&limit=3",
    "https://api.skinsmonkey.com/api/v1/items?limit=3",
]

for url in CANDIDATES:
    try:
        r = requests.get(url, headers=UA, timeout=30)
        print(f"{r.status_code} {url[:78]:<78} {r.text[:140].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {url[:78]} {type(e).__name__}")
