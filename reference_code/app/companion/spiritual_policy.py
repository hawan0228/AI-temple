from __future__ import annotations

from app.companion.enums import SpiritualIntensity


class SpiritualPolicy:
    _SPIRITUAL_HINTS = (
        "神明",
        "祈福",
        "命運",
        "拜拜",
        "參拜",
        "求神",
        "信仰",
        "保佑",
    )
    _PROHIBITED_PHRASES = (
        "神明告訴我",
        "神明現在對你說",
        "神明一定會幫你",
        "這是神明給你的考驗",
        "這是你的業報",
        "你不夠虔誠",
        "不照做會有壞事",
        "你命中注定",
        "這件事一定會成功",
        "只要祈福就會改變結果",
    )

    def intensity_limit_for_text(
        self,
        text: str,
        *,
        repair_mode: bool = False,
    ) -> SpiritualIntensity:
        if repair_mode:
            return SpiritualIntensity.LEVEL_0_NEUTRAL
        if any(token in text for token in self._SPIRITUAL_HINTS):
            return SpiritualIntensity.LEVEL_2_SPIRITUAL_MEANING
        return SpiritualIntensity.LEVEL_1_COURTYARD

    def contains_prohibited_spiritual_phrase(self, text: str) -> bool:
        return any(phrase in text for phrase in self._PROHIBITED_PHRASES)
