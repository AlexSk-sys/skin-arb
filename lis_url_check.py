import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

ITEM_ID = "583793166"
PATTERNS = [
    f"https://lis-skins.com/csgo/item/{ITEM_ID}",
    f"https://lis-skins.com/market/csgo/{ITEM_ID}",
    f"https://lis-skins.com/item/{ITEM_ID}",
    f"https://lis-skins.com/csgo/{ITEM_ID}",
    f"https://lis-skins.com/market/item/{ITEM_ID}",
]

for url in PATTERNS:
    try:
        r = requests.get(url, headers=UA, timeout=20, allow_redirects=True)
        print(f"{r.status_code} {url[:60]:<60} -> {r.url[:60]}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {url[:60]} {type(e).__name__}")
