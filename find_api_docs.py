import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

CANDIDATES = [
    ("ShadowPay docs", "https://docs.shadowpay.com/"),
    ("ShadowPay api", "https://shadowpay.com/api"),
    ("SkinsMonkey api", "https://skinsmonkey.com/api"),
    ("SkinsMonkey docs", "https://docs.skinsmonkey.com/"),
    ("Tradeit api", "https://tradeit.gg/api"),
    ("Tradeit docs", "https://docs.tradeit.gg/"),
    ("White api", "https://white.market/api"),
    ("White docs", "https://docs.white.market/"),
    ("Loot api", "https://loot.farm/api"),
    ("Swap api", "https://swap.gg/api"),
]

for name, url in CANDIDATES:
    try:
        r = requests.get(url, headers=UA, timeout=20, allow_redirects=True)
        print(f"{name:<18} {r.status_code} -> {r.url[:70]:<70} {r.text[:80].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"{name:<18} ERR {type(e).__name__}")
