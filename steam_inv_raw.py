import requests

STEAM_ID = "76561198848755367"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}

for app_id, label in ((570, "Dota 2"), (730, "CS2"), (440, "TF2"), (252490, "Rust")):
    try:
        r = requests.get(
            f"https://steamcommunity.com/inventory/{STEAM_ID}/{app_id}/2",
            params={"l": "english", "count": 1},
            headers=UA,
            timeout=30,
        )
        print(f"{label:<7} status={r.status_code} bytes={len(r.content)}")
        print("   ", r.text[:220].replace("\n", " "))
    except Exception as e:  # noqa: BLE001
        print(f"{label:<7} ERR {type(e).__name__}: {str(e)[:100]}")
