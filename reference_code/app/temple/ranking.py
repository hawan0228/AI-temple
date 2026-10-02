from __future__ import annotations

from dataclasses import dataclass

from app.temple.distance import haversine_km
from app.temple.enums import TempleSearchMode, TempleTheme
from app.temple.schemas import TempleRecordV1, TempleResultSet, TempleSearchResult


def _quality_bonus(temple: TempleRecordV1) -> float:
    bonus = 0.0
    if temple.quality.details_status == "DETAILS_REVIEWED":
        bonus += 1.5
    if temple.quality.coordinate_status == "COORDINATES_VERIFIED":
        bonus += 1.0
    if temple.quality.theme_status == "THEMES_REVIEWED":
        bonus += 1.0
    return bonus


@dataclass(frozen=True)
class TempleRankingService:
    max_results: int = 3

    def rank_region(
        self,
        temples: list[TempleRecordV1],
        *,
        county: str,
        district: str | None = None,
    ) -> TempleResultSet:
        ranked: list[TempleSearchResult] = []
        for temple in temples:
            score = 10.0 + _quality_bonus(temple)
            reasons = [f"位於{county}"]
            if district and temple.location.district == district:
                score += 2.0
                reasons.append(f"位於{district}")
            flags = [temple.quality.details_status]
            ranked.append(
                TempleSearchResult(
                    temple_id=temple.temple_id,
                    score=score,
                    match_reasons=reasons,
                    quality_flags=flags,
                    temple=temple,
                )
            )
        ranked.sort(key=lambda item: (-item.score, item.temple.name.normalized, item.temple_id))
        return TempleResultSet(
            results=ranked[: self.max_results],
            total_candidates=len(ranked),
            search_mode=TempleSearchMode.REGION,
        )

    def rank_theme(
        self,
        temples: list[TempleRecordV1],
        *,
        theme: TempleTheme,
    ) -> TempleResultSet:
        ranked: list[TempleSearchResult] = []
        for temple in temples:
            score = 12.0 + _quality_bonus(temple)
            reasons = [f"符合已審核的{_theme_label(theme)}參拜方向"]
            if temple.location.county:
                reasons.append(f"位於{temple.location.county}")
            ranked.append(
                TempleSearchResult(
                    temple_id=temple.temple_id,
                    score=score,
                    match_reasons=reasons,
                    quality_flags=[temple.quality.theme_status],
                    temple=temple,
                )
            )
        ranked.sort(key=lambda item: (-item.score, item.temple.name.normalized, item.temple_id))
        return TempleResultSet(
            results=ranked[: self.max_results],
            total_candidates=len(ranked),
            search_mode=TempleSearchMode.THEME,
        )

    def rank_deity(
        self,
        temples: list[TempleRecordV1],
        *,
        deity: str,
    ) -> TempleResultSet:
        ranked: list[TempleSearchResult] = []
        for temple in temples:
            score = 11.0 + _quality_bonus(temple)
            ranked.append(
                TempleSearchResult(
                    temple_id=temple.temple_id,
                    score=score,
                    match_reasons=[f"資料顯示主祀或相關神祇符合 {deity}"],
                    quality_flags=[temple.quality.identity_status],
                    temple=temple,
                )
            )
        ranked.sort(key=lambda item: (-item.score, item.temple.name.normalized, item.temple_id))
        return TempleResultSet(
            results=ranked[: self.max_results],
            total_candidates=len(ranked),
            search_mode=TempleSearchMode.DEITY,
        )

    def rank_nearby(
        self,
        temples: list[TempleRecordV1],
        *,
        latitude: float,
        longitude: float,
    ) -> TempleResultSet:
        ranked: list[TempleSearchResult] = []
        for temple in temples:
            coords = temple.location.coordinates
            if (
                coords.status != "COORDINATES_VERIFIED"
                or coords.latitude is None
                or coords.longitude is None
            ):
                continue
            distance = haversine_km(latitude, longitude, coords.latitude, coords.longitude)
            reasons = [f"依目前位置與已驗證座標，距離約 {distance:.1f} 公里"]
            if temple.location.county:
                reasons.append(f"位於{temple.location.county}{temple.location.district}")
            score = 20.0 - min(distance, 20.0) + _quality_bonus(temple)
            ranked.append(
                TempleSearchResult(
                    temple_id=temple.temple_id,
                    score=score,
                    distance_km=distance,
                    match_reasons=reasons,
                    quality_flags=[coords.status],
                    temple=temple,
                )
            )
        ranked.sort(
            key=lambda item: (
                item.distance_km if item.distance_km is not None else float("inf"),
                -item.score,
                item.temple.name.normalized,
                item.temple_id,
            )
        )
        return TempleResultSet(
            results=ranked[: self.max_results],
            total_candidates=len(ranked),
            search_mode=TempleSearchMode.NEARBY,
        )


def _theme_label(theme: TempleTheme) -> str:
    return {
        TempleTheme.GENERAL_PEACE: "平安",
        TempleTheme.ACADEMIC: "學業",
        TempleTheme.CAREER: "工作",
        TempleTheme.FAMILY: "家庭",
        TempleTheme.RELATIONSHIP: "感情",
        TempleTheme.HEALTH_WELLBEING: "健康與身心安定",
        TempleTheme.SAFE_TRAVEL: "平安出行",
        TempleTheme.PROSPERITY: "順遂與財運",
        TempleTheme.GRATITUDE: "感謝",
        TempleTheme.OTHER: "其他",
    }[theme]

