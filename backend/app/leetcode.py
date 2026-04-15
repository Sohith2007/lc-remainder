from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import re

import httpx

from .models import DailyProblem


DAILY_CHALLENGE_QUERY = """
query activeDailyCodingChallengeQuestion {
    activeDailyCodingChallengeQuestion {
        date
        link
        question {
            title
            titleSlug
            content
            difficulty
            acRate
            topicTags {
                name
            }
        }
    }
}
"""

DAILY_LINK_PATTERN = re.compile(
        r"https://leetcode\.com/problems/(?P<slug>[a-z0-9-]+)/?",
        re.IGNORECASE,
)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


class LeetCodeFetchError(RuntimeError):
    pass


async def fetch_daily_problem(source_url: str) -> DailyProblem:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            "https://leetcode.com/graphql",
            json={"query": DAILY_CHALLENGE_QUERY},
            headers={"content-type": "application/json", "referer": source_url},
        )
        response.raise_for_status()

    payload = response.json()
    challenge = payload.get("data", {}).get("activeDailyCodingChallengeQuestion")
    if not challenge:
        raise LeetCodeFetchError("Could not load the active daily challenge from LeetCode.")

    question = challenge.get("question") or {}
    title = question.get("title")
    slug = question.get("titleSlug")
    content = question.get("content") or ""
    difficulty = question.get("difficulty") or "Unknown"
    ac_rate = question.get("acRate")
    raw_topic_tags = question.get("topicTags") or []
    
    # Convert acceptance rate to float (it's a percentage string like "42.8")
    acceptance_rate: float | None = None
    if ac_rate is not None:
        try:
            acceptance_rate = float(ac_rate)
        except (ValueError, TypeError):
            acceptance_rate = None

    topic_tags = [
        str(tag.get("name", "")).strip()
        for tag in raw_topic_tags
        if isinstance(tag, dict) and str(tag.get("name", "")).strip()
    ]
    
    if not title or not slug:
        raise LeetCodeFetchError("LeetCode returned an incomplete daily challenge payload.")

    problem_url = f"https://leetcode.com/problems/{slug}/"
    description = html_to_text(content)
    if not description:
        description = "Open the problem link to view the current LeetCode daily challenge description."

    return DailyProblem(
        title=title,
        slug=slug,
        url=problem_url,
        difficulty=difficulty,
        description=description,
        fetched_at=datetime.now(timezone.utc),
        acceptance_rate=acceptance_rate,
        topic_tags=topic_tags,
    )


def html_to_text(value: str) -> str:
    text = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", value)
    text = re.sub(r"(?i)</\s*(p|div|h1|h2|h3|h4|h5|h6|pre|ul|ol)\s*>", "\n\n", text)
    text = re.sub(r"(?i)<\s*li[^>]*>", "\n- ", text)
    text = re.sub(r"(?i)</\s*li\s*>", "", text)
    text = unescape(HTML_TAG_PATTERN.sub("", text)).replace("\xa0", " ")

    normalized_lines = []
    for raw_line in text.splitlines():
        line = WHITESPACE_PATTERN.sub(" ", raw_line).strip()
        normalized_lines.append(line)

    compact_lines = []
    previous_blank = True
    for line in normalized_lines:
        if not line:
            if not previous_blank:
                compact_lines.append("")
            previous_blank = True
            continue
        compact_lines.append(line)
        previous_blank = False

    return "\n".join(compact_lines).strip()