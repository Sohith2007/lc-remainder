from datetime import datetime, timezone
import asyncio

from app import scheduler as scheduler_module
from app.models import DailyProblem


class FakeStorage:
    def __init__(self):
        self.problems = []
        self.sent_dates = set()
        self.mark_calls = []

    def save_daily_problem(self, problem):
        self.problems.append(problem)

    def was_sent(self, sent_date):
        return sent_date in self.sent_dates

    def mark_sent(self, sent_date):
        self.sent_dates.add(sent_date)
        self.mark_calls.append(sent_date)

    def list_recipients(self):
        return ["recipient@example.com"]

def test_refresh_and_send_skips_duplicate_email(monkeypatch):
    problem = DailyProblem(
        title="Two Sum",
        slug="two-sum",
        url="https://leetcode.com/problems/two-sum/",
        difficulty="Easy",
        description="Find two numbers that add up to target.",
        fetched_at=datetime.now(timezone.utc),
    )
    storage = FakeStorage()
    send_calls = []

    async def fake_fetch_daily_problem(source_url):
        return problem

    def fake_send_email(message, host, port, username, password):
        send_calls.append(message)

    monkeypatch.setattr(scheduler_module, "fetch_daily_problem", fake_fetch_daily_problem)
    monkeypatch.setattr(scheduler_module, "send_email", fake_send_email)

    async def run_once():
        first = await scheduler_module.refresh_and_send(
            storage=storage,
            source_url="https://leetcode.com/problemset/all/",
            sender="sender@example.com",
            recipients=["recipient@example.com", "recipient@example.com"],
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_username="sender@example.com",
            smtp_password="secret",
        )
        second = await scheduler_module.refresh_and_send(
            storage=storage,
            source_url="https://leetcode.com/problemset/all/",
            sender="sender@example.com",
            recipients=["recipient@example.com"],
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_username="sender@example.com",
            smtp_password="secret",
        )
        return first, second

    first, second = asyncio.run(run_once())

    assert first == "sent:1"
    assert second == "already-sent"
    assert len(send_calls) == 1
    assert len(storage.mark_calls) == 1


def test_refresh_and_send_requires_recipients(monkeypatch):
    problem = DailyProblem(
        title="Two Sum",
        slug="two-sum",
        url="https://leetcode.com/problems/two-sum/",
        difficulty="Easy",
        description="Find two numbers that add up to target.",
        fetched_at=datetime.now(timezone.utc),
    )
    storage = FakeStorage()

    async def fake_fetch_daily_problem(source_url):
        return problem

    monkeypatch.setattr(scheduler_module, "fetch_daily_problem", fake_fetch_daily_problem)

    result = asyncio.run(
        scheduler_module.refresh_and_send(
            storage=storage,
            source_url="https://leetcode.com/problemset/all/",
            sender="sender@example.com",
            recipients=[],
            smtp_host="smtp.gmail.com",
            smtp_port=587,
            smtp_username="sender@example.com",
            smtp_password="secret",
        )
    )

    assert result == "no-recipients"