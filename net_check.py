import time

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) skin-arb/1.0"}
PROXY = {"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"}


def egress(label, proxies):
    try:
        r = requests.get("https://api.ipify.org", proxies=proxies, headers=UA, timeout=20)
        print(f"{label:<14} egress IP: {r.text.strip()}")
    except Exception as e:  # noqa: BLE001
        print(f"{label:<14} ERR {type(e).__name__}")


def latency(label, proxies, url, n=3):
    times = []
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            requests.get(url, proxies=proxies, headers=UA, timeout=30)
            times.append(time.perf_counter() - t0)
        except Exception:  # noqa: BLE001
            times.append(float("nan"))
    print(f"{label:<14} {url[:38]:<38} " + " ".join(f"{t:.2f}s" for t in times))


egress("direct", None)
egress("http-proxy", PROXY)

latency("direct", None, "https://csfloat.com/api/v1/listings?limit=1")
latency("http-proxy", PROXY, "https://csfloat.com/api/v1/listings?limit=1")
latency("direct", None, "https://market.csgo.com/api/v2/prices/USD.json")
latency("http-proxy", PROXY, "https://market.csgo.com/api/v2/prices/USD.json")
