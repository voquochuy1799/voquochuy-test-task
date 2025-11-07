# Test Automation Repo: UI + API (Pytest, Selenium, Allure)

This repository contains:

- UI tests (Python + Pytest + Selenium) using Page Object Model.
- API tests (Pytest + requests) for Petstore Swagger (pet endpoints) with CRUD happy/negative cases.
- Allure reporting, retries, parallel execution, and GitHub Actions CI with notifications.

## Project structure

- `tests/ui` — UI tests
- `tests/api` — API tests
- `src/pages` — Page Objects and locators
- `src/utils` — Utilities (driver factory, API client, config)
- `pytest.ini` — Pytest config (markers, options)

## Prerequisites

- Python 3.11+
- Google Chrome and/or Mozilla Firefox installed
- On Windows, run commands in PowerShell

## Setup

```powershell
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

## How to run

Common parameters:

- `--browser` chrome|firefox (default: chrome)
- `--env` dev|qa|uat (default: qa)
- `--tags` pytest expression or marker (e.g., smoke)
- `--headless` run browser headless

Run all tests in parallel (6 workers), with retries (3):

```powershell
pytest -n 6 --reruns 3 --reruns-delay 2 --alluredir=allure-results
```

Run only smoke tests on QA in Chrome:

```powershell
pytest -m smoke --env qa --browser chrome -n 6 --reruns 3 --alluredir=allure-results
```

UI only:

```powershell
pytest tests/ui -n 6 --reruns 3 --alluredir=allure-results --browser chrome
```

API only:

```powershell
pytest tests/api -n 6 --reruns 3 --alluredir=allure-results
```

View Allure report locally (requires Allure CLI installed):

```powershell
allure serve allure-results
```

## Notifications

SMTP with an App Password (e.g., Gmail) is used to send CI email summaries.

Secrets required:

- `MAIL_USERNAME` — your mailbox address (e.g., yourname@gmail.com)
- `MAIL_PASSWORD` — the App Password generated for your mailbox
- `NOTIFY_EMAIL_TO` — Recipient email

- Secrets required:
  - `MAIL_USERNAME` — your mailbox address (e.g., yourname@gmail.com)
  - `MAIL_PASSWORD` — the App Password generated for your mailbox
  - `NOTIFY_EMAIL_TO` — Recipient email

How to generate an App Password (Gmail example):

- Turn on 2‑Step Verification at https://myaccount.google.com/security
- After 2FA is enabled, open “App passwords” on the same page
- Create a new app password (you can name it like “GitHub Actions CI”)
- Copy the 16‑character password (without spaces) into the `MAIL_PASSWORD` secret

Notes:

- SMTP defaults to Gmail’s server (smtp.gmail.com:465). If you need Outlook/Yahoo/iCloud, update the workflow step accordingly.
- Email contains: totals (tests/passed/failures/errors/skipped), pass rate, environment, browser, run URL, and artifacts info.
- Microsoft Teams notification has been removed. You can re-add it later by restoring the step in `.github/workflows/tests.yml` if needed.

## Notes

- The driver is managed automatically via webdriver-manager/Selenium Manager. The browser window is sized to 1920x1080.
- On UI failures, a screenshot is attached to the Allure report.
- An auth token placeholder is included for UI/API collaboration; set `API_TOKEN` env var if required.
- If your system doesn't have Chrome/Firefox installed:
  - Chrome: the framework auto-downloads a portable "Chrome for Testing" to `.browsers/` and uses it.
  - Firefox: install Firefox or set `FIREFOX_BINARY` to the executable path.
  - You can also run headless via `--headless`.

Environment variables:

- `CHROME_BINARY` — absolute path to a Chrome executable (overrides auto-detection and auto-download).
- `FIREFOX_BINARY` — absolute path to a Firefox executable.

## Pipelines

GitHub Actions workflow `.github/workflows/tests.yml` runs on push and PR, defaults to `qa` env, runs smoke tests in parallel with retries, and uploads Allure results as artifacts. If SMTP email secrets are set it sends an HTML summary.

## Debugging with Python Test Explorer (VS Code)

1. Install extensions:

   - Python (ms-python.python)
   - Python Debugger (ms-python.debugpy)
   - Python Test Explorer (littlefoxteam.vscode-python-test-adapter)

2. The workspace includes `.vscode/settings.json` to enable pytest discovery and default arguments, and `.vscode/launch.json` with handy debug configs:

   - "Debug All Tests (smoke, chrome)": runs smoke tests against QA, Chrome.
   - "Debug UI Test (firefox)": runs the Insider UI flow on Firefox.
   - "Debug API Tests (dev)": runs API smoke tests with parallelism and retries.

3. To debug with custom parameters from Test Explorer:
   - Open the Testing view (beaker icon), ensure tests are discovered.
   - Use the gear icon to pick "Debug" or the play icon to run; the configured args in `.vscode/settings.json` are applied.
   - To override, launch from Run and Debug panel using one of the launch configurations and change `--browser`, `--env`, or markers in the args.

Environment variables: - `TEST_ENV`, `BROWSER`, and `TAGS` can be set in `.env` or via the launch configuration `env` block.

### Troubleshooting Test Explorer

- If no tests are discovered:
  - Make sure `pytest` is installed in the selected interpreter (check bottom-right of VS Code).
  - Open Command Palette → "Python: Configure Tests" → Pick `pytest` and the `tests` folder.
  - Ensure `.vscode/settings.json` has `"python.testing.pytestEnabled": true` and `"python.testing.pytestArgs": ["tests"]`.
- If the Debug button runs without your CLI options:
  - Use the provided Run and Debug configurations (Run panel) which pass `--browser`/`--env`.
  - Or add your own test args under `pytest-explorer.pytestArgs` in `.vscode/settings.json`.
- If the interpreter is wrong:
  - Set `python.defaultInterpreterPath` in `.vscode/settings.json` or select interpreter via the Python status bar.
