import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

URLS = [
    "https://waxpeer.com/",
    "https://waxpeer.com/profile",
    "https://waxpeer.com/settings",
    "https://waxpeer.com/en/profile",
    "https://docs.waxpeer.com/",
    "https://market.csgo.com/",
    "https://market.csgo.com/en/profile",
    "https://market.csgo.com/profile",
    "https://market.csgo.com/docs-v2",
    "https://market.csgo.com/docs",
]

for url in URLS:
    try:
        r = requests.get(url, headers=UA, timeout=20, allow_redirects=True)
        m = re.search(r"<title[^>]*>(.*?)</title>", r.text, re.S | re.I)
        title = m.group(1).strip()[:60] if m else ""
        print(f"{r.status_code} -> {r.url[:70]:<70} | {title}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {url[:70]:<70} | {type(e).__name__}")
