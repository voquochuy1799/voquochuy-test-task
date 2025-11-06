import os
from dataclasses import dataclass


def _get_env(name: str, default: str | None = None) -> str:
    val = os.environ.get(name, default)
    if val is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val


@dataclass
class EnvConfig:
    name: str
    base_url: str
    careers_url: str = "https://useinsider.com/careers/"
    qa_jobs_url: str = "https://useinsider.com/careers/quality-assurance/"


def get_env_config(env: str | None = None) -> EnvConfig:
    env = (env or os.environ.get("TEST_ENV") or "qa").lower()
    # Using public site, same across envs; pattern supports dev/uat if ever differ
    base_url = "https://useinsider.com/"
    return EnvConfig(name=env, base_url=base_url)


def get_notification_targets() -> dict:
    return {
        "teams_webhook": os.environ.get("TEAMS_WEBHOOK_URL", ""),
        "email_to": os.environ.get("NOTIFY_EMAIL_TO", ""),
    }
