import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

for url in (
    "https://lis-skins.com/ru/faq/",
    "https://lis-skins.com/ru/faq",
    "https://lis-skins.com/ru/support/",
):
    try:
        r = requests.get(url, headers=UA, timeout=25, allow_redirects=True)
        text = re.sub(r"<script.*?</script>", " ", r.text, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        print(f"=== {url} -> {r.status_code} {r.url[:60]} ({len(text)} chars)")
        for kw in ("Недоступно", "недоступ", "минимальн", "холд", "trade hold", "обмен"):
            i = text.lower().find(kw.lower())
            if i >= 0:
                print(f"  [{kw}] ...{text[max(0, i-150):i+300]}...")
    except Exception as e:  # noqa: BLE001
        print(f"=== {url} ERR {type(e).__name__}")
