from __future__ import annotations

from datetime import datetime

from supabase import Client, create_client

from .models import DailyProblem


class Storage:
    def __init__(self, supabase_url: str, supabase_key: str) -> None:
        self.client: Client | None = None
        if supabase_url and supabase_key:
            self.client = create_client(supabase_url, supabase_key)

    def _table(self, name: str):
        if self.client is None:
            raise RuntimeError("Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY.")
        return self.client.table(name)

    def save_daily_problem(self, problem: DailyProblem) -> None:
        payload = {
            "id": 1,
            "title": problem.title,
            "slug": problem.slug,
            "url": problem.url,
            "difficulty": problem.difficulty,
            "description": problem.description,
            "fetched_at": problem.fetched_at.isoformat(),
            "acceptance_rate": problem.acceptance_rate,
            "topic_tags": problem.topic_tags or [],
        }
        try:
            # Preferred path when the daily_problem table includes all optional columns.
            self._table("daily_problem").upsert(payload, on_conflict="id").execute()
        except Exception:
            try:
                # Backward compatibility for schemas missing topic_tags.
                legacy_payload = dict(payload)
                legacy_payload.pop("topic_tags", None)
                self._table("daily_problem").upsert(legacy_payload, on_conflict="id").execute()
            except Exception:
                # Backward compatibility for schemas missing both topic_tags and acceptance_rate.
                legacy_payload = dict(payload)
                legacy_payload.pop("topic_tags", None)
                legacy_payload.pop("acceptance_rate", None)
                self._table("daily_problem").upsert(legacy_payload, on_conflict="id").execute()

    def load_daily_problem(self) -> DailyProblem | None:
        try:
            response = (
                self._table("daily_problem")
                .select("title, slug, url, difficulty, description, fetched_at, acceptance_rate, topic_tags")
                .eq("id", 1)
                .limit(1)
                .execute()
            )
        except Exception:
            try:
                # Backward compatibility for schemas missing topic_tags.
                response = (
                    self._table("daily_problem")
                    .select("title, slug, url, difficulty, description, fetched_at, acceptance_rate")
                    .eq("id", 1)
                    .limit(1)
                    .execute()
                )
            except Exception:
                # Backward compatibility for schemas missing both topic_tags and acceptance_rate.
                response = (
                    self._table("daily_problem")
                    .select("title, slug, url, difficulty, description, fetched_at")
                    .eq("id", 1)
                    .limit(1)
                    .execute()
                )

        if not response.data:
            return None

        row = response.data[0]
        raw_tags = row.get("topic_tags")
        if isinstance(raw_tags, list):
            topic_tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
        else:
            topic_tags = []

        return DailyProblem(
            title=row["title"],
            slug=row["slug"],
            url=row["url"],
            difficulty=row["difficulty"],
            description=row["description"],
            fetched_at=datetime.fromisoformat(row["fetched_at"]),
            acceptance_rate=row.get("acceptance_rate"),
            topic_tags=topic_tags,
        )

    def mark_sent(self, sent_date: str) -> None:
        payload = {
            "sent_date": sent_date,
            "sent_at": datetime.utcnow().isoformat(),
        }
        self._table("delivery_log").upsert(payload, on_conflict="sent_date").execute()

    def was_sent(self, sent_date: str) -> bool:
        response = (
            self._table("delivery_log")
            .select("sent_date")
            .eq("sent_date", sent_date)
            .limit(1)
            .execute()
        )
        return bool(response.data)

    def add_recipient(self, email: str) -> bool:
        normalized = email.strip().lower()
        existing = (
            self._table("recipients")
            .select("email")
            .eq("email", normalized)
            .limit(1)
            .execute()
        )
        if existing.data:
            return False
        self._table("recipients").insert({"email": normalized}).execute()
        return True

    def list_recipients(self) -> list[str]:
        response = self._table("recipients").select("email").order("email").execute()
        return [row["email"] for row in response.data or []]
