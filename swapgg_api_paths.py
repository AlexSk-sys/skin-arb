import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
BASE = "https://swap.gg"
PATHS = [
    "/api/items",
    "/api/items/list",
    "/api/items/search",
    "/api/market/items",
    "/api/market/list",
    "/api/store/items",
    "/api/trade/items",
    "/api/inventory",
    "/api/inventory/items",
    "/api/games/dota2/items",
    "/api/dota2/items",
    "/api/v1/items",
    "/api/v2/items",
    "/api/catalog",
    "/api/catalog/items",
    "/api/skins",
    "/api/list",
    "/api/search",
    "/api/market",
    "/api/store",
]
for path in PATHS:
    for params in ({"game": "dota2", "limit": 3}, {"game": "dota", "limit": 3}):
        try:
            r = requests.get(BASE + path, params=params, headers=UA, timeout=20)
            txt = r.text[:110].replace("\n", " ")
            if "Cannot GET" in txt:
                break
            print(f"{r.status_code} {path:<28} {txt}")
        except Exception as e:  # noqa: BLE001
            print(f"ERR {path} {type(e).__name__}")
            break
