import re
import winreg
from pathlib import Path

PATH = Path(r"C:\Users\AgentPC\Desktop\апи кс2.docx")
lines = [ln.strip() for ln in PATH.read_text(encoding="utf-8", errors="ignore").splitlines()]


def grab(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


values: dict[str, str | None] = {
    "PRICEMPIRE_API_KEY": lines[0].split()[0] if lines and lines[0] else None,
    "CSFLOAT_API_KEY": lines[1].split()[0] if len(lines) > 1 and lines[1] else None,
    "DMARKET_PUBLIC_KEY": grab(r"\(открытий\s+([0-9a-fA-F]{64})", lines[2]) if len(lines) > 2 else None,
    "DMARKET_SECRET_KEY": grab(r"закрытй\s+([0-9a-fA-F]+)", lines[3]) if len(lines) > 3 else None,
    "WAXPEER_API_KEY": grab(r"waxpeer\.com/\s*-\s*([A-Za-z0-9]+)", lines[5]) if len(lines) > 5 else None,
    "MARKET_CSGO_API_KEY": grab(r"market\.csgo\.com\s*-\s*([A-Za-z0-9]+)", lines[7]) if len(lines) > 7 else None,
    "STEAM_TRADE_URL": grab(r"(https://steamcommunity\.com/tradeoffer/new/\?\S+)", lines[9]) if len(lines) > 9 else None,
}

env = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_SET_VALUE)
for name, value in values.items():
    if not value:
        print(f"{name:<22} NOT FOUND")
        continue
    winreg.SetValueEx(env, name, 0, winreg.REG_SZ, value)
    masked = value[:4] + "…" + value[-4:] if len(value) > 10 else "***"
    print(f"{name:<22} {masked:<20} len {len(value)}")
winreg.CloseKey(env)
print("\nwritten to HKCU\\Environment")
