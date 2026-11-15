import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

urls = [
    "https://csfloat.com/profile",
    "https://csfloat.com/settings",
    "https://csfloat.com/account",
    "https://csfloat.com/settings/api",
    "https://csfloat.com/api-keys",
    "https://csfloat.com/developers",
    "https://csfloat.com/docs",
    "https://csfloat.com/api/v1/listings?limit=1",
    "https://csfloat.com/api/v1/me",
    "https://csfloat.com/api/v1/openapi.json",
    "https://csfloat.com/api/v1/docs",
]

for u in urls:
    try:
        r = requests.get(u, headers=UA, timeout=20, allow_redirects=False)
        body = r.text[:90].replace("\n", " ")
        print(f"{r.status_code} {r.headers.get('content-type','')[:28]:<28} {u[:70]} | {body}")
    except Exception as e:  # noqa: BLE001
        print("ERR", u[:70], type(e).__name__)

print("\n--- root html ---")
try:
    h = requests.get("https://csfloat.com/", headers=UA, timeout=30).text
    t = re.search(r"<title[^>]*>(.*?)</title>", h, re.S | re.I)
    print("title:", t.group(1).strip()[:100] if t else "none")
    print("len:", len(h))
    print("script tags:", len(re.findall(r"<script", h, re.I)))
    print("js urls:", re.findall(r'["\']([^"\']+\.js)["\']', h)[:10])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)
