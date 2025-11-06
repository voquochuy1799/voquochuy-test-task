import pytest
import allure
import pytest_check as check

from src.pages.home_page import HomePage
from src.pages.careers_page import CareersPage
from src.pages.qa_jobs_page import QAJobsPage


@allure.feature("Insider Careers")
@allure.story("QA jobs filtering and Lever redirection")
@pytest.mark.ui
@pytest.mark.smoke
def test_insider_careers_qa_jobs_flow(driver, env):
    home = HomePage(driver)
    careers = CareersPage(driver)
    qa = QAJobsPage(driver)

    with allure.step("Open Insider home page"):
        home.open(env.base_url)
        home.accept_cookies_if_present()
        check.is_true("Insider" in driver.title, "Home page title should contain 'Insider'")

    with allure.step("Navigate to Careers via Company menu"):
        home.open_careers()
        check.is_true("Careers" in driver.title or "careers" in driver.current_url, "Careers page should open")

    with allure.step("Verify Careers page blocks (Locations, Teams, Life at Insider)"):
        check.is_true(careers.blocks_are_visible(), "Careers blocks should be visible")

    with allure.step("Open QA jobs section and see all QA jobs"):
        careers.go_to_qa_jobs_direct(env.base_url)
        home.accept_cookies_if_present()
        qa.click_see_all_qa()

    with allure.step("Filter jobs by Department=Quality Assurance and Location=Istanbul, Turkiye"):
        qa.filter_by_department("Quality Assurance")
        qa.filter_by_location("Istanbul, Turkiye")
        cards = qa.get_job_cards()
        check.greater(len(cards), 0, "Jobs list should not be empty")

    with allure.step("Validate each job's Position/Department/Location"):
        errors = qa.assert_jobs_match("Quality Assurance", "Quality Assurance", "Istanbul, Turkiye")
        check.equal(errors, [], f"Job card content mismatches: {errors}")

    with allure.step("Open first job 'View Role' and verify Lever page"):
        qa.open_first_job_in_lever()
        # Lever pages are hosted at jobs.lever.co or similar
        check.is_true("lever.co" in driver.current_url, f"Expected to be redirected to Lever, got {driver.current_url}")
