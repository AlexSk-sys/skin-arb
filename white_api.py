import winreg

import requests

KEY = "jdnrgdo4ehr3md3phl6ungfedsmmnyynjkmpv74wboqrfr45sqnusojecepfsilj"

env = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(env, "WHITE_API_KEY", 0, winreg.REG_SZ, KEY)
winreg.CloseKey(env)
print("key stored, len", len(KEY))

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}

ENDPOINTS = [
    "https://api.white.market/",
    "https://api.white.market/api/v1/items",
    "https://api.white.market/api/v1/prices",
    "https://api.white.market/api/v1/market/items",
    "https://white.market/api/v1/items",
    "https://white.market/api/prices",
]

AUTH = {
    "Bearer": {"Authorization": f"Bearer {KEY}"},
    "X-API-KEY": {"X-API-KEY": KEY},
    "X-Api-Key": {"X-Api-Key": KEY},
    "api-key": {"api-key": KEY},
}

for url in ENDPOINTS:
    for label, headers in AUTH.items():
        try:
            r = requests.get(
                url, params={"game": "rust"}, headers={**UA, **headers}, timeout=20
            )
            if r.status_code != 404:
                print(f"{label:<10} {url[:60]:<60} {r.status_code} {r.text[:120].replace(chr(10), ' ')}")
        except Exception as e:  # noqa: BLE001
            print(f"{label:<10} {url[:60]} ERR {type(e).__name__}")
