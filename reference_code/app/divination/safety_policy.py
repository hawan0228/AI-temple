from __future__ import annotations

from app.companion.enums import RiskCategory, RiskLevel
from app.companion.safety import DeterministicSafetyPrecheck, SafetyPrecheck
from app.divination.schemas import DivinationGuardDecision


class DivinationSafetyPolicy:
    _MAJOR_DECISION_CATEGORIES = {
        RiskCategory.MEDICAL_DECISION,
        RiskCategory.LEGAL_DECISION,
        RiskCategory.MAJOR_FINANCIAL_DECISION,
    }
    _EXPLICIT_MAJOR_DECISION_PATTERNS = (
        "停藥",
        "手術",
        "報警",
        "提告",
        "投資全部",
        "借高額貸款",
        "借大筆錢",
    )

    def __init__(self, precheck: SafetyPrecheck | None = None) -> None:
        self._precheck = precheck or DeterministicSafetyPrecheck()

    def evaluate(self, text: str) -> DivinationGuardDecision:
        normalized = text.strip()
        if any(pattern in normalized for pattern in self._EXPLICIT_MAJOR_DECISION_PATTERNS):
            return DivinationGuardDecision(
                allowed=False,
                reason_code="major_decision",
                messages=[
                    "這件事牽涉到重要的安全或專業判斷，不適合交給一支籤替你決定。",
                    "你可以先把最在意的部分說清楚，再找合適的專業或可信任的人一起判斷。",
                ],
            )
        assessment = self._precheck.evaluate(text)
        if assessment.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            return DivinationGuardDecision(
                allowed=False,
                reason_code="high_risk",
                messages=[
                    "這件事現在比較需要先顧到安全，並不適合交給一支籤替你承擔。",
                    "如果你覺得自己或別人可能有立即危險，請優先聯絡當地緊急服務，或找身邊可信任的人陪你。",
                ],
            )
        if any(category in self._MAJOR_DECISION_CATEGORIES for category in assessment.categories):
            return DivinationGuardDecision(
                allowed=False,
                reason_code="major_decision",
                messages=[
                    "這件事牽涉到重要的安全或專業判斷，不適合交給一支籤替你決定。",
                    "你可以先把最在意的部分說清楚，再找合適的專業或可信任的人一起判斷。",
                ],
            )
        return DivinationGuardDecision(allowed=True)
