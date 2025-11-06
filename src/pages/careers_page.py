from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class CareersPage(BasePage):
    # Primary IDs + fallback to headings text
    LOCATIONS_BLOCK = (
        By.XPATH,
        "//section[contains(@id,'career-our-location')] | //section[.//h2[contains(normalize-space(),'Locations')] or .//h3[contains(normalize-space(),'Locations')]]",
    )
    TEAMS_BLOCK = (
        By.XPATH,
        "//section[contains(@id,'career-find-our-calling')] | //section[.//h2[contains(.,'Teams') or contains(.,'Find your calling')] or .//h3[contains(.,'Teams') or contains(.,'Find your calling')]]",
    )
    LIFE_BLOCK = (
        By.XPATH,
        "//section[contains(@id,'career-life-at-insider')] | //section[.//h2[contains(.,'Life at Insider')] or .//h3[contains(.,'Life at Insider')]]",
    )


    def blocks_are_visible(self) -> bool:
        # Some content loads as you scroll; also cookie banners can block clicks
        self._dismiss_cookies_if_any()
        # Scroll progressively to trigger lazy-loading
        for y in (200, 800, 1400, 2200, 3000, 4000):
            try:
                self.driver.execute_script(f"window.scrollTo(0, {y});")
            except Exception:
                pass
        # Now wait for blocks to be visible using robust locators
        self.wait_visible(self.LOCATIONS_BLOCK)
        self.wait_visible(self.TEAMS_BLOCK)
        self.wait_visible(self.LIFE_BLOCK)
        return True

    def go_to_qa_jobs_direct(self, base_url: str):
        qa_url = base_url.rstrip("/") + "/careers/quality-assurance/"
        self.open(qa_url)
        self._dismiss_cookies_if_any()

    def _dismiss_cookies_if_any(self):
        candidates = [
            (By.ID, "onetrust-accept-btn-handler"),
            (By.XPATH, "//button[contains(@id,'onetrust-accept') or normalize-space()='Accept All']"),
            (By.XPATH, "//a[contains(@class,'icon-close')]")
        ]
        for loc in candidates:
            try:
                WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(loc)).click()
                break
            except Exception:
                continue
