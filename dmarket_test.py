import hashlib
import hmac
import os
import time
import winreg

import requests

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def get_key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


PUB = get_key("DMARKET_PUBLIC_KEY")
SEC = get_key("DMARKET_SECRET_KEY")
print("public len", len(PUB), "secret len", len(SEC))


def try_variant(label, signer, url, path):
    ts = str(int(time.time() * 1000))
    sig = signer("GET", path, "", ts)
    headers = {**UA, "X-Api-Key": PUB, "X-Request-Sign": ts + sig}
    try:
        r = requests.get(url, headers=headers, timeout=30)
        body = r.text[:150].replace("\n", " ")
        print(f"{label}: {r.status_code} {body}")
        return r.status_code == 200
    except Exception as e:  # noqa: BLE001
        print(f"{label}: ERR {type(e).__name__}")
        return False


url = "https://api.dmarket.com/account/v1/balance"
path = "/account/v1/balance"

variants = {
    "hmac(m+p+b+ts)": lambda m, p, b, ts: hmac.new(
        SEC.encode(), (m + p + b + ts).encode(), hashlib.sha256
    ).hexdigest(),
    "sha256(m+p+b+ts+secret)": lambda m, p, b, ts: hashlib.sha256(
        (m + p + b + ts + SEC).encode()
    ).hexdigest(),
    "hmac(m+p+ts)": lambda m, p, b, ts: hmac.new(
        SEC.encode(), (m + p + ts).encode(), hashlib.sha256
    ).hexdigest(),
}

for label, fn in variants.items():
    if try_variant(label, fn, url, path):
        print("WORKING VARIANT:", label)
        break
