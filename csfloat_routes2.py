import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}
BASE = "https://csfloat.com/"

html = requests.get(BASE, headers=UA, timeout=30).text
js = set(re.findall(r'["\']([^"\']+\.js)["\']', html))
print("js files:", len(js))

patterns = re.compile(r"(api[-_ ]?key|apikey|apiKeys|developers?/|/settings)", re.I)
hits = {}
for path in sorted(js):
    url = path if path.startswith("http") else BASE + path.lstrip("/")
    try:
        r = requests.get(url, headers=UA, timeout=40)
        body = r.text
    except Exception as e:  # noqa: BLE001
        print("ERR", path[:40], type(e).__name__)
        continue
    for m in patterns.finditer(body):
        s = max(0, m.start() - 60)
        snippet = body[s : m.end() + 60].replace("\n", " ")
        hits.setdefault(m.group(1).lower(), set()).add(snippet[:140])

for key, vals in hits.items():
    print(f"\n## {key}")
    for v in list(vals)[:6]:
        print("  ", v)
