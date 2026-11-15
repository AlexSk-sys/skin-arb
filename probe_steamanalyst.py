import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

print("=== /v1/prices no params ===")
try:
    r = requests.get("https://api.steamanalyst.com/v1/prices", headers=UA, timeout=20)
    print(r.status_code, r.text[:600])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)

print("\n=== /v1/prices with guesses ===")
for params in (
    {"names": "AK-47 | Redline (Field-Tested)"},
    {"items": "AK-47 | Redline (Field-Tested)"},
    {"market_hash_name": "AK-47 | Redline (Field-Tested)"},
    {"q": "AK-47 | Redline (Field-Tested)"},
    {"limit": 1},
):
    try:
        r = requests.get(
            "https://api.steamanalyst.com/v1/prices", params=params, headers=UA, timeout=20
        )
        print(list(params)[0], "->", r.status_code, r.text[:200].replace("\n", " "))
    except Exception as e:  # noqa: BLE001
        print(list(params)[0], "ERR", type(e).__name__)

print("\n=== api-info page text ===")
try:
    r = requests.get("https://www.steamanalyst.com/api-info", headers=UA, timeout=25)
    print("status", r.status_code, "bytes", len(r.content))
    text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    i = text.lower().find("api")
    print(text[max(0, i - 200): i + 1800])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__, str(e)[:100])
