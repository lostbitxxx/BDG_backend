"""
PSC Scoring Service
Calculates scores according to official PSC (Putonghua Shuiping Ceshi) standards.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SectionScore:
    """Score for a PSC section"""
    section: int
    max_score: float
    raw_score: float
    final_score: float
    timeout_penalty: float
    error_count: int
    defect_count: int
    breakdown: Dict[str, Any]


@dataclass
class PSCRating:
    """Final PSC rating"""
    level: str  # Level 1, Level 2, Level 3, Below Level 3
    grade: str  # A or B
    pass_status: bool  # True if score >= ============================================================================
# SECTION CONFIGURATION
# 60


# ============================================================================

# Official PSC Section Configuration
# Based on PSC (Putonghua Shuiping Ceshi) scoring standards
SECTION_CONFIG = {
    1: {
        "name": "讀單音節字詞",
        "name_en": "Read Single Characters",
        "description": "100 single characters, no neutral tone or erhua",
        "max_score": 10.0,
        "time_limit": 210,  # 3.5 minutes (210 seconds)
        "content_info": "100音節, 70% from 表一, 30% from 表二",
        "deduction": {
            "phonetic_error": 0.1,      # 語音錯誤 - 扣0.1分/個
            "phonetic_defect": 0.05,     # 語音缺陷 - 扣0.05分/個
        },
        "timeout_penalty": {
            "under1min": 0.5,           # 超時1分鐘以內 - 扣0.5分
            "over1min": 1.0,            # 超時1分鐘以上 - 扣1分
        }
    },
    2: {
        "name": "讀多音節詞語",
        "name_en": "Read Polysyllabic Words",
        "description": "50 two-syllable words, tests tone pairs, tone sandhi, neutral tone",
        "max_score": 20.0,
        "time_limit": 150,  # 2.5 minutes (150 seconds)
        "content_info": "100音節, 70% from 表一, 30% from 表二",
        "deduction": {
            "phonetic_error": 0.2,      # 語音錯誤 - 扣0.2分/個
            "phonetic_defect": 0.1,     # 語音缺陷 - 扣0.1分/個
        },
        "timeout_penalty": {
            "under1min": 0.5,           # 超時1分鐘以內 - 扣0.5分
            "over1min": 1.0,            # 超時1分鐘以上 - 扣1分
        },
        # Special checks for Section 2
        "special_checks": ["tone_sandhi", "neutral_tone", "erhua"]
    },
    3: {
        "name": "選擇判斷",
        "name_en": "Choice & Judgment",
        "description": "25 questions: 10 vocabulary, 10 classifiers, 5 grammar",
        "max_score": 10.0,
        "time_limit": 180,  # 3 minutes (180 seconds)
        "content_info": "10詞語判斷 + 10量詞搭配 + 5語法判斷",
        "deduction": {
            "phonetic_error": 0.1,      # 語音錯誤 - 扣0.1分/個
            "word_judgment": 0.25,      # 詞語判斷錯誤 - 扣0.25分/組
            "classifier": 0.5,          # 量詞搭配錯誤 - 扣0.5分/組
            "grammar": 0.5,             # 語法判斷錯誤 - 扣0.5分/組
        },
        "timeout_penalty": {
            "under1min": 0.5,           # 超時1分鐘以內 - 扣0.5分
            "over1min": 1.0,            # 超時1分鐘以上 - 扣1分
        }
    },
    4: {
        "name": "朗讀短文",
        "name_en": "Reading Passage",
        "description": "Read a 400-character passage aloud",
        "max_score": 30.0,
        "time_limit": 240,  # 4 minutes (240 seconds)
        "content_info": "400字以內, from 朗讀作品",
        "deduction": {
            "misread": 0.1,             # 錯讀 - 扣0.1分/字
            "omission": 0.1,            # 漏讀 - 扣0.1分/字
            "addition": 0.1,            # 增讀 - 扣0.1分/字
            "tone_defect": 0.1,        # 聲韻系統缺陷 - 扣0.5-1分
            "intonation_error": 0.5,   # 語調偏誤 - 扣0.5/1/2分
            "pause_error": 0.5,        # 停連不當 - 扣0.5/1/2分
            "disfluency": 0.5,          # 不流暢/回讀 - 扣0.5/1/2分
        },
        "timeout_penalty": 1.0          # 超時 - 扣1分
    },
    5: {
        "name": "命題說話",
        "name_en": "Topic Speaking",
        "description": "Speak for 3 minutes on a given topic (choose 1 of 2)",
        "max_score": 30.0,
        "time_limit": 180,  # 3 minutes (180 seconds)
        "content_info": "二選一話題, from 測試話題",
        "sub_scores": {
            "pronunciation": 20.0,      # 語音 - 20分 (6檔)
            "vocabulary": 5.0,          # 詞彙語法 - 5分 (3檔)
            "fluency": 5.0,             # 自然流暢 - 5分 (3檔)
        },
        # PSC 6-3-3 tier scoring for Section 5
        "pronunciation_tiers": {
            1: {"range": (0, 1), "criteria": "極少失誤", "deduction": (0, 1)},
            2: {"range": (1.5, 2), "criteria": "錯誤<10，方音不明顯", "deduction": (1.5, 2)},
            3: {"range": (3, 4), "criteria": "錯誤<10，方音明顯 OR 錯誤10-15，方音不明顯", "deduction": (3, 4)},
            4: {"range": (5, 6), "criteria": "錯誤10-15，方音較明顯", "deduction": (5, 6)},
            5: {"range": (7, 9), "criteria": "錯誤>15，方音明顯", "deduction": (7, 9)},
            6: {"range": (10, 12), "criteria": "錯誤多，方音重", "deduction": (10, 12)},
        },
        "vocabulary_tiers": {
            1: {"deduction": 0, "criteria": "規範"},
            2: {"deduction": (0.5, 1), "criteria": "偶不規範"},
            3: {"deduction": (2, 3), "criteria": "屢不規範"},
        },
        "fluency_tiers": {
            1: {"deduction": 0, "criteria": "自然流暢"},
            2: {"deduction": (0.5, 1), "criteria": "口語化差、背稿"},
            3: {"deduction": (2, 3), "criteria": "不連貫、生硬"},
        },
        "time_deduction": {
            "under30s": 30.0,           # 說話不足0.5分鐘 - 扣30分
            "under1min": (1, 3),        # 1分鐘以內 - 扣1/2/3分
            "over1min": (4, 6),         # 1分鐘以上 - 扣4/5/6分
        }
    }
}


# ============================================================================
# SCORER CLASS
# ============================================================================

class PSCScorer:
    """Calculate PSC-aligned scores"""

    def __init__(self):
        self.config = SECTION_CONFIG

    def calculate_section_score(
        self,
        section: int,
        errors: List[Dict[str, Any]],
        duration: float,
        character_count: int = 0
    ) -> SectionScore:
        """
        Calculate score for a specific PSC section.

        Args:
            section: PSC section (1-5)
            errors: List of detected errors
            duration: Time taken in seconds
            character_count: Number of characters (for Section 4)

        Returns:
            SectionScore with breakdown
        """
        config = self.config.get(section)
        if not config:
            raise ValueError(f"Invalid section: {section}")

        max_score = config["max_score"]
        time_limit = config["time_limit"]

        # Count errors by type
        error_count = 0
        defect_count = 0

        tone_errors = 0
        initial_errors = 0
        final_errors = 0
        omissions = 0
        additions = 0

        for error in errors:
            severity = error.get("severity", "error")
            category = error.get("category", "")

            if severity == "error":
                error_count += 1
            elif severity == "defect":
                defect_count += 1

            if category == "tone_error":
                tone_errors += 1
            elif category == "initial_error":
                initial_errors += 1
            elif category == "final_error":
                final_errors += 1
            elif category == "omission":
                omissions += 1
            elif category == "addition":
                additions += 1

        # Calculate raw score based on section
        if section in [1, 2]:
            error_deduction = error_count * config["deduction"]["phonetic_error"]
            defect_deduction = defect_count * config["deduction"]["phonetic_defect"]
            raw_score = max(0, max_score - error_deduction - defect_deduction)

        elif section == 3:
            # Section 3 has different deduction rules
            raw_score = max_score  # Simplified - would need actual answers

        elif section == 4:
            # Section 4: Reading passage
            char_errors = omissions + additions
            misread_deduction = char_errors * config["deduction"]["misread"]
            tone_deduction = tone_errors * config["deduction"]["tone_defect"]
            raw_score = max(0, max_score - misread_deduction - tone_deduction)

        elif section == 5:
            # Section 5: 命題說話 - Full 6-3-3 tier scoring
            # Based on PSC official rubric:
            # - 語音 (Pronunciation): 20 points (6 tiers)
            # - 詞彙語法 (Vocabulary/Grammar): 5 points (3 tiers)
            # - 自然流暢 (Fluency): 5 points (3 tiers)

            # Get tier configs from SECTION_CONFIG
            pron_tiers = config.get("pronunciation_tiers", {})
            vocab_tiers = config.get("vocabulary_tiers", {})
            fluency_tiers = config.get("fluency_tiers", {})

            # Calculate pronunciation score based on error count and dialect features
            # Determine which tier based on error count
            total_errors = error_count + defect_count

            # Simplified dialect detection (in real implementation, would use AI to detect)
            dialect_obvious = False  # Would be determined by analysis

            pronunciation_deduction = self._calculate_pronunciation_tier(
                total_errors, dialect_obvious, pron_tiers
            )
            pronunciation_score = max(0, 20 - pronunciation_deduction)

            # Vocabulary/Grammar tier (simplified - would need AI analysis)
            vocab_deduction = self._calculate_vocab_tier(
                error_count, vocab_tiers
            )
            vocabulary_score = max(0, 5 - vocab_deduction)

            # Fluency tier (simplified - would need AI analysis)
            fluency_deduction = self._calculate_fluency_tier(
                error_count, fluency_tiers
            )
            fluency_score = max(0, 5 - fluency_deduction)

            raw_score = pronunciation_score + vocabulary_score + fluency_score

        else:
            raw_score = 0

        # Calculate timeout penalty
        timeout_penalty = 0
        if section in [1, 2, 3]:
            time_over = duration - time_limit
            if time_over > 60:
                timeout_penalty = config["timeout_penalty"]["over1min"]
            elif time_over > 0:
                timeout_penalty = config["timeout_penalty"]["under1min"]

        elif section == 4:
            if duration > time_limit:
                timeout_penalty = config["timeout_penalty"]

        elif section == 5:
            if duration < 30:
                timeout_penalty = config["time_deduction"]["under30s"]
            elif duration < 60:
                timeout_penalty = config["time_deduction"]["under1min"]
            elif duration > time_limit:
                timeout_penalty = config["time_deduction"]["over1min"]

        # Final score
        final_score = max(0, raw_score - timeout_penalty)

        # Generate breakdown
        breakdown = {
            "raw_score": round(raw_score, 2),
            "error_count": error_count,
            "defect_count": defect_count,
            "error_breakdown": {
                "tone_errors": tone_errors,
                "initial_errors": initial_errors,
                "final_errors": final_errors,
                "omissions": omissions,
                "additions": additions,
            },
            "deductions": {
                "error_deduction": error_count * config["deduction"].get("phonetic_error", 0.1),
                "defect_deduction": defect_count * config["deduction"].get("phonetic_defect", 0.05),
                "timeout_penalty": timeout_penalty,
            }
        }

        return SectionScore(
            section=section,
            max_score=max_score,
            raw_score=round(raw_score, 2),
            final_score=round(final_score, 2),
            timeout_penalty=round(timeout_penalty, 2),
            error_count=error_count,
            defect_count=defect_count,
            breakdown=breakdown
        )

    def calculate_total_score(
        self,
        section_scores: Dict[int, SectionScore]
    ) -> Dict[str, Any]:
        """Calculate total PSC score from section scores"""

        total_score = sum(s.final_score for s in section_scores.values())

        # Determine level and grade
        rating = self.determine_level(total_score)

        return {
            "total_score": round(total_score, 2),
            "max_score": 100.0,
            "level": rating.level,
            "grade": rating.grade,
            "pass": rating.pass_status,
            "section_scores": {
                s.section: {
                    "max_score": s.max_score,
                    "final_score": s.final_score,
                    "error_count": s.error_count,
                    "defect_count": s.defect_count
                }
                for s in section_scores.values()
            }
        }

    def _calculate_pronunciation_tier(
        self,
        error_count: int,
        dialect_obvious: bool,
        tiers: Dict
    ) -> float:
        """
        Calculate pronunciation deduction based on PSC 6-tier rubric.

        6-Tier Pronunciation Scoring (20 points):
        - 一檔: 極少失誤 - 扣0-1分
        - 二檔: 錯誤<10，方音不明顯 - 扣1.5-2分
        - 三檔: 錯誤<10，方音明顯 OR 錯誤10-15，方音不明顯 - 扣3-4分
        - 四檔: 錯誤10-15，方音較明顯 - 扣5-6分
        - 五檔: 錯誤>15，方音明顯 - 扣7-9分
        - 六檔: 錯誤多，方音重 - 扣10-12分
        """
        if error_count == 0:
            return 0  # Tier 1: minimal errors
        elif error_count < 10:
            if not dialect_obvious:
                return 1.5  # Tier 2
            else:
                return 3.0  # Tier 3
        elif error_count <= 15:
            if not dialect_obvious:
                return 3.5  # Tier 3
            else:
                return 5.5  # Tier 4
        else:  # error_count > 15
            if not dialect_obvious:
                return 8.0  # Tier 5
            else:
                return 11.0  # Tier 6

    def _calculate_vocab_tier(
        self,
        error_count: int,
        tiers: Dict
    ) -> float:
        """
        Calculate vocabulary/grammar deduction based on PSC 3-tier rubric.

        3-Tier Vocabulary/Grammar Scoring (5 points):
        - 一檔: 規範 - 扣0分
        - 二檔: 偶不規範 - 扣0.5-1分
        - 三檔: 屢不規範 - 扣2-3分
        """
        if error_count == 0:
            return 0  # Tier 1: standard
        elif error_count <= 2:
            return 0.75  # Tier 2: occasional
        else:
            return 2.5  # Tier 3: frequent

    def _calculate_fluency_tier(
        self,
        pause_count: int,
        tiers: Dict
    ) -> float:
        """
        Calculate fluency deduction based on PSC 3-tier rubric.

        3-Tier Fluency Scoring (5 points):
        - 一檔: 自然流暢 - 扣0分
        - 二檔: 口語化差、背稿 - 扣0.5-1分
        - 三檔: 不連貫、生硬 - 扣2-3分
        """
        if pause_count == 0:
            return 0  # Tier 1: natural
        elif pause_count <= 3:
            return 0.75  # Tier 2: stilted
        else:
            return 2.5  # Tier 3: disjointed

    def determine_level(self, total_score: float) -> PSCRating:
        """Determine PSC level and grade based on total score"""

        if total_score >= 97:
            return PSCRating(level="一级", grade="A", pass_status=True)
        elif total_score >= 92:
            return PSCRating(level="一级", grade="B", pass_status=True)
        elif total_score >= 87:
            return PSCRating(level="二级", grade="A", pass_status=True)
        elif total_score >= 80:
            return PSCRating(level="二级", grade="B", pass_status=True)
        elif total_score >= 70:
            return PSCRating(level="三级", grade="A", pass_status=True)
        elif total_score >= 60:
            return PSCRating(level="三级", grade="B", pass_status=True)
        else:
            return PSCRating(level="三级以下", grade="C", pass_status=False)

    def calculate_scores_from_errors(
        self,
        expected_text: str,
        transcription: str,
        errors: List[Dict[str, Any]],
        section: int = 4,
        duration: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate all scores from error analysis.

        Args:
            expected_text: Expected text
            transcription: User's transcription
            errors: List of detected errors
            section: PSC section
            duration: Time taken in seconds

        Returns:
            Complete score breakdown
        """
        # Calculate base scores (simplified)
        error_count = len([e for e in errors if e.get("severity") == "error"])
        defect_count = len([e for e in errors if e.get("severity") == "defect"])

        # Calculate percentage scores
        if section in [1, 2]:
            char_count = len(expected_text.replace(" ", ""))
            if char_count > 0:
                accuracy = 1 - (error_count * 0.1 + defect_count * 0.05) / char_count
            else:
                accuracy = 0
        else:
            # Simplified for other sections
            accuracy = max(0, 1 - (error_count + defect_count) * 0.05)

        pronunciation_score = min(100, accuracy * 100)
        tone_score = min(100, 100 - len([e for e in errors if e.get("category") == "tone_error"]) * 10)
        fluency_score = min(100, 100 - duration * 0.1 if duration > 0 else 90)

        overall = (pronunciation_score + tone_score + fluency_score) / 3

        # Calculate section score
        section_score = self.calculate_section_score(section, errors, duration)

        # Get rating
        rating = self.determine_level(overall)

        return {
            "overall": round(overall, 1),
            "pronunciation": round(pronunciation_score, 1),
            "tone": round(tone_score, 1),
            "fluency": round(fluency_score, 1),
            "psc_level": rating.level,
            "psc_grade": rating.grade,
            "pass": rating.pass_status,
            "section_score": section_score.final_score,
            "max_score": section_score.max_score,
            "error_count": error_count,
            "defect_count": defect_count,
            "breakdown": section_score.breakdown
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_scorer_instance = None


def get_scorer() -> PSCScorer:
    """Get singleton instance of PSC scorer"""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = PSCScorer()
    return _scorer_instance


def calculate_scores(
    expected_text: str,
    transcription: str,
    errors: List[Dict[str, Any]],
    section: int = 4,
    duration: float = 0
) -> Dict[str, Any]:
    """Convenience function to calculate scores"""
    scorer = get_scorer()
    return scorer.calculate_scores_from_errors(
        expected_text=expected_text,
        transcription=transcription,
        errors=errors,
        section=section,
        duration=duration
    )
