from __future__ import annotations

from typing import Tuple

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


Locator = Tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 20):
        self.driver = driver
        self.timeout = timeout

    # Wait helpers
    def wait_visible(self, locator: Locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_clickable(self, locator: Locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_present(self, locator: Locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_all_present(self, locator: Locator):
        return WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_all_elements_located(locator)
        )

    # Actions
    def click(self, locator: Locator):
        el = self.wait_clickable(locator)
        el.click()

    def hover(self, locator: Locator):
        el = self.wait_visible(locator)
        ActionChains(self.driver).move_to_element(el).perform()

    def send_keys(self, locator: Locator, text: str, clear: bool = True):
        el = self.wait_visible(locator)
        if clear:
            el.clear()
        el.send_keys(text)

    def scroll_into_view(self, locator: Locator):
        el = self.wait_present(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)

    def open(self, url: str):
        self.driver.get(url)
