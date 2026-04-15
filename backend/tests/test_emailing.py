from datetime import datetime, timezone

from app.emailing import build_email
from app.models import DailyProblem


def test_build_email_contains_link_and_description():
    problem = DailyProblem(
        title="Two Sum",
        slug="two-sum",
        url="https://leetcode.com/problems/two-sum/",
        difficulty="Easy",
        description="Find two numbers that add up to target.\n\n- Use a map\n- Return indices",
        fetched_at=datetime.now(timezone.utc),
    )
    message = build_email(problem, "sender@example.com", "recipient@example.com")

    assert "Two Sum" in message["Subject"]
    serialized = message.as_string()
    assert "https://leetcode.com/problems/two-sum/" in serialized
    assert "Difficulty: Easy" in serialized
    assert "Description Preview" in serialized
    assert "Use a map" in serialized
    assert "<br />" in serialized