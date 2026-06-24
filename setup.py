# TEST-IA: 
#!/usr/bin/env python3
"""
Setup script for TigerBeetle production environment.
- Downloads TigerBeetle binary if missing
- Formats the data file if missing
- Installs and enables the systemd service
- Starts TigerBeetle in production
"""

import os
import sys
import stat
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
BINARY     = SCRIPT_DIR / "tigerbeetle"
DATA_FILE  = SCRIPT_DIR / "tb_data.tigerbeetle"
SERVICE_FILE = SCRIPT_DIR / "tigerbeetle.service"
SYSTEMD_DIR  = Path("/etc/systemd/system")

ARCH_MAP = {"x86_64": "x86_64", "aarch64": "aarch64", "arm64": "aarch64"}
DOWNLOAD_URL = (
    "https://github.com/tigerbeetle/tigerbeetle/releases/latest/download/"
    "tigerbeetle-{arch}-linux.zip"
)


def run(cmd: list[str], check: bool = True, **kw) -> subprocess.CompletedProcess:
    print(f"  >> {' '.join(str(c) for c in cmd)}")
    return subprocess.run(cmd, check=check, **kw)


def step(msg: str) -> None:
    print(f"\n[*] {msg}")


# ── 1. Download TigerBeetle if missing ──────────────────────────────────────
def install_tigerbeetle() -> None:
    if BINARY.exists():
        print(f"    tigerbeetle already present: {BINARY}")
        return

    step("Downloading TigerBeetle binary…")
    machine = os.uname().machine
    arch = ARCH_MAP.get(machine)
    if arch is None:
        sys.exit(f"Unsupported architecture: {machine}")

    url  = DOWNLOAD_URL.format(arch=arch)
    zip_path = SCRIPT_DIR / "tigerbeetle.zip"

    print(f"    {url}")
    urllib.request.urlretrieve(url, zip_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(SCRIPT_DIR)
    zip_path.unlink(missing_ok=True)

    BINARY.chmod(BINARY.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"    Installed: {BINARY}")


# ── 2. Format data file if missing ──────────────────────────────────────────
def format_data() -> None:
    if DATA_FILE.exists():
        print(f"    Data file already exists: {DATA_FILE}")
        return

    step("Formatting TigerBeetle data file…")
    run([
        str(BINARY), "format",
        "--cluster=0", "--replica=0", "--replica-count=1",
        str(DATA_FILE),
    ])


# ── 3. Install systemd service ───────────────────────────────────────────────
def install_service() -> None:
    step("Installing systemd service…")

    if not SERVICE_FILE.exists():
        sys.exit(f"Service file not found: {SERVICE_FILE}")

    dest = SYSTEMD_DIR / SERVICE_FILE.name
    try:
        shutil.copy2(SERVICE_FILE, dest)
    except PermissionError:
        sys.exit("Permission denied – run this script with sudo.")

    run(["systemctl", "daemon-reload"])
    run(["systemctl", "enable", "tigerbeetle"])
    print("    Service enabled for startup.")


# ── 4. Start production ──────────────────────────────────────────────────────
def start_production() -> None:
    step("Starting TigerBeetle production service…")
    run(["systemctl", "start", "tigerbeetle"])
    run(["systemctl", "status", "tigerbeetle", "--no-pager"], check=False)


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== TigerBeetle Setup ===")
    os.chdir(SCRIPT_DIR)

    install_tigerbeetle()
    format_data()
    install_service()
    start_production()

    print("\n=== Setup complete ===")
    print("  Logs : journalctl -u tigerbeetle -f")
    print("  Stop : systemctl stop tigerbeetle")

