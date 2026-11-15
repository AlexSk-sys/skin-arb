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
URL = "https://api.white.market/graphql/api"
UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Content-Type": "application/json"}

VARIANTS = {
    "bearer": {"Authorization": f"Bearer {K}"},
    "authtoken": {"authToken": K},
    "x-api-key": {"X-API-KEY": K},
    "none": {},
}

for label, headers in VARIANTS.items():
    try:
        r = requests.post(
            URL, json={"query": "{ __typename }"}, headers={**UA, **headers}, timeout=30
        )
        print(f"{label:<10} {r.status_code} {r.text[:250]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<10} ERR {type(e).__name__}")

print("\n--- introspection with bearer/authtoken ---")
for label in ("bearer", "authtoken"):
    try:
        r = requests.post(
            URL,
            json={"query": "{ __schema { queryType { name } } }"},
            headers={**UA, **VARIANTS[label]},
            timeout=30,
        )
        print(f"{label:<10} {r.status_code} {r.text[:400]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<10} ERR {type(e).__name__}")
