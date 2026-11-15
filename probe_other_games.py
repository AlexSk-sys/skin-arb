import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

print("=== Waxpeer by game ===")
for game in ("csgo", "dota2", "tf2", "rust"):
    try:
        r = requests.get(
            "https://api.waxpeer.com/v1/prices", params={"game": game}, headers=UA, timeout=60
        )
        data = r.json()
        items = data.get("items", [])
        print(f"{game:<6} {r.status_code} items={len(items)}")
        for it in items[:3]:
            print(f"   {it.get('name')} | min {it.get('min')} | count {it.get('count')}")
    except Exception as e:  # noqa: BLE001
        print(f"{game:<6} ERR {type(e).__name__}")

print("\n=== Skinport app_ids ===")
for app_id, label in ((570, "Dota 2"), (440, "TF2"), (252490, "Rust"), (730, "CS2")):
    try:
        r = requests.get(
            "https://api.skinport.com/v1/items",
            params={"app_id": app_id, "currency": "USD"},
            headers=UA,
            timeout=45,
        )
        print(f"{label:<7} {r.status_code} bytes={len(r.content)} {r.text[:80]}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<7} ERR {type(e).__name__}")
