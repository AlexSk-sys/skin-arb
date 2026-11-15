import json

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}
URL = "https://api.buff.market/api/market/goods"

r = requests.get(
    URL,
    params={"game": "csgo", "page_num": 1, "page_size": 3, "search": "Piggles"},
    headers=UA,
    timeout=40,
)
print("status", r.status_code)
data = r.json()
print("code", data.get("code"))
items = (data.get("data") or {}).get("items") or []
print("items", len(items))
for it in items[:2]:
    print(json.dumps(it, ensure_ascii=False)[:700])
