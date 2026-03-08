"""
Section 4 (朗讀短文) Analyzer for PSC

Analyzes reading passage performance:
- 錯讀/漏讀/增讀 (misread/omission/addition)
- 聲韻系統缺陷 (phoneme system defects)
- 語調偏誤 (intonation errors)
- 停連不當 (pause/continuation errors)
- 不流暢/回讀 (disfluency/re-reading)

Integrates with error_detector.py and psc_scorer.py.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass


# PSC Section 4 scoring rules
SECTION4_DEDUCTIONS = {
    "misread": 0.1,           # 錯讀 - 扣0.1分/字
    "omission": 0.1,          # 漏讀 - 扣0.1分/字
    "addition": 0.1,          # 增讀 - 扣0.1分/字
    "tone_defect": 0.1,       # 聲韻系統缺陷 - 扣0.5-1分 (use 0.1 for simplicity)
    "intonation_error": 0.5,  # 語調偏誤 - 扣0.5/1/2分
    "pause_error": 0.5,        # 停連不當 - 扣0.5/1/2分
    "disfluency": 0.5,        # 不流暢/回讀 - 扣0.5/1/2分
}

# Standard reading pace (characters per minute)
NORMAL_CPM = 150  # ~150 chars/min is normal reading pace
FAST_CPM = 200    # Too fast
SLOW_CPM = 80     # Too slow


@dataclass
class IntonationError:
    """Intonation error details"""
    position: int
    character: str
    context: str
    error_type: str  # "rising", "falling", "flat", "question"
    severity: str    # "minor", "moderate", "major"
    deduction: float


@dataclass
class PauseError:
    """Pause/continuation error details"""
    position: int
    before_char: str
    after_char: str
    error_type: str  # "过早停顿", "过长停顿", "不当连读", "不当断句"
    severity: str
    deduction: float


@dataclass
class DisfluencyError:
    """Disfluency error details"""
    position: int
    start_position: int
    end_position: int
    error_type: str  # "repetition", "re-reading", "hesitation", "long_pause"
    severity: str
    deduction: float


class Section4Analyzer:
    """Analyze Section 4 (Reading Passage) performance"""

    def __init__(self):
        self.deductions = SECTION4_DEDUCTIONS

    def analyze_passage(
        self,
        expected_text: str,
        transcription: str,
        audio_duration: float = 0,
        section: int = 4
    ) -> Dict[str, Any]:
        """
        Analyze a reading passage for PSC Section 4.

        Args:
            expected_text: The passage user should read
            transcription: What user actually said
            audio_duration: Duration of audio in seconds
            section: PSC section (should be 4)

        Returns:
            Dict with all analysis results
        """
        # Clean texts
        expected_clean = re.sub(r'[，。？！、；：""''（）【】《》…—\s]', '', expected_text)
        transcription_clean = re.sub(r'[，。？！、；：""''（）【】《》…—\s]', '', transcription)

        # 1. Detect misread/omission/addition errors
        reading_errors = self._detect_reading_errors(expected_clean, transcription_clean)

        # 2. Analyze intonation (based on iFlytek tone score)
        intonation_issues = self._analyze_intonation(
            expected_clean, audio_duration
        )

        # 3. Analyze pauses and continuation
        pause_issues = self._analyze_pauses(
            expected_clean, audio_duration
        )

        # 4. Analyze disfluency
        disfluency_issues = self._analyze_disfluency(
            expected_clean, transcription_clean, audio_duration
        )

        # 5. Calculate total deductions
        total_deductions = self._calculate_deductions(
            reading_errors, intonation_issues, pause_issues, disfluency_issues
        )

        # 6. Calculate score
        max_score = 30.0
        raw_score = max(0, max_score - total_deductions)

        # Add timeout penalty if applicable
        timeout_penalty = 0
        if audio_duration > 240:  # 4 minutes
            timeout_penalty = 1.0

        final_score = max(0, raw_score - timeout_penalty)

        return {
            "section": section,
            "max_score": max_score,
            "raw_score": round(raw_score, 2),
            "final_score": round(final_score, 2),
            "timeout_penalty": timeout_penalty,
            "reading_errors": reading_errors,
            "intonation_issues": intonation_issues,
            "pause_issues": pause_issues,
            "disfluency_issues": disfluency_issues,
            "total_deductions": round(total_deductions, 2),
            "error_counts": {
                "reading_errors": len(reading_errors),
                "intonation_errors": len(intonation_issues),
                "pause_errors": len(pause_issues),
                "disfluency_errors": len(disfluency_issues),
            }
        }

    def _detect_reading_errors(
        self,
        expected: str,
        transcription: str
    ) -> List[Dict[str, Any]]:
        """Detect misread, omission, and addition errors"""
        errors = []

        # Find omissions (chars in expected but not in transcription)
        expected_chars = list(expected)
        trans_chars = list(transcription)

        for i, char in enumerate(expected_chars):
            if char not in trans_chars:
                errors.append({
                    "type": "omission",
                    "position": i,
                    "character": char,
                    "deduction": self.deductions["omission"],
                    "description_en": f"Omission: character '{char}' not read",
                    "description_zh": f"漏讀: 未讀出'{char}'"
                })

        # Find additions (chars in transcription but not in expected)
        for i, char in enumerate(trans_chars):
            if char not in expected_chars:
                errors.append({
                    "type": "addition",
                    "position": i,
                    "character": char,
                    "deduction": self.deductions["addition"],
                    "description_en": f"Addition: extra character '{char}' read",
                    "description_zh": f"增讀: 多讀了'{char}'"
                })

        # Find misreads (same char but different position - simplified)
        # In a real implementation, this would use ASR to detect mispronunciations

        return errors

    def _analyze_intonation(
        self,
        expected_text: str,
        audio_duration: float
    ) -> List[IntonationError]:
        """
        Analyze intonation patterns.

        Note: Full intonation analysis requires audio processing.
        This provides a simplified analysis based on reading pace.
        """
        issues = []

        if audio_duration > 0:
            char_count = len(expected_text)
            cpm = (char_count / audio_duration) * 60

            # Check for too fast or too slow reading
            if cpm > FAST_CPM:
                # Too fast - may have intonation issues
                issues.append(IntonationError(
                    position=0,
                    character="",
                    context="全文",
                    error_type="too_fast",
                    severity="moderate",
                    deduction=self.deductions["intonation_error"]
                ))
            elif cpm < SLOW_CPM:
                # Too slow - may indicate difficulty with intonation
                issues.append(IntonationError(
                    position=0,
                    character="",
                    context="全文",
                    error_type="too_slow",
                    severity="moderate",
                    deduction=self.deductions["intonation_error"]
                ))

        # Check for question marks in text - indicate rising intonation needed
        if "？" in expected_text or "?" in expected_text:
            # Would need audio analysis to detect if properly pronounced with rising tone
            pass

        return issues

    def _analyze_pauses(
        self,
        expected_text: str,
        audio_duration: float
    ) -> List[PauseError]:
        """Analyze pause patterns"""
        issues = []

        if audio_duration > 0:
            char_count = len(expected_text)
            cpm = (char_count / audio_duration) * 60

            # Check for unnatural pause patterns
            # Very slow reading with frequent pauses
            if cpm < SLOW_CPM:
                # Too many pauses
                issue_count = max(1, int((SLOW_CPM - cpm) / 30))
                for i in range(min(issue_count, 3)):
                    issues.append(PauseError(
                        position=i * 10,
                        before_char="",
                        after_char="",
                        error_type="过长停顿",
                        severity="moderate",
                        deduction=self.deductions["pause_error"]
                    ))

        return issues

    def _analyze_disfluency(
        self,
        expected_text: str,
        transcription: str,
        audio_duration: float
    ) -> List[DisfluencyError]:
        """Analyze disfluency (re-reading, repetition, etc.)"""
        issues = []

        # Check for repetitions in transcription (user repeated themselves)
        # This is simplified - would need more sophisticated analysis

        # Check for re-reading patterns
        if transcription:
            # Check if transcription is significantly longer than expected
            # (might indicate repetitions)
            ratio = len(transcription) / max(1, len(expected_text))
            if ratio > 1.2:
                # Significant extra content - likely re-reading
                issues.append(DisfluencyError(
                    position=0,
                    start_position=0,
                    end_position=len(transcription),
                    error_type="re-reading",
                    severity="moderate",
                    deduction=self.deductions["disfluency"]
                ))

        # Check for very short duration (rushed reading)
        if audio_duration > 0 and audio_duration < 30:
            issues.append(DisfluencyError(
                position=0,
                start_position=0,
                end_position=0,
                error_type="rushed",
                severity="major",
                deduction=self.deductions["disfluency"] * 2
            ))

        return issues

    def _calculate_deductions(
        self,
        reading_errors: List[Dict],
        intonation_issues: List[IntonationError],
        pause_issues: List[PauseError],
        disfluency_issues: List[DisfluencyError]
    ) -> float:
        """Calculate total score deductions"""
        total = 0.0

        # Reading errors
        for error in reading_errors:
            total += error.get("deduction", 0)

        # Intonation issues
        for issue in intonation_issues:
            total += issue.deduction

        # Pause issues
        for issue in pause_issues:
            total += issue.deduction

        # Disfluency issues
        for issue in disfluency_issues:
            total += issue.deduction

        return total


# Convenience function
def analyze_section4(
    expected_text: str,
    transcription: str,
    audio_duration: float = 0,
    section: int = 4
) -> Dict[str, Any]:
    """Analyze Section 4 (Reading Passage) performance"""
    analyzer = Section4Analyzer()
    return analyzer.analyze_passage(expected_text, transcription, audio_duration, section)
