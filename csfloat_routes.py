import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

html = requests.get("https://csfloat.com/", headers=UA, timeout=30).text
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print("scripts:", len(scripts))

base = "https://csfloat.com"
paths = set()
for src in scripts:
    url = src if src.startswith("http") else base + ("" if src.startswith("/") else "/") + src
    try:
        r = requests.get(url, headers=UA, timeout=40)
        body = r.text
        print(f"  {url[:90]} -> {r.status_code} {len(body)} bytes")
        for m in re.findall(r'["\'](/[a-z0-9][a-z0-9/_-]{2,40})["\']', body, re.I):
            low = m.lower()
            if any(k in low for k in ("api", "doc", "develop", "key", "setting", "profile")):
                paths.add(m)
    except Exception as e:  # noqa: BLE001
        print("  ERR", url[:80], type(e).__name__)

print("\ncandidate routes:")
for p in sorted(paths)[:80]:
    print("  ", p)
