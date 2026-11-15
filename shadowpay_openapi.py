import re

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/yaml,text/yaml,*/*"}

for ver in ("v2", "v3"):
    url = f"https://api.shadowpay.com/doc/openapi_salt_{ver}.yaml"
    try:
        r = requests.get(url, headers=UA, timeout=40)
        print(f"=== {ver}: {r.status_code} bytes {len(r.content)}")
        if r.status_code != 200:
            print(r.text[:200])
            continue
        text = r.text
        paths = re.findall(r"^  (/[A-Za-z0-9/_{}.-]+):\s*$", text, re.M)
        print(f"paths: {len(paths)}")
        for p in paths[:80]:
            print("  ", p)
        # auth hint
        for kw in ("securitySchemes", "bearer", "apiKey", "Authorization", "X-API"):
            i = text.find(kw)
            if i >= 0:
                print(f"[{kw}] {text[i:i+200].replace(chr(10), ' ')}")
    except Exception as e:  # noqa: BLE001
        print(f"=== {ver} ERR {type(e).__name__}")
