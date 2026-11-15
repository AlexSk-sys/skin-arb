import os
import re
import winreg
from pathlib import Path

# Steam install path from the registry.
steam_path = None
try:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
        steam_path = winreg.QueryValueEx(k, "SteamPath")[0]
except OSError:
    pass
print("SteamPath:", steam_path)

candidates: list[Path] = []
if steam_path:
    base = Path(steam_path)
    for rel in ("config/config.vdf", "config/loginusers.vdf"):
        p = base / rel
        if p.exists():
            candidates.append(p)
    for d in (base / "userdata").glob("*"):
        for rel in ("config/localconfig.vdf", "config/config.vdf"):
            p = d / rel
            if p.exists():
                candidates.append(p)

print("files found:", len(candidates))
for p in candidates:
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    tokens = re.findall(r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", text)
    print(f"{p} | jwt found: {len(tokens)} | len: {[len(t) for t in tokens][:3]}")
