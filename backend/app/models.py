from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class DailyProblem:
    title: str
    slug: str
    url: str
    difficulty: str
    description: str
    fetched_at: datetime
    acceptance_rate: float | None = None
    topic_tags: list[str] | None = None


@dataclass
class DeliveryRecord:
    sent_date: str
    sent_at: datetime