import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
}

for url in ("https://docs.skinport.com/", "https://docs.skinport.com"):
    try:
        r = requests.get(url, headers=UA, timeout=25)
        print(url, r.status_code, "bytes", len(r.content))
        if r.status_code == 200:
            links = set(re.findall(r'href="([^"]+)"', r.text))
            for link in sorted(links):
                if any(k in link.lower() for k in ("account", "sale", "sell", "item", "list", "api")):
                    print("  ", link[:120])
            break
    except Exception as e:  # noqa: BLE001
        print(url, "ERR", type(e).__name__)
