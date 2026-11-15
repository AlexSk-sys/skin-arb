import json
import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

html = requests.get("https://doc.shadowpay.com", headers=UA, timeout=30).text
print("bytes", len(html))

for marker in ("URQL_DATA", "__NEXT_DATA__", "__NUXT_DATA__", "projectId", "openapi"):
    i = html.find(marker)
    print(f"[{marker}] idx={i}")
    if i >= 0:
        print("  ", html[max(0, i - 100): i + 300].replace("\n", " ")[:400])

m = re.search(r"window\.URQL_DATA\s*=\s*", html)
if m:
    try:
        data, _ = json.JSONDecoder().raw_decode(html[m.end():])
        print("URQL keys:", list(data.keys())[:5])
        for key, value in data.items():
            if isinstance(value, dict) and isinstance(value.get("data"), str):
                txt = value["data"]
                if "defaultBranchNodes" in txt or "projects" in txt:
                    print(f"[{key}] data preview:", txt[:300])
    except Exception as e:  # noqa: BLE001
        print("URQL parse error", e)
