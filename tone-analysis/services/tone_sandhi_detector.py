"""
Tone Sandhi (變調) Detector for PSC
Detects errors in tone sandhi rules:
- 一的變調 (yi tone changes: yī→yí/yì/yǐ)
- 不的變調 (bu tone changes: bù→bú)
- 三聲連讀變調 (third tone sandhi: 3+3→2+3)
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

from . import pinyin_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SandhiError:
    """Tone sandhi error details"""
    position: int
    character: str
    context: str  # The word or phrase containing the sandhi
    expected_tone: int  # The tone after sandhi application
    actual_tone: int   # The tone the user actually said
    sandhi_type: str   # "yi_sandhi", "bu_sandhi", "third_tone_sandhi"
    description_en: str = ""
    description_zh: str = ""
    severity: str = "error"  # error or defect


@dataclass
class NeutralToneError:
    """Neutral tone (輕聲) error details"""
    position: int
    character: str
    context: str
    expected_neutral: bool  # Should it be neutral?
    actual_neutral: bool    # Did user pronounce it as neutral?
    description_en: str = ""
    description_zh: str = ""
    severity: str = "error"


@dataclass
class ErhuaError:
    """Erhua (兒化韻) error details"""
    position: int
    character: str
    context: str
    expected_erhua: bool   # Should it have erhua?
    actual_erhua: bool     # Did user add/remove erhua?
    description_en: str = ""
    description_zh: str = ""
    severity: str = "error"


# ============================================================================
# TONE SANDHI DETECTOR
# ============================================================================

class ToneSandhiDetector:
    """Detect tone sandhi errors in Chinese pronunciation"""

    def __init__(self):
        self.pinyin_db = pinyin_db
        self.neutral_words = pinyin_db.NEUTRAL_TONE_WORDS
        # Define erhua patterns - words that commonly take 兒化
        self.erhua_patterns = self._init_erhua_patterns()

    def _init_erhua_patterns(self) -> Dict[str, str]:
        """Initialize common erhua patterns"""
        return {
            # Common nouns that take 兒化
            "花": "花兒", "鳥": "小鳥兒", "魚": "小魚兒",
            "孩": "小孩兒", "姐": "小姐兒", "叔": "小叔兒",
            "球": "球兒", "冊": "一本兒", "事": "事儿",
            "頭": "頭兒", "話": "話兒", "臉": "小臉兒",
            "門": "門兒", "湯": "湯兒", "糖": "糖兒",
            "盤": "盤兒", "碟": "碟兒", "杯": "杯兒",
            # Common erhua suffixes
            "玩": "玩兒", "唱": "唱兒", "跳": "跳兒",
            "說": "說兒", "笑": "笑兒", "鬧": "鬧兒",
        }

    def detect_sandhi_errors(
        self,
        expected_text: str,
        transcription: str,
        expected_pinyin_list: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Detect tone sandhi errors in the text.

        Args:
            expected_text: The text the user should have said
            transcription: What the user actually said (can be empty for detection)
            expected_pinyin_list: Optional list of expected pinyin for each character

        Returns:
            Dictionary with sandhi_errors, neutral_errors, erhua_errors, and summary
        """
        sandhi_errors: List[SandhiError] = []
        neutral_errors: List[NeutralToneError] = []
        erhua_errors: List[ErhuaError] = []

        # Get characters
        chars = list(expected_text.replace(" ", ""))

        # Check each character position for sandhi
        for i, char in enumerate(chars):
            # Check for 一不变调
            if char == "一":
                error = self._check_yi_sandhi(chars, i, expected_text)
                if error:
                    sandhi_errors.append(error)

            # Check for 不不变调
            elif char == "不":
                error = self._check_bu_sandhi(chars, i, expected_text)
                if error:
                    sandhi_errors.append(error)

            # Check for third tone sandhi (3+3 → 2+3)
            elif i > 0:
                error = self._check_third_tone_sandhi(chars, i, expected_text)
                if error:
                    sandhi_errors.append(error)

            # Check for neutral tone
            if char in self.neutral_words:
                error = self._check_neutral_tone(char, i, expected_text)
                if error:
                    neutral_errors.append(error)

            # Check for erhua
            if char in self.erhua_patterns:
                error = self._check_erhua(char, i, expected_text, transcription)
                if error:
                    erhua_errors.append(error)

        # Generate summary
        summary = {
            "total_sandhi_errors": len(sandhi_errors),
            "total_neutral_errors": len(neutral_errors),
            "total_erhua_errors": len(erhua_errors),
            "by_type": {
                "yi_sandhi": len([e for e in sandhi_errors if e.sandhi_type == "yi_sandhi"]),
                "bu_sandhi": len([e for e in sandhi_errors if e.sandhi_type == "bu_sandhi"]),
                "third_tone_sandhi": len([e for e in sandhi_errors if e.sandhi_type == "third_tone_sandhi"]),
            }
        }

        return {
            "sandhi_errors": sandhi_errors,
            "neutral_errors": neutral_errors,
            "erhua_errors": erhua_errors,
            "summary": summary,
            "expected_text": expected_text,
            "transcription": transcription
        }

    def _check_yi_sandhi(
        self,
        chars: List[str],
        position: int,
        context: str
    ) -> Optional[SandhiError]:
        """Check 一不变调 (yi tone changes)"""
        if position >= len(chars) - 1:
            return None

        next_char = chars[position + 1]
        next_info = self.pinyin_db.get_char_info(next_char)

        if not next_info:
            return None

        next_tone = next_info.get("tone", 0)

        # 一 in first tone (yī) followed by any tone becomes the 4th tone (yì)
        # except when followed by another first tone (yī + yī = yī yì)
        # Actually in modern Mandarin:
        # - yī + yī/yí/yǔ → yì (4th tone)
        # - yī + è(yì) → yì (4th tone)

        if next_tone == 1:
            expected_tone = 4  # yī + yī → yì
        elif next_tone == 2:
            expected_tone = 2  # yī + é → yí (2nd tone)
        elif next_tone == 3:
            expected_tone = 3  # yī + ě → yǐ (3rd tone)
        elif next_tone == 4:
            expected_tone = 4  # yī + è → yì (4th tone)
        else:
            return None

        # For now, we can't know what the user actually said without audio
        # This would need to be filled in by the ASR/transcription
        # We'll mark this as a potential issue that needs verification

        return SandhiError(
            position=position,
            character="一",
            context=context[max(0, position-2):position+3],
            expected_tone=expected_tone,
            actual_tone=1,  # Would need to be filled from ASR
            sandhi_type="yi_sandhi",
            description_en=f"'一' should be tone {expected_tone} when followed by tone {next_tone}",
            description_zh=f"'一'在{self._tone_name(next_tone)}前應讀{self._tone_name(expected_tone)}聲",
            severity="error"
        )

    def _check_bu_sandhi(
        self,
        chars: List[str],
        position: int,
        context: str
    ) -> Optional[SandhiError]:
        """Check 不不变调 (bu tone changes)"""
        if position >= len(chars) - 1:
            return None

        next_char = chars[position + 1]
        next_info = self.pinyin_db.get_char_info(next_char)

        if not next_info:
            return None

        next_tone = next_info.get("tone", 0)

        # 不 (bù) before 4th tone (è) stays as bù
        # 不 (bù) before 1st/2nd/3rd tone becomes bú (2nd tone)

        if next_tone == 4:
            expected_tone = 4  # bù + è → bù
        elif next_tone in [1, 2, 3]:
            expected_tone = 2  # bù + any other tone → bú
        else:
            return None

        return SandhiError(
            position=position,
            character="不",
            context=context[max(0, position-2):position+3],
            expected_tone=expected_tone,
            actual_tone=4,  # Would need to be filled from ASR
            sandhi_type="bu_sandhi",
            description_en=f"'不' should be tone {expected_tone} when followed by tone {next_tone}",
            description_zh=f"'不'在{self._tone_name(next_tone)}前應讀{self._tone_name(expected_tone)}聲",
            severity="error"
        )

    def _check_third_tone_sandhi(
        self,
        chars: List[str],
        position: int,
        context: str
    ) -> Optional[SandhiError]:
        """Check 第三声连读 (third tone sandhi: 3+3→2+3)"""
        if position == 0:
            return None

        prev_char = chars[position - 1]
        current_char = chars[position]

        prev_info = self.pinyin_db.get_char_info(prev_char)
        curr_info = self.pinyin_db.get_char_info(current_char)

        if not prev_info or not curr_info:
            return None

        prev_tone = prev_info.get("tone", 0)
        curr_tone = curr_info.get("tone", 0)

        # Third tone sandhi: 3+3 → 2+3
        # When two 3rd tone characters are adjacent, the first becomes 2nd tone
        if prev_tone == 3 and curr_tone == 3:
            return SandhiError(
                position=position - 1,
                character=prev_char,
                context=context[max(0, position-3):position+2],
                expected_tone=2,  # Should be 2nd tone
                actual_tone=3,    # User might have said 3rd tone
                sandhi_type="third_tone_sandhi",
                description_en=f"Third tone '{prev_char}' before another third tone should be second tone",
                description_zh=f"兩個第三聲相連，前一個應讀第二聲",
                severity="error"
            )

        return None

    def _check_neutral_tone(
        self,
        char: str,
        position: int,
        context: str
    ) -> Optional[NeutralToneError]:
        """Check if a neutral tone word is pronounced correctly"""
        # This would need ASR data to know if user said it correctly
        # For now, we just identify potential neutral tone words
        return NeutralToneError(
            position=position,
            character=char,
            context=context[max(0, position-2):position+3],
            expected_neutral=True,
            actual_neutral=False,  # Would need to be filled from ASR
            description_en=f"'{char}' is typically pronounced as neutral tone",
            description_zh=f"'{char}'通常讀輕聲",
            severity="error"
        )

    def _check_erhua(
        self,
        char: str,
        position: int,
        expected_context: str,
        actual_transcription: str
    ) -> Optional[ErhuaError]:
        """Check erhua (兒化) usage"""
        # Check if the word in expected text has erhua
        expected_has_erhua = "兒" in expected_context[max(0, position-1):position+2] or "儿" in expected_context[max(0, position-1):position+2]

        # Check if user added or removed erhua
        actual_has_erhua = False
        if actual_transcription:
            actual_has_erhua = "兒" in actual_transcription or "儿" in actual_transcription

        # Only flag if there's a mismatch
        if expected_has_erhua != actual_has_erhua:
            return ErhuaError(
                position=position,
                character=char,
                context=expected_context[max(0, position-2):position+3],
                expected_erhua=expected_has_erhua,
                actual_erhua=actual_has_erhua,
                description_en=f"Erhua mismatch: expected {'with' if expected_has_erhua else 'without'} 兒化",
                description_zh=f"兒化韻{'應有' if expected_has_erhua else '不應有'}兒化",
                severity="error"
            )

        return None

    def _tone_name(self, tone: int) -> str:
        """Convert tone number to Chinese tone name"""
        tone_names = {
            1: "一聲",
            2: "二聲",
            3: "三聲",
            4: "四聲",
            0: "輕聲"
        }
        return tone_names.get(tone, f"第{tone}聲")


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def detect_sandhi_errors(
    expected_text: str,
    transcription: str = "",
    expected_pinyin_list: List[Dict] = None
) -> Dict[str, Any]:
    """
    Convenience function to detect tone sandhi errors.

    Args:
        expected_text: The text the user should have said
        transcription: What the user actually said
        expected_pinyin_list: Optional list of expected pinyin for each character

    Returns:
        Dictionary with sandhi detection results
    """
    detector = ToneSandhiDetector()
    return detector.detect_sandhi_errors(
        expected_text=expected_text,
        transcription=transcription,
        expected_pinyin_list=expected_pinyin_list
    )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test the tone sandhi detector
    detector = ToneSandhiDetector()

    # Test cases
    test_cases = [
        "一起",      # 一 + 一声 → should be yì (4th tone)
        "不一樣",    # 不 + 四声 → should stay bù
        "不好",      # 不 + 三声 → should be bú
        "你好",      # Third tone + Third tone → first should be 2nd tone
        "水果",      # Third tone + Third tone → first should be 2nd tone
    ]

    print("=== Tone Sandhi Detection Test ===\n")

    for text in test_cases:
        result = detector.detect_sandhi_errors(text, "")
        print(f"Text: {text}")
        print(f"Sandhi errors found: {result['summary']['total_sandhi_errors']}")
        for error in result['sandhi_errors']:
            print(f"  - {error.character}: {error.description_en}")
        print()
