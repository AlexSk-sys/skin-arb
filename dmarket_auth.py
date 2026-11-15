import hashlib
import hmac
import os
import time
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


PUB = key("DMARKET_PUBLIC_KEY")
SEC_FULL = key("DMARKET_SECRET_KEY")
SEC_64 = SEC_FULL[:64]

PATH = "/marketplace-api/v2/offers"
QUERY = "gameId=a8db&limit=1"
URL = "https://api.dmarket.com" + PATH + "?" + QUERY

variants = []
for secret, slabel in ((SEC_64, "sec64"), (SEC_FULL, "sec128")):
    for path, plabel in ((PATH, "path"), (PATH + "?" + QUERY, "pathq")):
        for ts_unit, tlabel in ((1000, "ms"), (1, "s")):
            for scheme in ("hmac", "sha"):
                variants.append((secret, slabel, path, plabel, ts_unit, tlabel, scheme))

for secret, slabel, path, plabel, ts_unit, tlabel, scheme in variants:
    ts = str(int(time.time() * ts_unit))
    base = "GET" + path + "" + ts
    if scheme == "hmac":
        sig = hmac.new(secret.encode(), base.encode(), hashlib.sha256).hexdigest()
    else:
        sig = hashlib.sha256((base + secret).encode()).hexdigest()
    headers = {**UA, "X-Api-Key": PUB, "X-Request-Sign": ts + sig}
    try:
        r = requests.get(URL, headers=headers, timeout=25)
    except Exception as e:  # noqa: BLE001
        print(f"{slabel} {plabel} {tlabel} {scheme} ERR {type(e).__name__}")
        continue
    print(f"{slabel} {plabel} {tlabel} {scheme}: {r.status_code} {r.text[:110].replace(chr(10), ' ')}")
    if r.status_code == 200:
        print("WORKING:", slabel, plabel, tlabel, scheme)
        break
