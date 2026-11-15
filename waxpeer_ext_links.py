import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for path in ("/faq/how-to-sell", "/faq/instant-sell"):
    url = "https://faq.waxpeer.com" + path
    r = requests.get(url, headers=UA, timeout=25)
    print(f"=== {url}")
    links = set(re.findall(r'href="([^"]+)"', r.text))
    for link in sorted(links):
        low = link.lower()
        if any(k in low for k in ("chrome", "extension", "app", "download", "waxpeer.com", "store")):
            print("  ", link[:140])
