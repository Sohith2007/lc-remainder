from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
import json
import os

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "LeetCode Daily Reminder"
    supabase_url: str = ""
    supabase_key: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_sender: str = ""
    reminder_recipient: str = ""
    reminder_hour: int = 8
    reminder_minute: int = 0
    timezone: str = "UTC"
    leetcode_daily_url: str = "https://leetcode.com/problemset/all/"
    cors_origins: list[str] = field(default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"])

    @property
    def reminder_time(self) -> time:
        return time(self.reminder_hour, self.reminder_minute)


def load_settings() -> Settings:
    cors_origins_str = os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://localhost:3000"]')
    try:
        cors_origins = json.loads(cors_origins_str)
    except json.JSONDecodeError:
        cors_origins = ["http://localhost:5173", "http://localhost:3000"]
    
    return Settings(
        app_name=os.getenv("APP_NAME", "LeetCode Daily Reminder"),
        supabase_url=os.getenv("SUPABASE_URL", ""),
        supabase_key=os.getenv("SUPABASE_KEY", ""),
        smtp_host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
        smtp_port=int(os.getenv("SMTP_PORT", "587")),
        smtp_username=os.getenv("SMTP_USERNAME", ""),
        smtp_password=os.getenv("SMTP_PASSWORD", ""),
        smtp_sender=os.getenv("SMTP_SENDER", ""),
        reminder_recipient=os.getenv("REMINDER_RECIPIENT", ""),
        reminder_hour=int(os.getenv("REMINDER_HOUR", "8")),
        reminder_minute=int(os.getenv("REMINDER_MINUTE", "0")),
        timezone=os.getenv("TIMEZONE", "UTC"),
        leetcode_daily_url=os.getenv(
            "LEETCODE_DAILY_URL",
            "https://leetcode.com/problemset/all/",
        ),
        cors_origins=cors_origins,
    )


def validate_email_settings(settings: Settings) -> list[str]:
    missing = []
    if not settings.supabase_url:
        missing.append("SUPABASE_URL")
    if not settings.supabase_key:
        missing.append("SUPABASE_KEY")
    if not settings.smtp_username:
        missing.append("SMTP_USERNAME")
    if not settings.smtp_password:
        missing.append("SMTP_PASSWORD")
    if not settings.smtp_sender:
        missing.append("SMTP_SENDER")
    return missing