from __future__ import annotations

import os
from typing import Literal, Optional
import shutil
import platform

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

from .browser_downloader import ensure_chrome_for_testing, ensure_chromedriver_for_testing


def _find_browser_binary(browser: str) -> Optional[str]:
    """Try to locate a browser binary on common paths if not provided.
    Returns absolute path or None.
    """
    system = platform.system().lower()
    if browser == "chrome":
        # env var override
        env_bin = os.environ.get("CHROME_BINARY")
        if env_bin and os.path.exists(env_bin):
            return env_bin
        # PATH lookup
        which = shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chrome.exe")
        if which:
            return which
        # Common Windows locations
        if system == "windows":
            candidates = [
                r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            ]
            for c in candidates:
                if os.path.exists(c):
                    return c
    elif browser == "firefox":
        env_bin = os.environ.get("FIREFOX_BINARY")
        if env_bin and os.path.exists(env_bin):
            return env_bin
        which = shutil.which("firefox") or shutil.which("firefox.exe")
        if which:
            return which
        if system == "windows":
            candidates = [
                r"C:\\Program Files\\Mozilla Firefox\\firefox.exe",
                r"C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe",
            ]
            for c in candidates:
                if os.path.exists(c):
                    return c
    return None


def create_driver(
    browser: Literal["chrome", "firefox"] = "chrome",
    headless: bool = False,
    window_size: str = "1920,1080",
) -> webdriver.Remote:
    browser = browser.lower()
    if browser not in ("chrome", "firefox"):
        raise ValueError("Unsupported browser. Use 'chrome' or 'firefox'.")

    width, height = map(int, window_size.split(","))

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument(f"--window-size={window_size}")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if headless:
            options.add_argument("--headless=new")
        chrome_binary = _find_browser_binary("chrome")
        portable_driver_path = None
        portable_mode = False
        # Prefer local Chrome if found; otherwise download portable Chrome for Testing
        try:
            if chrome_binary:
                options.binary_location = chrome_binary
                # Use Selenium Manager to resolve the correct chromedriver automatically
                try:
                    driver = webdriver.Chrome(options=options)
                except Exception:
                    # Fallback to webdriver-manager in case Selenium Manager is blocked
                    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            else:
                auto_bin = ensure_chrome_for_testing()
                if auto_bin:
                    chrome_binary = str(auto_bin)
                    options.binary_location = chrome_binary
                    portable_mode = True
                    # Get matching chromedriver for that version
                    try:
                        version = auto_bin.parent.name
                        portable_driver_path = ensure_chromedriver_for_testing(version)
                    except Exception:
                        portable_driver_path = None
                # Start with portable driver if available
                if portable_mode and portable_driver_path and os.path.exists(portable_driver_path):
                    driver = webdriver.Chrome(service=ChromeService(portable_driver_path), options=options)
                else:
                    # As a last resort try Selenium Manager without explicit binary (may fail if no Chrome installed)
                    driver = webdriver.Chrome(options=options)
        except Exception as e:
            msg = (
                "Failed to start Chrome. Tried local install, Selenium Manager, and portable Chrome.\n"
                f"Binary used: {chrome_binary or 'not found'}\n"
                "Options: \n"
                "  1) Install Google Chrome, or set CHROME_BINARY to the executable,\n"
                "  2) Ensure network allows Selenium Manager to download drivers,\n"
                "  3) Try --browser firefox if Firefox is available.\n"
                f"Original error: {e}"
            )
            raise RuntimeError(msg) from e
        driver.set_window_size(width, height)
    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        firefox_binary = _find_browser_binary("firefox")
        if firefox_binary:
            options.binary = firefox_binary
        try:
            # Prefer Selenium Manager to resolve geckodriver automatically
            driver = webdriver.Firefox(options=options)
        except Exception as e:
            # Fallback to webdriver-manager
            try:
                driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
            except Exception:
                msg = (
                    "Failed to start Firefox. Ensure Firefox is installed or set FIREFOX_BINARY to the executable path.\n"
                    f"Tried binary: {firefox_binary or 'not found'}\n"
                    "Alternatively run with --browser chrome if Chrome is installed.\n"
                    f"Original error: {e}"
                )
                raise RuntimeError(msg) from e
        driver.set_window_size(width, height)

    return driver
