import os
import time
import winreg

import requests

UA = {"User-Agent": "Mozilla/5.0 skin-arb/1.0", "Accept": "application/json"}
PID = "31208293"


def key(name: str) -> str:
    if os.environ.get(name):
        return os.environ[name]
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
        return winreg.QueryValueEx(k, name)[0]


WX = key("WAXPEER_API_KEY")
last = None
for attempt in range(25):
    try:
        chk = requests.get(
            "https://api.waxpeer.com/v1/check-many-steam",
            params={"api": WX, "id": PID},
            headers=UA,
            timeout=30,
        ).json()
        trade = (chk.get("trades") or [{}])[0]
        status = trade.get("status")
        if status != last:
            print(f"{time.strftime('%H:%M:%S')} status {status} done {trade.get('done')} reason {trade.get('reason')}")
            last = status
        if status in (5, 6):
            break
    except Exception as e:  # noqa: BLE001
        print(f"{time.strftime('%H:%M:%S')} retry after {type(e).__name__}")
    time.sleep(12)
