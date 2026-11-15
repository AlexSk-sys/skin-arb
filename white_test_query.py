import json
import os
import re
import winreg
from pathlib import Path

import requests


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


K = key("WHITE_API_KEY")
text = (Path(__file__).resolve().parent / "white_queries.txt").read_text(encoding="utf-8")
m = re.search(r"### InstantSellList\n(.*?)(?=\n### |\Z)", text, re.S)
query = "query " + m.group(1).strip()

for app in ("CSGO", "CS2", "csgo", "cs2"):
    payload = {
        "query": query,
        "variables": {"appId": app, "forwardPagination": {"first": 20}},
    }
    try:
        r = requests.post(
            "https://api.white.market/graphql/api",
            json=payload,
            headers={
                "User-Agent": "Mozilla/5.0 skin-arb/1.0",
                "Content-Type": "application/json",
                "authToken": K,
            },
            timeout=40,
        )
        print(f"appId={app}: {r.status_code} {r.text[:400]}")
        if r.status_code == 200 and '"data"' in r.text and '"errors"' not in r.text:
            break
    except Exception as e:  # noqa: BLE001
        print(f"appId={app}: ERR {type(e).__name__}")
