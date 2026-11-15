import re

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

html = requests.get(
    "https://lis-skins.stoplight.io/docs/lis-skins/dzq78x3edc19r-api-overview",
    headers=UA,
    timeout=30,
).text
urls = set(re.findall(r'"(https://[^"]*stoplight[^"]*)"', html))
urls |= set(re.findall(r'"(/api/[^"]+)"', html))
print("urls found:")
for u in sorted(urls)[:20]:
    print("  ", u[:120])

CANDIDATES = [
    "https://lis-skins.stoplight.io/docs/lis-skins/openapi.json",
    "https://lis-skins.stoplight.io/docs/lis-skins/openapi.yaml",
    "https://lis-skins.stoplight.io/api/v1/projects/lis-skins",
    "https://lis-skins.stoplight.io/api/v1/projects/lis-skins/nodes",
    "https://lis-skins.stoplight.io/api/v1/workspaces/lis-skins/projects/lis-skins",
]
for u in CANDIDATES:
    try:
        r = requests.get(u, headers=UA, timeout=25, allow_redirects=True)
        print(f"{r.status_code} {u[:80]} | {r.headers.get('content-type','')[:24]} | {r.text[:120].replace(chr(10),' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"ERR {u[:80]} {type(e).__name__}")
