import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE = "https://loot.farm"

html = requests.get(BASE + "/", headers=UA, timeout=30).text
js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
print("js files:", len(js))

paths = set()
for path in sorted(js)[:15]:
    url = path if path.startswith("http") else BASE + ("" if path.startswith("/") else "/") + path
    try:
        body = requests.get(url, headers=UA, timeout=40).text
    except Exception:  # noqa: BLE001
        continue
    for m in re.findall(r'["\'](/api/[a-zA-Z0-9/_.-]{2,60})["\']', body):
        paths.add(m)
    for m in re.findall(r'["\'](https://[a-z0-9.-]*loot\.farm/[a-zA-Z0-9/_.-]{2,60})["\']', body):
        paths.add(m)

print("api paths:")
for p in sorted(paths)[:40]:
    print("  ", p)
