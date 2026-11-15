import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


MC = key("MARKET_CSGO_API_KEY")

for path, params in (
    ("/api/v2/search-item-by-hash-name", {"hash_name": "AK-47 | Redline (Field-Tested)", "currency": "USD"}),
    ("/api/v2/search-items-by-hash-name", {"hash_names": "AK-47 | Redline (Field-Tested)", "currency": "USD"}),
):
    try:
        r = requests.get(
            "https://market.csgo.com" + path,
            params={**params, "key": MC},
            headers=UA,
            timeout=30,
        )
        print(f"=== {path} {r.status_code} {len(r.content)}")
        print(r.text[:600])
    except Exception as e:  # noqa: BLE001
        print(f"=== {path} ERR {type(e).__name__}")
