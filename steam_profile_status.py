import re

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0"}
STEAM_ID = "76561198848755367"

r = requests.get(
    f"https://steamcommunity.com/profiles/{STEAM_ID}/?xml=1", headers=UA, timeout=30
)
print("status", r.status_code)
xml = r.text

for tag in (
    "isLimitedAccount",
    "vacBanned",
    "tradeBanState",
    "privacyState",
    "visibilityState",
    "steamID",
    "onlineState",
    "memberSince",
):
    m = re.search(rf"<{tag}>(.*?)</{tag}>", xml, re.S)
    print(f"{tag:<18}: {m.group(1).strip() if m else '—'}")

print("\nraw head:")
print(xml[:600].replace("\n", " "))
