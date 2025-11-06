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

CI supports posting a summary to Microsoft Teams and/or email. Configure secrets in your repository:

- `TEAMS_WEBHOOK_URL` — Incoming webhook URL
- `NOTIFY_EMAIL_TO` — Email address to notify (requires Actions runner to support sending mail or a custom action)

## Notes

- The driver is managed automatically via webdriver-manager/Selenium Manager. The browser window is sized to 1920x1080.
- On UI failures, a screenshot is attached to the Allure report.
- An auth token placeholder is included for UI/API collaboration; set `API_TOKEN` env var if required.
- If your system doesn't have Chrome/Firefox on PATH, set `CHROME_BINARY` or `FIREFOX_BINARY` to the browser executable path. You can also run headless via `--headless`.

## Pipelines

GitHub Actions workflow `.github/workflows/tests.yml` runs on push and PR, defaults to `qa` env, runs smoke tests, parallel `-n 6`, retries up to 3 times, and uploads Allure results as an artifact. It posts an optional Teams message with pass/fail counts and a link to the artifact.

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
