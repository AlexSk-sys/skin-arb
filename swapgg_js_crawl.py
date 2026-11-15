import re
from collections import deque

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE = "https://swap.gg"

html = requests.get(BASE + "/dota2/trade", headers=UA, timeout=30).text
start = set(re.findall(r'src="([^"]+\.js[^"]*)"', html))
start |= set(re.findall(r'href="([^"]+\.js[^"]*)"', html))
start = {s if s.startswith("http") else BASE + ("" if s.startswith("/") else "/") + s for s in start}
start |= {BASE + "/_nuxt/DQv47C5l.js"}

seen = set()
queue = deque(start)
paths = set()
count = 0

while queue and count < 80:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    try:
        body = requests.get(url, headers=UA, timeout=30).text
    except Exception:  # noqa: BLE001
        continue
    count += 1
    for m in re.findall(r'["\'`](/?api/[A-Za-z0-9/_${}.-]{2,70})["\'`]', body):
        paths.add(m)
    for m in re.findall(r'["\'`](wss?://[^"\'`]+)["\'`]', body):
        paths.add(m)
    for m in re.findall(r'from"\./([A-Za-z0-9_-]+\.js)"', body):
        queue.append(BASE + "/_nuxt/" + m)
    for m in re.findall(r'import\("\./([A-Za-z0-9_-]+\.js)"\)', body):
        queue.append(BASE + "/_nuxt/" + m)

print(f"scanned {count} js files")
print("found paths:")
for p in sorted(paths)[:80]:
    print("  ", p[:110])
