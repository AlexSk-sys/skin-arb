import re
from urllib.parse import unquote

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for path in ("robots.txt", "sitemap.xml", "sitemap_index.xml"):
    try:
        r = requests.get(f"https://csfloat.com/{path}", headers=UA, timeout=20)
        print(f"=== {path} {r.status_code} {len(r.text)}")
        print(r.text[:400].replace("\n", " | "))
    except Exception as e:  # noqa: BLE001
        print(f"=== {path} ERR {type(e).__name__}")

print("\n=== DuckDuckGo ===")
for q in ("csfloat api documentation", "csfloat api key generate"):
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/", data={"q": q}, headers=UA, timeout=30
        )
        links = re.findall(r'uddg=([^"&]+)', r.text)
        seen = []
        for link in links:
            u = unquote(link)
            if "csfloat" in u and u not in seen:
                seen.append(u)
        print(f"[{q}] status={r.status_code} results={len(seen)}")
        for u in seen[:10]:
            print("   ", u)
    except Exception as e:  # noqa: BLE001
        print(f"[{q}] ERR {type(e).__name__}: {str(e)[:80]}")
