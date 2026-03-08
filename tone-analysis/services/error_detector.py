"""
Error Detector Engine for PSC Pronunciation Analysis
Detects and classifies pronunciation errors with detailed feedback.
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
class PronunciationError:
    """Detailed pronunciation error with feedback"""
    character: str
    position: int
    category: str  # initial_error, final_error, tone_error, etc.

    # Expected vs Actual
    expected_pinyin: str = ""
    expected_tone: int = 0
    expected_initial: str = ""
    expected_final: str = ""

    actual_pinyin: str = ""
    actual_tone: int = 0
    actual_initial: str = ""
    actual_final: str = ""

    # PSC Classification
    severity: str = "error"  # error, defect, minor_defect
    psc_impact: float = 0.1  # deduction in points

    # Detection
    detection_method: str = "character_mismatch"  # asr_mismatch, iflytek, tone_analyzer, ai_analysis
    confidence: float = 0.0

    # Feedback
    error_code: str = ""
    description_en: str = ""
    description_zh: str = ""
    fix_tip_en: str = ""
    fix_tip_zh: str = ""
    practice_words: List[str] = field(default_factory=list)


@dataclass
class CharacterResult:
    """Result for each character"""
    position: int
    character: str
    expected_pinyin: str
    actual_pinyin: str = ""
    expected_tone: int = 0
    actual_tone: int = 0
    expected_initial: str = ""
    actual_initial: str = ""
    expected_final: str = ""
    actual_final: str = ""
    status: str = "pending"  # pending, correct, error, defect
    errors: List[PronunciationError] = field(default_factory=list)


# ============================================================================
# ERROR DETECTOR CLASS
# ============================================================================

class ErrorDetector:
    """Detect and classify pronunciation errors"""

    def __init__(self):
        self.pinyin_db = pinyin_db

    def detect_errors(
        self,
        expected_text: str,
        transcription: str,
        iflytek_data: Dict = None,
        tone_analysis: Dict = None
    ) -> Dict[str, Any]:
        """
        Main method to detect errors from expected text and transcription.

        Args:
            expected_text: The text the user should have said
            transcription: What the user actually said (from ASR)
            iflytek_data: Optional detailed data from iFlytek
            tone_analysis: Optional tone analysis data

        Returns:
            Dictionary with character_results, errors, and summary
        """
        # Parse expected text
        expected_chars = list(expected_text.replace(" ", ""))
        actual_chars = list(transcription.replace(" ", ""))

        # Initialize results
        character_results: List[CharacterResult] = []
        all_errors: List[PronunciationError] = []

        # Perform character-level analysis
        for i, expected_char in enumerate(expected_chars):
            if not expected_char.strip():
                continue

            result = CharacterResult(
                position=i,
                character=expected_char,
                expected_pinyin="",
                status="pending"
            )

            # Get expected pinyin info
            expected_info = self.pinyin_db.get_char_info(expected_char)
            if expected_info:
                result.expected_pinyin = expected_info.get("pinyin", "")
                result.expected_tone = expected_info.get("tone", 0)
                result.expected_initial = expected_info.get("initial", "")
                result.expected_final = expected_info.get("final", "")

            # Find corresponding actual character
            # Try to match at the same position first
            actual_char = actual_chars[i] if i < len(actual_chars) else ""

            # If no match, try fuzzy matching (for insertions/deletions)
            if actual_char != expected_char:
                actual_char = self._find_matching_char(
                    expected_char, actual_chars, i
                )

            if actual_char:
                result.actual_pinyin = actual_char
                actual_info = self.pinyin_db.get_char_info(actual_char)
                if actual_info:
                    result.actual_tone = actual_info.get("tone", 0)
                    result.actual_initial = actual_info.get("initial", "")
                    result.actual_final = actual_info.get("final", "")
            else:
                actual_info = None

            # Detect errors for this character
            errors = self._detect_character_errors(
                result, expected_info, actual_info
            )

            if errors:
                result.errors = errors
                result.status = "error"
                all_errors.extend(errors)
            else:
                result.status = "correct"

            character_results.append(result)

        # Generate summary
        summary = self._generate_error_summary(all_errors)

        return {
            "character_results": character_results,
            "errors": all_errors,
            "summary": summary,
            "expected_text": expected_text,
            "transcription": transcription
        }

    def _find_matching_char(
        self,
        expected_char: str,
        actual_chars: List[str],
        position: int
    ) -> Optional[str]:
        """Find the best matching actual character for an expected character"""
        # Try nearby positions
        search_range = 3
        for offset in range(-search_range, search_range + 1):
            if offset == 0:
                continue
            idx = position + offset
            if 0 <= idx < len(actual_chars):
                if actual_chars[idx] == expected_char:
                    return actual_chars[idx]

        # If no match, return empty (omission)
        return ""

    def _detect_character_errors(
        self,
        result: CharacterResult,
        expected_info: Dict = None,
        actual_info: Dict = None
    ) -> List[PronunciationError]:
        """Detect errors for a single character"""
        errors = []

        if not expected_info:
            return errors

        expected_char = result.character

        # Case 1: Character not pronounced at all (omission)
        if not actual_info or result.actual_pinyin == "":
            error = PronunciationError(
                character=expected_char,
                position=result.position,
                category="omission",
                expected_pinyin=result.expected_pinyin,
                expected_tone=result.expected_tone,
                severity="error",
                psc_impact=0.1,
                detection_method="character_mismatch",
                confidence=1.0,
                error_code="OMISSION",
                description_en=f"Character '{expected_char}' was not pronounced",
                description_zh=f"字符'{expected_char}'未被朗读",
                fix_tip_en="Make sure to pronounce every character clearly",
                fix_tip_zh="确保清晰地朗读每个字符"
            )
            errors.append(error)
            return errors

        # Case 2: Completely different character
        if result.expected_pinyin and result.actual_pinyin:
            # Check for specific error patterns
            expected_initial = expected_info.get("initial", "")
            actual_initial = actual_info.get("initial", "") if actual_info else ""

            expected_final = expected_info.get("final", "")
            actual_final = actual_info.get("final", "") if actual_info else ""

            expected_tone = expected_info.get("tone", 0)
            actual_tone = actual_info.get("tone", 0) if actual_info else 0

            # Check initial error
            if expected_initial and actual_initial and expected_initial != actual_initial:
                error_info = self.pinyin_db.get_error_info(
                    expected_initial, actual_initial
                )
                if error_info:
                    error = PronunciationError(
                        character=expected_char,
                        position=result.position,
                        category=error_info.get("category", "initial_error"),
                        expected_pinyin=result.expected_pinyin,
                        expected_tone=expected_tone,
                        expected_initial=expected_initial,
                        expected_final=expected_final,
                        actual_pinyin=result.actual_pinyin,
                        actual_tone=actual_tone,
                        actual_initial=actual_initial,
                        actual_final=actual_final,
                        severity="error",
                        psc_impact=0.1,
                        detection_method="character_mismatch",
                        confidence=0.9,
                        error_code=error_info.get("error_code", "INIT_ERROR"),
                        description_en=error_info.get("description_en", ""),
                        description_zh=error_info.get("description_zh", ""),
                        fix_tip_en=error_info.get("fix_en", ""),
                        fix_tip_zh=error_info.get("fix_zh", ""),
                        practice_words=error_info.get("practice_words", [])
                    )
                    errors.append(error)

            # Check final error
            if not any(e.category == "initial_error" for e in errors):
                if expected_final and actual_final and expected_final != actual_final:
                    # Check if it's a nasal final confusion
                    error_info = self.pinyin_db.get_error_info(
                        expected_final, actual_final
                    )
                    if error_info:
                        error = PronunciationError(
                            character=expected_char,
                            position=result.position,
                            category=error_info.get("category", "final_error"),
                            expected_pinyin=result.expected_pinyin,
                            expected_tone=expected_tone,
                            expected_final=expected_final,
                            actual_pinyin=result.actual_pinyin,
                            actual_tone=actual_tone,
                            actual_final=actual_final,
                            severity="error",
                            psc_impact=0.1,
                            detection_method="character_mismatch",
                            confidence=0.9,
                            error_code=error_info.get("error_code", "FINAL_ERROR"),
                            description_en=error_info.get("description_en", ""),
                            description_zh=error_info.get("description_zh", ""),
                            fix_tip_en=error_info.get("fix_en", ""),
                            fix_tip_zh=error_info.get("fix_zh", ""),
                            practice_words=error_info.get("practice_words", [])
                        )
                        errors.append(error)

            # Check tone error (only if no other errors)
            if not errors:
                if expected_tone != actual_tone:
                    # Check if actual tone is neutral but shouldn't be
                    if actual_tone == 0 and expected_tone != 0:
                        error_info = self.pinyin_db.get_error_info(
                            "neutral_to_full"
                        )
                    # Check if expected tone is neutral but got full
                    elif expected_tone == 0 and actual_tone != 0:
                        error_info = self.pinyin_db.get_error_info(
                            "full_to_neutral"
                        )
                    else:
                        error_info = self.pinyin_db.get_error_info(
                            f"tone_{expected_tone}_to_{actual_tone}"
                        )

                    if error_info:
                        error = PronunciationError(
                            character=expected_char,
                            position=result.position,
                            category=error_info.get("category", "tone_error"),
                            expected_pinyin=result.expected_pinyin,
                            expected_tone=expected_tone,
                            expected_initial=expected_initial,
                            expected_final=expected_final,
                            actual_pinyin=result.actual_pinyin,
                            actual_tone=actual_tone,
                            actual_initial=actual_initial,
                            actual_final=actual_final,
                            severity="error",
                            psc_impact=0.1,
                            detection_method="character_mismatch",
                            confidence=0.85,
                            error_code=error_info.get("error_code", "TONE_ERROR"),
                            description_en=error_info.get("description_en", ""),
                            description_zh=error_info.get("description_zh", ""),
                            fix_tip_en=error_info.get("fix_en", ""),
                            fix_tip_zh=error_info.get("fix_zh", ""),
                            practice_words=error_info.get("practice_words", [])
                        )
                        errors.append(error)

        return errors

    def _generate_error_summary(
        self,
        errors: List[PronunciationError]
    ) -> Dict[str, Any]:
        """Generate error summary statistics"""
        summary = {
            "total_errors": len(errors),
            "total_defects": 0,
            "by_category": {},
            "by_severity": {},
            "by_initial": {},
            "by_final": {},
            "by_tone": {},
            "total_psc_impact": 0.0
        }

        for error in errors:
            # Count by category
            cat = error.category
            summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1

            # Count by severity
            sev = error.severity
            summary["by_severity"][sev] = summary["by_severity"].get(sev, 0) + 1
            if sev == "defect":
                summary["total_defects"] += 1

            # Count by initial (if initial error)
            if error.category == "initial_error":
                init = error.expected_initial
                summary["by_initial"][init] = summary["by_initial"].get(init, 0) + 1

            # Count by final (if final error)
            if error.category == "final_error":
                fin = error.expected_final
                summary["by_final"][fin] = summary["by_final"].get(fin, 0) + 1

            # Count by tone (if tone error)
            if error.category == "tone_error":
                tone_key = f"{error.expected_tone}→{error.actual_tone}"
                summary["by_tone"][tone_key] = summary["by_tone"].get(tone_key, 0) + 1

            # Total PSC impact
            summary["total_psc_impact"] += error.psc_impact

        return summary


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def detect_errors(
    expected_text: str,
    transcription: str,
    iflytek_data: Dict = None,
    tone_analysis: Dict = None
) -> Dict[str, Any]:
    """
    Convenience function to detect pronunciation errors.

    Args:
        expected_text: The text the user should have said
        transcription: What the user actually said
        iflytek_data: Optional detailed data from iFlytek
        tone_analysis: Optional tone analysis data

    Returns:
        Dictionary with character_results, errors, and summary
    """
    detector = ErrorDetector()
    return detector.detect_errors(
        expected_text=expected_text,
        transcription=transcription,
        iflytek_data=iflytek_data,
        tone_analysis=tone_analysis
    )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Test the error detector
    detector = ErrorDetector()

    # Test case 1: Simple tone error
    result = detector.detect_errors(
        expected_text="春天来了",
        transcription="春田来了"
    )

    print("=== Test Case 1 ===")
    print(f"Expected: 春天来了")
    print(f"Actual: 春田来了")
    print(f"\nCharacter Results:")
    for cr in result["character_results"]:
        print(f"  {cr.character}: expected={cr.expected_pinyin}(T{cr.expected_tone}), "
              f"actual={cr.actual_pinyin}(T{cr.actual_tone}), status={cr.status}")

    print(f"\nErrors Found: {len(result['errors'])}")
    for err in result["errors"]:
        print(f"  - {err.character}: {err.category}")
        print(f"    {err.description_en}")
        print(f"    Fix: {err.fix_tip_en}")
        print(f"    Practice: {err.practice_words}")

    print(f"\nSummary: {result['summary']}")
