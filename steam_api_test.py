import os
import winreg

import requests

STEAM_KEY = "958367AA98CC16CA68EF6A2A5FE4155A"
STEAM_ID = "76561198848755367"

env = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(env, "STEAM_API_KEY", 0, winreg.REG_SZ, STEAM_KEY)
winreg.CloseKey(env)
print("steam key stored, len", len(STEAM_KEY))


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}

print("\n=== Steam GetPlayerSummaries ===")
try:
    r = requests.get(
        "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
        params={"key": STEAM_KEY, "steamids": STEAM_ID},
        timeout=30,
    )
    print(r.status_code, r.text[:300])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)

print("\n=== Steam GetTradeOffers ===")
try:
    r = requests.get(
        "https://api.steampowered.com/IEconService/GetTradeOffers/v1/",
        params={
            "key": STEAM_KEY,
            "get_sent_offers": 1,
            "get_received_offers": 1,
            "active_only": 1,
        },
        timeout=30,
    )
    print(r.status_code, r.text[:400])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)

print("\n=== Waxpeer set-my-steamapi ===")
try:
    r = requests.get(
        "https://api.waxpeer.com/v1/set-my-steamapi",
        params={"api": WX, "steamapi": STEAM_KEY},
        timeout=30,
    )
    print(r.status_code, r.text[:300])
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)

print("\n=== Waxpeer user steam_api field ===")
try:
    r = requests.get("https://api.waxpeer.com/v1/user", params={"api": WX}, timeout=30)
    u = r.json().get("user", {})
    print("wallet", u.get("wallet"), "| can_p2p", u.get("can_p2p"), "| steam_api", bool(u.get("steam_api")))
except Exception as e:  # noqa: BLE001
    print("ERR", type(e).__name__)
