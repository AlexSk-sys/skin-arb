import json

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0"}
STEAM_ID = "76561198848755367"

for app_id, label in ((570, "Dota 2"), (730, "CS2"), (440, "TF2"), (252490, "Rust")):
    url = f"https://steamcommunity.com/inventory/{STEAM_ID}/{app_id}/2"
    try:
        r = requests.get(
            url,
            params={"l": "english", "count": 1},
            headers=UA,
            timeout=30,
        )
        try:
            d = r.json()
        except Exception:  # noqa: BLE001
            print(f"{label:<7} {r.status_code} not json: {r.text[:120]}")
            continue
        if d.get("success"):
            total = d.get("total_inventory_count")
            print(f"{label:<7} {r.status_code} OK, предметов: {total}")
        else:
            print(f"{label:<7} {r.status_code} FAIL: {json.dumps(d, ensure_ascii=False)[:160]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<7} ERR {type(e).__name__}")

print("\n=== profile xml ===")
try:
    r = requests.get(
        f"https://steamcommunity.com/profiles/{STEAM_ID}/?xml=1", headers=UA, timeout=30
    )
    print(r.status_code, r.text[:300].replace("\n", " "))
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)
