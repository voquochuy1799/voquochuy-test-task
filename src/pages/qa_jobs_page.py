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

    def filter_by_department(self, department: str, max_wait: int = 300, interval: int = 3):
        """Pure user-action approach: keep clicking dropdown arrow until >1 options show, then pick match.
        Extended wait: up to 5 minutes (300s) retrying every 3s.
        No URL/query param tricks, no counter polling.
        """
        print(f"[dept] START collecting options (pure retry, max {max_wait}s)")
        opts = self._retry_collect_options(
            self.FILTER_DEPT_ARROW,
            prefix="select2-filter-by-department",
            max_wait=max_wait,
            interval=interval,
        )
        print(f"[dept] options collected: {[t for _, t in opts]}")
        chosen = self._choose_best_match(department, opts)
        if not chosen:
            raise TimeoutException(f"[dept] No matching option for '{department}' in {[t for _, t in opts]}")
        el = chosen[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", el)
        el.click()
        print(f"[dept] clicked '{chosen[1]}'")

    def filter_by_location(self, location: str, max_wait: int = 300, interval: int = 3):
        """Pure user-action approach for location dropdown (same pattern as department)."""
        print(f"[loc] START collecting options (pure retry, max {max_wait}s)")
        opts = self._retry_collect_options(
            self.FILTER_LOC_ARROW,
            prefix="select2-filter-by-location",
            max_wait=max_wait,
            interval=interval,
        )
        print(f"[loc] options collected: {[t for _, t in opts]}")
        chosen = self._choose_best_match(location, opts)
        if not chosen:
            raise TimeoutException(f"[loc] No matching option for '{location}' in {[t for _, t in opts]}")
        el = chosen[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", el)
        el.click()
        print(f"[loc] clicked '{chosen[1]}'")
        self._debug_dump_cards(limit=5)

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
        self.wait_jobs_counter_stable()
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

    # -------------------- New helper methods for robust Select2 interaction -------------------- #

    # Removed _select2_pick_option; simplified retry logic implemented in _retry_collect_options + _choose_best_match

    def _retry_collect_options(self, arrow_locator, prefix: str, max_wait: int, interval: int):
        """Retry clicking dropdown arrow until more than one option is visible or timeout reached."""
        deadline = time.time() + max_wait
        attempt = 0
        last_seen = []
        while time.time() < deadline:
            attempt += 1
            try:
                self._open_select_dropdown(arrow_locator)
            except Exception:
                pass
            opts = self._collect_select2_options(results_ul_id_prefix=prefix)
            texts = [t for _, t in opts]
            print(f"[select2] attempt {attempt} options: {texts}")
            last_seen = texts
            if len(opts) > 1:
                return opts
            time.sleep(interval)
        raise TimeoutException(f"[select2] Timeout after {max_wait}s; last seen options: {last_seen}")

    def _debug_dump_cards(self, limit: int = 5):
        try:
            cards = self.get_job_cards()
            print(f"[cards] total: {len(cards)}")
            for i, c in enumerate(cards[:limit], start=1):
                try:
                    pos = c.find_element(*self.JOB_POS).text
                except Exception:
                    pos = ""
                try:
                    dept = c.find_element(*self.JOB_DEPT).text
                except Exception:
                    dept = ""
                try:
                    loc = c.find_element(*self.JOB_LOC).text
                except Exception:
                    loc = ""
                print(f"[cards] {i}: pos='{pos}' dept='{dept}' loc='{loc}'")
        except Exception as e:
            print(f"[cards] dump failed: {e}")

    # Removed URL/counter-based fallback helpers (_any_card_contains, _has_result_counter, _get_result_counter, _wait_param_and_counter)

    def _collect_select2_options(self, results_ul_id_prefix: str):
        # Find any ul whose id starts with prefix and ends with -results
        uls = self.driver.find_elements(By.XPATH, f"//ul[starts-with(@id,'{results_ul_id_prefix}') and contains(@id,'-results')]")
        for ul in uls:
            if not ul.is_displayed():
                continue
            lis = ul.find_elements(By.CSS_SELECTOR, "li.select2-results__option:not(.select2-results__option--loading)")
            collected = []
            for li in lis:
                txt = li.text.strip()
                if txt:
                    collected.append((li, txt))
            if collected:
                return collected
        return []

    def _choose_best_match(self, target: str, options: list[tuple]):
        target_norm = target.lower().strip()
        # exact
        exact = [o for o in options if o[1].strip() == target]
        if exact:
            return exact[0]
        # case-ins contains
        ci_contains = [o for o in options if target_norm in o[1].lower()]
        if ci_contains:
            return ci_contains[0]
        # fuzzy: ignore punctuation & spaces
        import re
        def norm(s: str):
            return re.sub(r"[^a-z0-9]", "", s.lower())
        tn = norm(target_norm)
        fuzzy = [o for o in options if tn and tn in norm(o[1])]
        if fuzzy:
            return fuzzy[0]
        return None

    # Removed slug/diagnostic/query param fallback helpers (_slugify, _select2_diagnostics, _slug_variants, _query_param_filter)
