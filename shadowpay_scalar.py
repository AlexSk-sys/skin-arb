import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/json",
}

r = requests.get("https://api.shadowpay.com/api/doc", headers=UA, timeout=30)
print("status", r.status_code, "bytes", len(r.content))

html = r.text
for marker in ("openapi", "url:", "spec", "/api/v2", "user/items"):
    i = html.find(marker)
    print(f"[{marker}] idx={i}")
    if i >= 0:
        print("  ", html[max(0, i - 120): i + 240].replace("\n", " ")[:360])

# Endpoint-like strings in the HTML.
eps = set(re.findall(r'(?:GET|POST|PUT|PATCH|DELETE)\s+(/[a-zA-Z0-9/_{}.-]+)', html))
print("\nendpoints found:", len(eps))
for e in sorted(eps)[:60]:
    print("  ", e)
