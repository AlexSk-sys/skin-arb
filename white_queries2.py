import re
from collections import deque

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE = "https://white.market"
html = requests.get(BASE + "/", headers=UA, timeout=30).text
js = set(re.findall(r'(?:src|href)="([^"]+\.js[^"]*)"', html))
queue = deque(s if s.startswith("http") else BASE + ("" if s.startswith("/") else "/") + s for s in js)
seen = set()
names = set()

while queue and len(seen) < 80:
    url = queue.popleft()
    if url in seen:
        continue
    seen.add(url)
    try:
        body = requests.get(url, headers=UA, timeout=30).text
    except Exception:  # noqa: BLE001
        continue
    for m in re.findall(r"(?:query|mutation)\s+([A-Za-z0-9_]+)\s*\(", body):
        names.add(m)
    for m in re.findall(r'gql`\s*(?:query|mutation)\s+([A-Za-z0-9_]+)', body):
        names.add(m)
    for m in re.findall(r'["\'](/_next/static/chunks/[A-Za-z0-9/_.-]+\.js)["\']', body):
        queue.append(BASE + m)

print(f"scanned {len(seen)} chunks, operations: {len(names)}")
for n in sorted(names):
    print("  ", n)
