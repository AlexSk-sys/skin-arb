import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

html = requests.get("https://doc.shadowpay.com", headers=UA, timeout=30).text

for kw in ("slug", "projectId", "project_id", "branch", "nodes", "swagger", "openapi", "v2"):
    idxs = [m.start() for m in re.finditer(kw, html)][:3]
    for i in idxs:
        print(f"[{kw}] ...{html[max(0, i-150):i+250].replace(chr(10), ' ')}...")
    print("-" * 50)
