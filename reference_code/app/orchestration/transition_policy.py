from __future__ import annotations

from app.companion.enums import RiskCategory, RiskLevel
from app.orchestration.enums import (
    CrossFeatureContextPolicy,
    FeatureId,
    HandoffInitiator,
    HandoffReason,
)
from app.orchestration.schemas import TransitionDecision


class CrossFeatureTransitionPolicy:
    _RITUAL_AND_SEARCH_FEATURES = {
        FeatureId.DIVINATION,
        FeatureId.PRAYER,
        FeatureId.TEMPLE,
    }
    _MAJOR_DECISION_CATEGORIES = {
        RiskCategory.MEDICAL_DECISION,
        RiskCategory.LEGAL_DECISION,
        RiskCategory.MAJOR_FINANCIAL_DECISION,
    }

    def decide(
        self,
        *,
        source_feature: FeatureId | None,
        target_feature: FeatureId | None,
        reason: HandoffReason,
        initiated_by: HandoffInitiator,
        explicit_user_action: bool,
        risk_level: RiskLevel = RiskLevel.LOW,
        risk_categories: set[RiskCategory] | None = None,
    ) -> TransitionDecision:
        if source_feature is None or target_feature is None:
            return TransitionDecision(
                allowed=False,
                reason_code="unknown_feature",
            )

        categories = risk_categories or set()
        if target_feature in self._RITUAL_AND_SEARCH_FEATURES and (
            risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}
            or categories & self._MAJOR_DECISION_CATEGORIES
            or reason == HandoffReason.SAFETY_ROUTING
            or initiated_by == HandoffInitiator.SAFETY
        ):
            return TransitionDecision(
                allowed=False,
                context_policy=CrossFeatureContextPolicy.DENY,
                safety_override=True,
                reason_code="safety_override",
            )

        if source_feature == target_feature:
            if initiated_by == HandoffInitiator.USER and explicit_user_action:
                return TransitionDecision(
                    allowed=True,
                    context_policy=CrossFeatureContextPolicy.ALLOW_NONE,
                    reason_code="restart_feature",
                )
            return TransitionDecision(
                allowed=False,
                reason_code="requires_explicit_user_action",
            )

        if source_feature == FeatureId.HOME or target_feature == FeatureId.HOME:
            return TransitionDecision(
                allowed=True,
                requires_explicit_user_action=target_feature != FeatureId.HOME,
                context_policy=CrossFeatureContextPolicy.ALLOW_NONE,
                reason_code="home_transition",
            )

        if initiated_by == HandoffInitiator.USER and reason == HandoffReason.USER_SELECTED:
            bounded_pair = {
                source_feature,
                target_feature,
            } == {FeatureId.COMPANION, FeatureId.DIVINATION}
            return TransitionDecision(
                allowed=explicit_user_action,
                context_policy=(
                    CrossFeatureContextPolicy.BOUNDED_SESSION_BRIDGE
                    if bounded_pair
                    else CrossFeatureContextPolicy.ALLOW_NONE
                ),
                reason_code=(
                    "user_selected_feature_switch"
                    if explicit_user_action
                    else "requires_explicit_user_action"
                ),
            )

        if (
            source_feature in {FeatureId.PRAYER, FeatureId.DIVINATION, FeatureId.TEMPLE}
            and target_feature == FeatureId.COMPANION
            and explicit_user_action
            and reason in {HandoffReason.USER_SELECTED, HandoffReason.FEATURE_SUGGESTION}
        ):
            return TransitionDecision(
                allowed=True,
                context_policy=(
                    CrossFeatureContextPolicy.BOUNDED_SESSION_BRIDGE
                    if source_feature == FeatureId.DIVINATION
                    else CrossFeatureContextPolicy.ALLOW_NONE
                ),
                reason_code="support_companion_handoff",
            )

        if (
            source_feature == FeatureId.COMPANION
            and target_feature in self._RITUAL_AND_SEARCH_FEATURES
            and explicit_user_action
            and reason
            in {
                HandoffReason.USER_SELECTED,
                HandoffReason.USER_EXPLICIT_INTENT,
                HandoffReason.FEATURE_SUGGESTION,
            }
        ):
            return TransitionDecision(
                allowed=True,
                context_policy=(
                    CrossFeatureContextPolicy.BOUNDED_SESSION_BRIDGE
                    if target_feature == FeatureId.DIVINATION
                    else CrossFeatureContextPolicy.ALLOW_NONE
                ),
                reason_code="companion_explicit_handoff",
            )

        return TransitionDecision(
            allowed=False,
            context_policy=CrossFeatureContextPolicy.DENY,
            reason_code="transition_not_allowed",
        )
