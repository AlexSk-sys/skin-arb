import json
import os
import winreg

import requests


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


K = key("WHITE_API_KEY")
URL = "https://api.white.market/graphql"
UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Content-Type": "application/json"}

AUTH_VARIANTS = {
    "bearer": {"Authorization": f"Bearer {K}"},
    "x-api-key": {"X-API-KEY": K},
    "none": {},
}

query = {"query": "{ __typename }"}

for label, headers in AUTH_VARIANTS.items():
    try:
        r = requests.post(URL, json=query, headers={**UA, **headers}, timeout=30)
        print(f"{label:<10} {r.status_code} {r.text[:200]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<10} ERR {type(e).__name__}")

print("\n--- introspection ---")
intro = {"query": "{ __schema { queryType { name } } }"}
for label, headers in AUTH_VARIANTS.items():
    if label == "none":
        continue
    try:
        r = requests.post(URL, json=intro, headers={**UA, **headers}, timeout=30)
        print(f"{label:<10} {r.status_code} {r.text[:400]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<10} ERR {type(e).__name__}")
