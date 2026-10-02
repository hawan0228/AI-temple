from __future__ import annotations

from datetime import datetime, timedelta


class PrayerPrivacyPolicy:
    def __init__(
        self,
        *,
        session_ttl_seconds: int,
        intention_ttl_seconds: int,
    ) -> None:
        self._session_ttl_seconds = session_ttl_seconds
        self._intention_ttl_seconds = intention_ttl_seconds

    @property
    def no_history_default(self) -> bool:
        return True

    def build_base_metadata(
        self,
        *,
        ritual_profile_id: str,
        now: datetime,
        session_start_markers: list[str],
    ) -> dict[str, object]:
        return {
            "ritual_profile_id": ritual_profile_id,
            "target": None,
            "intention_mode": None,
            "intention_ref": None,
            "started_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=self._session_ttl_seconds)).isoformat(),
            "ritual_completed_at": None,
            "session_window_started_at": (
                now - timedelta(seconds=self._session_ttl_seconds)
            ).isoformat(),
            "session_start_markers": session_start_markers,
            "last_intention_message_id_hash": None,
            "no_history": True,
            "clear_requested": False,
        }

    def intention_ttl_seconds(self) -> int:
        return max(1, min(self._intention_ttl_seconds, self._session_ttl_seconds))
