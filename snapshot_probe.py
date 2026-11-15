import os
import winreg

import requests


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
url = "https://api.waxpeer.com/v1/prices/snapshot"
with requests.get(url, params={"api": WX, "format": "csv"}, stream=True, timeout=60) as r:
    print("status", r.status_code, "type", r.headers.get("content-type"))
    lines = []
    total = 0
    for raw in r.iter_lines(decode_unicode=True):
        if raw is None:
            continue
        total += len(raw)
        if len(lines) < 6:
            lines.append(raw)
        if total > 200_000:
            break
for i, line in enumerate(lines):
    print(f"{i}: {line[:300]}")
