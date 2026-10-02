from __future__ import annotations

from app.divination.enums import ConfirmationFailureBehavior, PermissionOutcome
from app.divination.schemas import RitualLotConfirmationRules, RitualPermissionRules, RitualProfile


REFERENCE_TRIPLE_CONFIRM_V1 = RitualProfile(
    profile_id="reference_triple_confirm_v1",
    one_question_per_session=True,
    permission_jiaobei_required=True,
    permission=RitualPermissionRules(
        sheng=PermissionOutcome.PROCEED,
        xiao=PermissionOutcome.RETRY,
        yin=PermissionOutcome.STOP,
    ),
    lot_confirmation=RitualLotConfirmationRules(
        required_consecutive_sheng=3,
        xiao_behavior=ConfirmationFailureBehavior.REDRAW,
        yin_behavior=ConfirmationFailureBehavior.REDRAW,
    ),
)

RITUAL_PROFILES = {
    REFERENCE_TRIPLE_CONFIRM_V1.profile_id: REFERENCE_TRIPLE_CONFIRM_V1,
}


def get_ritual_profile(profile_id: str) -> RitualProfile:
    try:
        return RITUAL_PROFILES[profile_id]
    except KeyError as exc:
        raise ValueError(f"Unsupported ritual profile: {profile_id}") from exc
