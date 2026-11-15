import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE = "https://market.csgo.com"

html = requests.get(f"{BASE}/en/", headers=UA, timeout=25).text
js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
print("js files:", len(js), sorted(js)[:10])

hits = set()
for path in sorted(js)[:12]:
    url = path if path.startswith("http") else BASE + ("" if path.startswith("/") else "/") + path
    try:
        body = requests.get(url, headers=UA, timeout=30).text
    except Exception:  # noqa: BLE001
        continue
    for m in re.findall(r'"(/en/profile[^"]{0,40})"', body):
        hits.add(m)
    for m in re.findall(r'"(/[a-z-]*api[a-z-]*[^"]{0,30})"', body, re.I):
        hits.add(m)

print("\nroutes:")
for h in sorted(hits)[:40]:
    print("  ", h)
