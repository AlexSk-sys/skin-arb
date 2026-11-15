import re

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
html = requests.get(
    "https://lis-skins.stoplight.io/docs/lis-skins/dzq78x3edc19r-api-overview",
    headers=UA,
    timeout=30,
).text

for kw in ("market/buy", "item_id", "Authorization", "Bearer", "api_key", "apiKey", "project_id", "lis-skins"):
    idx = 0
    shown = 0
    while shown < 2:
        i = html.find(kw, idx)
        if i < 0:
            break
        print(f"[{kw}] ...{html[max(0, i-150):i+250]}...")
        print("-" * 60)
        idx = i + len(kw)
        shown += 1
