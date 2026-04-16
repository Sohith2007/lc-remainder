from __future__ import annotations

from datetime import date

from .emailing import build_email, send_email
from .leetcode import fetch_daily_problem
from .storage import Storage


async def refresh_and_send(
    storage: Storage,
    source_url: str,
    sender: str,
    recipients: list[str],
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    force: bool = False,
) -> str:
    problem = await fetch_daily_problem(source_url)
    storage.save_daily_problem(problem)

    today = date.today().isoformat()
    if not force and storage.was_sent(today):
        return "already-sent"

    normalized_recipients = sorted({value.strip().lower() for value in recipients if value.strip()})
    if not normalized_recipients:
        return "no-recipients"

    for recipient in normalized_recipients:
        message = build_email(problem, sender, recipient)
        send_email(message, smtp_host, smtp_port, smtp_username, smtp_password)

    storage.mark_sent(today)
    return f"sent:{len(normalized_recipients)}"