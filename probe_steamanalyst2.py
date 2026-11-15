import json
import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

NAMES = [
    "AK-47 | Redline (Field-Tested)",
    "AWP | Asiimov (Field-Tested)",
    "★ Karambit | Fade (Minimal Factory New)"
    if False
    else "★ Karambit | Fade (Minimal Wear)",
]

for name in NAMES:
    try:
        r = requests.get(
            "https://api.steamanalyst.com/v1/prices",
            params={"market_name": name},
            headers=UA,
            timeout=30,
        )
        print("===", name, "status", r.status_code, "bytes", len(r.content))
        if r.status_code == 200:
            d = r.json()
            print(json.dumps(d, ensure_ascii=False, indent=2)[:1500])
        else:
            print(r.text[:300])
    except Exception as e:  # noqa: BLE001
        print("ERR", type(e).__name__, str(e)[:80])

print("\n=== api-info: keywords ===")
try:
    r = requests.get("https://www.steamanalyst.com/api-info", headers=UA, timeout=25)
    text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    for kw in ("market_name", "api_key", "curl", "endpoint", "free tier", "requests per"):
        i = text.lower().find(kw.lower())
        if i >= 0:
            print(f"[{kw}] ...{text[max(0, i-150): i+400]}...")
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)
