from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass(frozen=True)
class TemplePrivacyPolicy:
    session_ttl_seconds: int
    location_ttl_seconds: int

    def build_base_metadata(self, *, now: datetime | None = None) -> dict[str, object]:
        current = now or datetime.now(timezone.utc)
        return {
            "search_mode": None,
            "region": None,
            "district": None,
            "theme": None,
            "deity": None,
            "location_ref": None,
            "last_result_ids": [],
            "started_at": current.isoformat(),
            "expires_at": (current + timedelta(seconds=self.session_ttl_seconds)).isoformat(),
            "no_history": True,
            "last_location_message_id_hash": None,
        }

    def location_ttl(self) -> int:
        return self.location_ttl_seconds

