import re

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def links_of(url: str, keys: tuple[str, ...]) -> None:
    print(f"=== {url}")
    try:
        r = requests.get(url, headers=UA, timeout=25)
        print("status", r.status_code, "bytes", len(r.content))
        found = set(re.findall(r'href="([^"]+)"', r.text))
        found |= set(re.findall(r'"(https?://[^"]+)"', r.text))
        for link in sorted(found):
            if any(k in link.lower() for k in keys):
                print("  ", link[:120])
    except Exception as e:  # noqa: BLE001
        print("ERR", type(e).__name__, str(e)[:80])


links_of("https://docs.waxpeer.com/", ("api", "auth", "profile", "key", "trade"))
links_of("https://market.csgo.com/en/profile", ("api", "doc", "trade", "setting"))
links_of("https://market.csgo.com/en/", ("api", "doc", "trade", "profile"))
