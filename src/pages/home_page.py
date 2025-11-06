from __future__ import annotations

from selenium.webdriver.common.by import By

from .base_page import BasePage, Locator


class HomePage(BasePage):
    COMPANY_MENU = (By.XPATH, "//a[contains(@class,'nav-link') and normalize-space()='Company']")
    CAREERS_LINK = (By.XPATH, "//a[contains(@href,'/careers') and normalize-space()='Careers']")
    COOKIE_ACCEPT = (By.XPATH, "//a[contains(@class,'icon-close') or .='Accept All' or contains(@id,'onetrust-accept')]" )

    def accept_cookies_if_present(self):
        try:
            self.click(self.COOKIE_ACCEPT)
        except Exception:
            pass

    def open_careers(self):
        self.hover(self.COMPANY_MENU)
        self.click(self.CAREERS_LINK)
