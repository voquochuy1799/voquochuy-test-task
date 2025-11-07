from __future__ import annotations

import os
import sys
import json
import zipfile
from pathlib import Path
from typing import Optional

import requests


CFD_STABLE_URL = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"


def _platform_key() -> str:
    if sys.platform.startswith("win"):
        # Assume 64-bit on modern Windows
        return "win64"
    elif sys.platform == "darwin":
        return "mac-arm64" if ("arm64" in os.uname().machine) else "mac-x64"
    else:
        return "linux64"


def _http_get(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)


def ensure_chrome_for_testing(cache_dir: Path | str = ".browsers") -> Optional[Path]:
    """Download Chrome for Testing (stable) for this platform if missing.
    Returns path to chrome binary, or None on failure.
    """
    try:
        platform_key = _platform_key()
        # Fetch metadata
        resp = requests.get(CFD_STABLE_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        stable = data.get("channels", {}).get("Stable") or data.get("stable") or {}
        chrome_downloads = stable.get("downloads", {}).get("chrome", [])
        record = next((d for d in chrome_downloads if d.get("platform") == platform_key), None)
        if not record:
            return None
        url = record["url"]
        version = stable.get("version", "unknown")
        base_cache = Path(cache_dir)
        target_root = base_cache / "chrome" / version
        if sys.platform.startswith("win"):
            bin_rel = Path("chrome-win64") / "chrome.exe"
        elif sys.platform == "darwin":
            bin_rel = Path("chrome-mac-arm64" if "arm64" in os.uname().machine else "chrome-mac") / "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
        else:
            bin_rel = Path("chrome-linux64") / "chrome"

        chrome_bin = target_root / bin_rel
        if chrome_bin.exists():
            return chrome_bin

        # Download and extract
        zip_name = url.split("/")[-1]
        zip_path = target_root / zip_name
        _http_get(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_root)
        try:
            zip_path.unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass
        # Make executable on unix
        try:
            chrome_bin.chmod(0o755)
        except Exception:
            pass
        return chrome_bin if chrome_bin.exists() else None
    except Exception:
        return None


def ensure_chromedriver_for_testing(version: str, cache_dir: Path | str = ".browsers") -> Optional[Path]:
    """Download chromedriver for Chrome for Testing version and return executable path."""
    try:
        platform_key = _platform_key()
        resp = requests.get(CFD_STABLE_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # If the requested version differs from Stable in feed, try to map within stable; otherwise best-effort
        channels = data.get("channels", {})
        stable = channels.get("Stable") or {}
        downloads = stable.get("downloads", {}).get("chromedriver", [])
        record = next((d for d in downloads if d.get("platform") == platform_key), None)
        if not record:
            return None
        url = record["url"]
        base_cache = Path(cache_dir)
        target_root = base_cache / "chrome" / version
        if sys.platform.startswith("win"):
            bin_rel = Path("chromedriver-win64") / "chromedriver.exe"
        elif sys.platform == "darwin":
            bin_rel = Path("chromedriver-mac-arm64" if "arm64" in os.uname().machine else "chromedriver-mac-x64") / "chromedriver"
        else:
            bin_rel = Path("chromedriver-linux64") / "chromedriver"
        driver_bin = target_root / bin_rel
        if driver_bin.exists():
            return driver_bin
        zip_name = url.split("/")[-1]
        zip_path = target_root / zip_name
        _http_get(url, zip_path)
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(target_root)
        try:
            zip_path.unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass
        try:
            driver_bin.chmod(0o755)
        except Exception:
            pass
        return driver_bin if driver_bin.exists() else None
    except Exception:
        return None
