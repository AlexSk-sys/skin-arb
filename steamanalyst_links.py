import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

r = requests.get("https://www.steamanalyst.com/api-info", headers=UA, timeout=25)
links = set(re.findall(r'href="([^"]+)"', r.text))
for link in sorted(links):
    low = link.lower()
    if any(k in low for k in ("developer", "dashboard", "api", "signin", "login", "pricing", "upgrade")):
        print(link)
