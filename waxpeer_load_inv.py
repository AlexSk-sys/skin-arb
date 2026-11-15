import os
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")

TESTS = [
    ("/v1/load-inventory", {"api": WX, "game": "dota2"}),
    ("/v1/update-inventory", {"api": WX, "game": "dota2"}),
    ("/v1/get-inventory", {"api": WX, "game": "dota2"}),
    ("/v1/fetch-my-inventory", {"api": WX, "game": "dota2", "full": 1}),
    ("/v1/fetch-my-inventory", {"api": WX, "game": "dota2", "details": 1}),
    ("/v1/get-my-inventory", {"api": WX, "game": "dota2", "full": 1}),
]

for path, params in TESTS:
    try:
        r = requests.get("https://api.waxpeer.com" + path, params=params, headers=UA, timeout=60)
        print(f"{path} {list(params)[-1]}: {r.status_code} {r.text[:300]}")
    except Exception as e:  # noqa: BLE001
        print(f"{path} ERR {type(e).__name__}")
