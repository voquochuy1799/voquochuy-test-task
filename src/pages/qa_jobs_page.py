from __future__ import annotations

from typing import List
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

from .base_page import BasePage


class QAJobsPage(BasePage):
    SEE_ALL_QA = (
        By.XPATH,
        "//a[contains(@href,'positions')][contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'see all qa jobs')] | //button[contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'see all qa jobs')]",
    )
    FILTER_DEPT_DROPDOWN = (By.ID, "select2-filter-by-department-container")
    FILTER_DEPT_ARROW = (By.XPATH, "//span[@id='select2-filter-by-department-container']/ancestor::span[contains(@class,'select2-selection')]")
    FILTER_LOC_DROPDOWN = (By.ID, "select2-filter-by-location-container")
    FILTER_LOC_ARROW = (By.XPATH, "//span[@id='select2-filter-by-location-container']/ancestor::span[contains(@class,'select2-selection')]")
    SELECT2_INPUT = (By.XPATH, "//input[@class='select2-search__field']")
    JOB_LIST = (By.CSS_SELECTOR, "div.position-list div.position-list-item")
    JOB_POS = (By.CSS_SELECTOR, ".position-title")
    JOB_DEPT = (By.CSS_SELECTOR, ".position-department")
    JOB_LOC = (By.CSS_SELECTOR, ".position-location")
    VIEW_ROLE_BTN = (By.XPATH, ".//a[contains(@class,'btn') and contains(.,'View Role')]")

    def click_see_all_qa(self):
        self.scroll_into_view(self.SEE_ALL_QA)
        self.click(self.SEE_ALL_QA)
        # Wait for filters to appear on positions page
        try:
            WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(self.FILTER_DEPT_DROPDOWN))
        except TimeoutException:
            # Try minor scroll and re-wait
            self.driver.execute_script("window.scrollTo(0, 0);")
            WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(self.FILTER_DEPT_DROPDOWN))

    def _open_select_dropdown(self, arrow_locator):
        # Ensure filter area is in view
        try:
            self.scroll_into_view(arrow_locator)
        except Exception:
            pass
        self.click(arrow_locator)
        # Wait for Select2 search input to appear if used
        try:
            WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(self.SELECT2_INPUT))
        except TimeoutException:
            # Some dropdowns may not use a search input; continue
            pass

    def filter_by_department(self, department: str):
        if not self._wait_select2_results_generic("select2-filter-by-department-results"):
            # Fallback: wait for jobs counter stability to assume filters loaded then reopen
            self.wait_jobs_counter_stable()
            self._open_select_dropdown(self.FILTER_DEPT_ARROW)
            self._wait_select2_results_generic("select2-filter-by-department-results")
        self._open_select_dropdown(self.FILTER_DEPT_ARROW)
        self._scroll_results_into_view("select2-filter-by-department-results")
        # Then click desired option
        option_xpath_exact = f"//ul[@id='select2-filter-by-department-results']/li[contains(@class,'select2-results__option') and normalize-space()='{department}']"
        option_xpath_contains = f"//ul[@id='select2-filter-by-department-results']/li[contains(@class,'select2-results__option') and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{department.lower()}')]"
        try:
            el = WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.XPATH, option_xpath_exact)))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", el)
            el.click()
        except TimeoutException:
            el = WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.XPATH, option_xpath_contains)))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", el)
            el.click()

    def filter_by_location(self, location: str):
        if not self._wait_select2_results_generic("select2-filter-by-location-results"):
            self.wait_jobs_counter_stable()
            self._open_select_dropdown(self.FILTER_LOC_ARROW)
            self._wait_select2_results_generic("select2-filter-by-location-results")
        self._open_select_dropdown(self.FILTER_LOC_ARROW)
        self._scroll_results_into_view("select2-filter-by-location-results")
        # Then click desired option
        option_xpath_exact = f"//ul[@id='select2-filter-by-location-results']/li[contains(@class,'select2-results__option') and normalize-space()='{location}']"
        option_xpath_contains = f"//ul[@id='select2-filter-by-location-results']/li[contains(@class,'select2-results__option') and contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), '{location.lower()}')]"
        try:
            el = WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.XPATH, option_xpath_exact)))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", el)
            el.click()
        except TimeoutException:
            el = WebDriverWait(self.driver, self.timeout).until(EC.element_to_be_clickable((By.XPATH, option_xpath_contains)))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", el)
            el.click()

    def get_job_cards(self):
        return self.wait_all_present(self.JOB_LIST)

    def _wait_select2_results(self, results_ul_id: str, min_items: int = 1):
        """Wait until Select2 results ul has at least min_items li elements."""
        ul_locator = (By.ID, results_ul_id)
        WebDriverWait(self.driver, self.timeout).until(EC.presence_of_element_located(ul_locator))
        WebDriverWait(self.driver, self.timeout).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, f"#{results_ul_id} li.select2-results__option")) > min_items
        )

    def _wait_select2_results_generic(self, expected_id: str, min_items: int = 0) -> bool:
        """Attempt to wait for a specific results UL by id; fallback to any matching pattern.
        Returns True if results list found, else False.
        """
        try:
            self._wait_select2_results(expected_id, min_items)
            return True
        except TimeoutException:
            # Look for any select2 results list for department/location
            pattern_xpath = "//ul[starts-with(@id,'select2-filter-by-') and contains(@id,'-results') and count(li) > 0]"
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, pattern_xpath)))
                return True
            except TimeoutException:
                return False

    def _scroll_results_into_view(self, results_ul_id: str):
        try:
            ul = self.driver.find_element(By.ID, results_ul_id)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ul)
        except Exception:
            pass

    def wait_jobs_counter_stable(self, stable_seconds: float = 3, timeout: float = 10):
        """Fallback: wait until p#resultCounter text remains unchanged for stable_seconds."""
        start = time.time()
        last_text = None
        stable_start = None
        while time.time() - start < timeout:
            try:
                el = self.driver.find_element(By.ID, "resultCounter")
                txt = el.text.strip()
            except Exception:
                time.sleep(0.5)
                continue
            if txt == last_text:
                stable_start = stable_start or time.time()
                if time.time() - stable_start >= stable_seconds:
                    return txt
            else:
                stable_start = None
                last_text = txt
            time.sleep(0.5)
        return last_text

    def assert_jobs_match(self, position_contains: str, dept_contains: str, loc_contains: str) -> list[str]:
        errors: List[str] = []
        cards = self.get_job_cards()
        for idx, card in enumerate(cards, start=1):
            pos = card.find_element(*self.JOB_POS).text
            dept = card.find_element(*self.JOB_DEPT).text
            loc = card.find_element(*self.JOB_LOC).text
            if position_contains not in pos:
                errors.append(f"Card {idx} position mismatch: '{pos}'")
            if dept_contains not in dept:
                errors.append(f"Card {idx} department mismatch: '{dept}'")
            if loc_contains not in loc:
                errors.append(f"Card {idx} location mismatch: '{loc}'")
        return errors

    def open_first_job_in_lever(self):
        cards = self.get_job_cards()
        if not cards:
            raise AssertionError("No job cards found")
        card = cards[0]
        # Hover before clicking View Role
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
        view_btn = card.find_element(*self.VIEW_ROLE_BTN)
        ActionChains(self.driver).move_to_element(view_btn).perform()
        before = set(self.driver.window_handles)
        view_btn.click()
        # If a new tab opens, switch to it
        WebDriverWait(self.driver, self.timeout).until(lambda d: len(set(d.window_handles) - before) > 0)
        after = set(self.driver.window_handles)
        new = list(after - before)
        if new:
            self.driver.switch_to.window(new[0])
