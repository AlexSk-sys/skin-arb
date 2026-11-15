import requests

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0",
    "Accept": "application/json",
}
BASE = "https://api.shadowpay.com"

PATHS = [
    "/api/market",
    "/api/market/site_api",
    "/api/market/site_api/analytics",
    "/api/market/profile",
    "/api/market/partner",
    "/api/market/merchant",
    "/api/market/notification",
]

for path in PATHS:
    for params in ({}, {"game": "dota2"}, {"game": "dota2", "limit": 3}):
        try:
            r = requests.get(BASE + path, params=params, headers=UA, timeout=25)
            txt = r.text[:140].replace("\n", " ")
            print(f"{r.status_code} {path:<34} {params} {txt}")
            if r.status_code != 404:
                break
        except Exception as e:  # noqa: BLE001
            print(f"ERR {path} {type(e).__name__}")
            break
