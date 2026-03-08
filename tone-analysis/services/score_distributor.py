"""
Score Distributor for PSC Character Pronunciation Analysis

This module distributes iFlytek's overall scores to individual characters
based on character difficulty, transcription match, and position weighting.
"""

import re
from typing import List, Dict, Any, Optional
from .character_difficulty import get_character_difficulty, get_practice_words_for_issue
from . import pinyin_db


def clean_text(text: str) -> str:
    """Remove punctuation from text"""
    return re.sub(r'[，。？！、；：""''（）【】《》…—\s]', '', text)


def get_tone_from_pinyin(pinyin: str) -> int:
    """Extract tone number from pinyin string using pinyin_db"""
    if not pinyin:
        return 0
    # Use pinyin_db's get_tone function which handles both Unicode marks and digits
    return pinyin_db.get_tone(pinyin)


def distribute_scores(
    expected_text: str,
    transcription: str,
    overall_score: float,
    tone_score: float,
    fluency_score: float
) -> List[Dict[str, Any]]:
    """
    Distribute iFlytek scores to individual characters based on:
    1. Character difficulty (harder = more likely to have lower score)
    2. Transcription match (matched = higher score)
    3. Position in text (beginning = slightly higher weight)

    Args:
        expected_text: The text user should say
        transcription: What user actually said (from ASR)
        overall_score: iFlytek overall pronunciation score (0-100)
        tone_score: iFlytek tone score (0-100)
        fluency_score: iFlytek fluency score (0-100)

    Returns:
        List of character analysis results
    """

    # Clean texts
    expected_clean = clean_text(expected_text)
    transcription_clean = clean_text(transcription)

    results = []

    # Track transcription matches
    transcription_chars = list(transcription_clean)

    # Base scores as percentages
    base_pron_score = overall_score / 100.0
    base_tone_score = tone_score / 100.0

    for i, char in enumerate(expected_clean):
        # Skip if punctuation
        if not char.strip():
            continue

        # Get character difficulty info
        difficulty_info = get_character_difficulty(char)
        difficulty = difficulty_info.get("difficulty", 3)
        issues = difficulty_info.get("issues", [])
        category = difficulty_info.get("category", "basic")

        # Calculate difficulty factor (1.0 = easiest, 0.6 = hardest)
        difficulty_factor = 1.0 - (difficulty - 1) * 0.1

        # Check if character was transcribed (fuzzy match)
        char_transcribed = False
        actual_char = ""
        if char in transcription_clean:
            char_transcribed = True
            actual_char = char
        elif len(transcription_chars) > 0:
            # Check for similar characters
            for tc in transcription_chars:
                if tc == char:
                    char_transcribed = True
                    actual_char = tc
                    break

        # Get actual pinyin/initial/final from transcribed character
        actual_pinyin = ""
        actual_tone = 0
        actual_initial = ""
        actual_final = ""
        if actual_char:
            actual_info = pinyin_db.get_char_info(actual_char)
            if actual_info:
                actual_pinyin = actual_info.get("pinyin", "")
                actual_tone = actual_info.get("tone", 0)
                actual_initial = pinyin_db.get_initial(actual_pinyin) if actual_pinyin else ""
                actual_final = pinyin_db.get_final(actual_pinyin) if actual_pinyin else ""

        # Position weight (slightly higher for beginning)
        position_weight = 1.0 + (0.05 if i < 3 else 0)

        # Calculate estimated scores
        # If transcribed correctly, use higher end of score range
        # If not transcribed, use lower end
        if char_transcribed:
            # Character was recognized
            estimated_pron = min(95, (base_pron_score * 100 + 10) * difficulty_factor * position_weight)
            estimated_tone = min(95, (base_tone_score * 100 + 5) * difficulty_factor)
        else:
            # Character not recognized - significantly lower score
            estimated_pron = max(20, (base_pron_score * 100 - 20) * difficulty_factor)
            estimated_tone = max(20, (base_tone_score * 100 - 20) * difficulty_factor)

        # Determine status based on estimated score
        if estimated_pron >= 90:
            status = "correct"
        elif estimated_pron >= 75:
            status = "good"
        elif estimated_pron >= 50:
            status = "needs_work"
        else:
            status = "poor"

        # Get pinyin info - fall back to pinyin_db if not in difficulty database
        pinyin = difficulty_info.get("pinyin", "")
        if not pinyin:
            # Try to get from pinyin_db
            char_info = pinyin_db.get_char_info(char)
            if char_info:
                pinyin = char_info.get("pinyin", "")

        expected_tone = get_tone_from_pinyin(pinyin) if pinyin else 0

        # Generate feedback based on issues
        feedback_en = ""
        feedback_zh = ""
        fix_tip_en = ""
        fix_tip_zh = ""
        practice_words = []

        if status != "correct" and issues:
            # Generate specific feedback based on issues
            for issue in issues[:2]:  # Limit to 2 issues
                if issue == "zh":
                    feedback_en = "Retroflex zh needs practice"
                    feedback_zh = "翘舌音zh需要练习"
                    fix_tip_en = "Curl your tongue back for zh"
                    fix_tip_zh = "舌头向后翘起发zh音"
                    practice_words = ["知道", "中国", "车站"]
                elif issue == "ch":
                    feedback_en = "Retroflex ch needs practice"
                    feedback_zh = "翘舌音ch需要练习"
                    fix_tip_en = "Curl your tongue back for ch"
                    fix_tip_zh = "舌头向后翘起发ch音"
                    practice_words = ["吃饭", "出去", "车站"]
                elif issue == "sh":
                    feedback_en = "Retroflex sh needs practice"
                    feedback_zh = "翘舌音sh需要练习"
                    fix_tip_en = "Curl your tongue back for sh"
                    fix_tip_zh = "舌头向后翘起发sh音"
                    practice_words = ["是的", "老师", "学生"]
                elif issue == "r":
                    feedback_en = "Retroflex r needs practice"
                    feedback_zh = "翘舌音r需要练习"
                    fix_tip_en = "Curl your tongue back for r"
                    fix_tip_zh = "舌头向后翘起发r音"
                    practice_words = ["人民", "认识", "日本"]
                elif issue in ["n", "l"]:
                    feedback_en = f"N/L distinction needs practice"
                    feedback_zh = "n/l区分需要练习"
                    fix_tip_en = "Distinguish between n (舌尖抵住上齿龈) and l (舌尖抵住上齿龈后缩)"
                    fix_tip_zh = "注意n和l的发音位置"
                    practice_words = ["努力", "那里", "来了"]
                elif "ü" in issue or issue == "ü":
                    feedback_en = "Ü vowel needs practice"
                    feedback_zh = "ü元音需要练习"
                    fix_tip_en = "Round your lips and say ü"
                    fix_tip_zh = "嘴唇圆起发ü音"
                    practice_words = ["绿", "雨", "鱼"]
                elif "tone_3" in issue or issue == "tone_3":
                    feedback_en = "Third tone needs practice"
                    feedback_zh = "第三声需要练习"
                    fix_tip_en = "Practice the dipping tone: go down then up"
                    fix_tip_zh = "练习降升调：先降后升"
                    practice_words = ["马", "把", "可"]
                elif issue == "neutral":
                    feedback_en = "Neutral tone needs attention"
                    feedback_zh = "轻声需要注意"
                    fix_tip_en = "Say it quickly and lightly"
                    fix_tip_zh = "快速轻柔地发出"
                    practice_words = ["的", "了", "着"]
                else:
                    # Generic feedback
                    feedback_en = f"Pronunciation needs improvement"
                    feedback_zh = "发音需要改进"
                    fix_tip_en = "Practice this character carefully"
                    fix_tip_zh = "仔细练习这个字"

        elif status != "correct":
            feedback_en = "Pronunciation needs improvement"
            feedback_zh = "发音需要改进"
            fix_tip_en = "Focus on clear pronunciation"
            fix_tip_zh = "注意清晰发音"

        # Build result - extract initial and final from pinyin
        expected_initial = pinyin_db.get_initial(pinyin) if pinyin else ""
        expected_final = pinyin_db.get_final(pinyin) if pinyin else ""

        result = {
            "character": char,
            "expected_pinyin": pinyin,
            "expected_tone": expected_tone,
            "expected_initial": expected_initial,
            "expected_final": expected_final,
            "estimated_pronunciation": round(estimated_pron, 1),
            "estimated_tone_accuracy": round(estimated_tone, 1),
            "status": status,
            "difficulty": difficulty,
            "category": category,
            "issues": issues,
            "actual_pinyin": actual_pinyin,
            "actual_tone": actual_tone,
            "actual_initial": actual_initial,
            "actual_final": actual_final,
        }

        # Add feedback fields if applicable
        if feedback_en:
            result["feedback_en"] = feedback_en
        if feedback_zh:
            result["feedback_zh"] = feedback_zh
        if fix_tip_en:
            result["fix_tip_en"] = fix_tip_en
        if fix_tip_zh:
            result["fix_tip_zh"] = fix_tip_zh
        if practice_words:
            result["practice_words"] = practice_words

        results.append(result)

    return results


def analyze_tone_patterns(character_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze tone patterns from character results"""

    tone_issues = []
    tone_correct = 0
    tone_total = 0

    for cr in character_results:
        tone_total += 1
        if cr.get("estimated_tone_accuracy", 0) >= 70:
            tone_correct += 1
        else:
            issues = cr.get("issues", [])
            for issue in issues:
                if "tone" in issue:
                    tone_issues.append({
                        "character": cr["character"],
                        "tone": cr.get("expected_tone", 0),
                        "accuracy": cr.get("estimated_tone_accuracy", 0)
                    })

    accuracy = round(tone_correct / tone_total * 100, 1) if tone_total > 0 else 0

    return {
        "total_tones": tone_total,
        "correct_tones": tone_correct,
        "tone_accuracy": f"{accuracy}%",
        "tone_issues": tone_issues[:5],  # Top 5 issues
    }


def analyze_phoneme_patterns(character_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze phoneme (initial/final) patterns from character results"""

    initial_issues = []
    final_issues = []

    for cr in character_results:
        if cr.get("estimated_pronunciation", 0) < 75:
            issues = cr.get("issues", [])
            for issue in issues:
                if issue in ["zh", "ch", "sh", "r"]:
                    initial_issues.append({
                        "character": cr["character"],
                        "issue": issue,
                        "accuracy": cr.get("estimated_pronunciation", 0)
                    })
                elif issue in ["n", "l"]:
                    initial_issues.append({
                        "character": cr["character"],
                        "issue": "n/l",
                        "accuracy": cr.get("estimated_pronunciation", 0)
                    })
                elif "ü" in issue:
                    final_issues.append({
                        "character": cr["character"],
                        "issue": "ü",
                        "accuracy": cr.get("estimated_pronunciation", 0)
                    })

    # Count issues by type
    from collections import Counter
    initial_counts = Counter([i["issue"] for i in initial_issues])
    final_counts = Counter([i["issue"] for i in final_issues])

    return {
        "initial_issues": initial_issues[:5],
        "final_issues": final_issues[:5],
        "common_initial": list(initial_counts.keys())[:3],
        "common_final": list(final_counts.keys())[:3],
    }
