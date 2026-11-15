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

for path in ("/v1/get-items-list", "/v1/get-steam-items", "/v1/get-my-inventory"):
    for params in (
        {"api": WX, "game": "dota2"},
        {"api": WX, "game": "dota2", "include_hold": 1},
    ):
        try:
            r = requests.get(
                "https://api.waxpeer.com" + path, params=params, headers=UA, timeout=40
            )
            print(f"{path} {params.get('include_hold', '')}: {r.status_code} {r.text[:400]}")
            if r.status_code == 200:
                break
        except Exception as e:  # noqa: BLE001
            print(f"{path} ERR {type(e).__name__}")
