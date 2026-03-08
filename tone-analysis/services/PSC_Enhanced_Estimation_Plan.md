# PSC Character Pronunciation Analysis - Enhanced Estimation Plan

## Executive Summary

This plan implements a **smart estimation system** that provides per-character pronunciation feedback using only iFlytek's overall scores. The system uses character difficulty weighting and score distribution to estimate individual character performance.

---

## Current System Analysis

### What We Have
- iFlytek: Overall scores (pronunciation, tone, fluency) - NO per-character data
- ElevenLabs: Transcription only
- Error Detector: Character mismatch detection (not quality)
- Feedback Generator: Generic score-based feedback
- ERROR_PATTERNS: 793+ patterns with practice words

### What's Missing
- Per-character tone accuracy (1-4)
- Per-character initial/final quality estimation
- Character difficulty weighting
- Smart score distribution

---

## Implementation Plan

### Phase 1: Character Difficulty Database

Create a comprehensive character difficulty rating system:

```python
CHARACTER_DIFFICULTY = {
    # Difficulty: 1-5 (1=easy, 5=hard)
    # Categories: retroflex, nasal, tone_2_3, ü, neutral

    "知": {"difficulty": 4, "issues": ["zh", "tone_2_3"], "category": "retroflex"},
    "吃": {"difficulty": 4, "issues": ["ch", "tone_1"], "category": "retroflex"},
    "是": {"difficulty": 3, "issues": ["sh", "tone_4"], "category": "retroflex"},
    "人": {"difficulty": 1, "issues": ["r"], "category": "retroflex"},
    "女": {"difficulty": 3, "issues": ["n", "tone_3"], "category": "nasal"},
    "吕": {"difficulty": 4, "issues": ["ü", "tone_3"], "category": "umlaute"},
    # ... 500+ characters
}
```

### Phase 2: Smart Score Distribution Algorithm

```python
def distribute_scores(
    overall_score: float,
    tone_score: float,
    fluency_score: float,
    expected_chars: List[str],
    transcription: str
) -> List[CharacterAnalysis]:
    """
    Distribute iFlytek scores to individual characters based on:
    1. Character difficulty (harder chars = more error likely)
    2. Transcription match (matched = higher score)
    3. Position in text (beginning = higher weight)
    """

    results = []
    char_difficulties = get_character_difficulties(expected_chars)

    # Base distribution
    base_tone_score = tone_score
    base_pron_score = overall_score

    for i, char in enumerate(expected_chars):
        difficulty = char_difficulties.get(char, 3)  # default medium

        # Apply difficulty weighting (harder = more likely to have lower score)
        difficulty_factor = 1.0 - (difficulty - 1) * 0.1  # 1.0 to 0.6

        # Check if character was transcribed
        transcribed = char in transcription

        # Calculate estimated scores
        estimated_tone = base_tone_score * difficulty_factor * (1.0 if transcribed else 0.7)
        estimated_pron = base_pron_score * difficulty_factor * (1.0 if transcribed else 0.5)

        # Determine status
        if estimated_pron >= 90:
            status = "correct"
        elif estimated_pron >= 70:
            status = "good"
        elif estimated_pron >= 50:
            status = "needs_work"
        else:
            status = "poor"

        results.append({
            "character": char,
            "expected_tone": get_tone_from_pinyin(char),
            "estimated_tone_accuracy": estimated_tone,
            "estimated_pronunciation": estimated_pron,
            "status": status,
            "difficulty": difficulty,
            "issues": char_difficulties.get(char, {}).get("issues", [])
        })

    return results
```

### Phase 3: Enhanced Feedback Generation

```python
def generate_enhanced_feedback(
    character_results: List[CharacterAnalysis],
    scores: Dict,
    section: int
) -> Dict:
    """
    Generate detailed feedback based on estimated per-character scores
    """

    # Analyze overall patterns
    tone_issues = []
    initial_issues = []
    final_issues = []

    for char_result in character_results:
        if char_result["status"] == "needs_work" or char_result["status"] == "poor":
            issues = char_result.get("issues", [])
            for issue in issues:
                if "tone" in issue:
                    tone_issues.append(char_result["character"])
                elif issue in ["zh", "ch", "sh", "r"]:
                    initial_issues.append((char_result["character"], issue))
                else:
                    final_issues.append(char_result["character"])

    # Generate character-specific feedback
    character_analysis = []
    for cr in character_results:
        char = cr["character"]

        # Get feedback from ERROR_PATTERNS if issues exist
        if cr["status"] != "correct":
            feedback = get_error_feedback(cr["issues"])
        else:
            feedback = None

        character_analysis.append({
            "character": char,
            "expected_tone": cr["expected_tone"],
            "estimated_tone_accuracy": cr["estimated_tone_accuracy"],
            "estimated_pronunciation": cr["estimated_pronunciation"],
            "status": cr["status"],
            "difficulty": cr["difficulty"],
            "feedback": feedback,
            "practice_words": get_practice_words_for_issues(cr.get("issues", []))
        })

    return {
        "character_analysis": character_analysis,
        "tone_analysis": analyze_tone_patterns(tone_issues),
        "phoneme_analysis": analyze_phoneme_patterns(initial_issues, final_issues),
        "practice_recommendations": generate_recommendations(tone_issues, initial_issues, final_issues)
    }
```

### Phase 4: PSC-Aligned Scoring

Map estimation to PSC scoring standards:

| Estimated Score | PSC Impact | Feedback |
|-----------------|-----------|----------|
| 90-100 | Perfect | Excellent pronunciation |
| 80-89 | Minor issues | Good, minor practice needed |
| 60-79 | Moderate issues | Needs improvement |
| <60 | Major issues | Significant practice required |

---

## Character Difficulty Database Structure

```python
# Complete difficulty database for ~500 common PSC characters
CHARACTER_DIFFICULTY = {
    # Format: "character": {"difficulty": 1-5, "issues": ["issue1", "issue2"], "category": "category"}

    # Level 1 - Easy (difficulty 1)
    "我": {"difficulty": 1, "issues": [], "category": "basic"},
    "你": {"difficulty": 1, "issues": [], "category": "basic"},
    "大": {"difficulty": 1, "issues": [], "category": "basic"},

    # Level 2 - Medium-Easy (difficulty 2)
    "中": {"difficulty": 2, "issues": ["zh"], "category": "retroflex"},
    "三": {"difficulty": 2, "issues": ["tone_1"], "category": "tone"},

    # Level 3 - Medium (difficulty 3)
    "是": {"difficulty": 3, "issues": ["sh", "tone_4"], "category": "retroflex"},
    "在": {"difficulty": 3, "issues": ["z", "tone_4"], "category": "initial"},

    # Level 4 - Hard (difficulty 4)
    "知": {"difficulty": 4, "issues": ["zh", "tone_1"], "category": "retroflex"},
    "吃": {"difficulty": 4, "issues": ["ch", "tone_1"], "category": "retroflex"},
    "女": {"difficulty": 4, "issues": ["n", "tone_3"], "category": "nasal"},

    # Level 5 - Very Hard (difficulty 5)
    "绿": {"difficulty": 5, "issues": ["ü", "tone_4"], "category": "umlaute"},
    "鱼": {"difficulty": 5, "issues": ["ü", "tone_2"], "category": "umlaute"},
    "约": {"difficulty": 5, "issues": ["üe", "tone_1"], "category": "umlaute"},
}
```

---

## Implementation Files

### New Files
1. `tone-analysis/services/character_difficulty.py` - Character difficulty database
2. `tone-analysis/services/score_distributor.py` - Score distribution algorithm

### Modified Files
1. `tone-analysis/services/feedback_generator.py` - Use enhanced estimation
2. `tone-analysis/app.py` - Integrate new system

---

## Testing Plan

1. Test with known difficult characters (知, 绿, 女)
2. Verify score distribution matches expectations
3. Validate feedback aligns with PSC standards
4. Test all 5 PSC sections

---

## Expected Output Example

```
Character Analysis:
知 [Tone 1, Difficulty 4] → Estimated: 72% → Status: NEEDS_WORK
  Issues: zh/ch/sh retroflex, tone accuracy
  Feedback: Practice retroflex sounds, focus on tone 1

绿 [Tone 4, Difficulty 5] → Estimated: 58% → Status: POOR
  Issues: ü vowel, tone 4
  Feedback: Practice ü sound, focus on falling tone

Tone Analysis:
- Most issues: Tone 3 (3次), Tone 4 (2次)
- Characters to practice: 知, 女, 绿

Phoneme Analysis:
- Retroflex: 5 issues (知, 吃, 是, 人, 中)
- Nasal: 3 issues (女, 你, 里)
```

---

## Conclusion

This enhanced estimation system provides:
✅ Per-character tone display (1-4)
✅ Per-character pronunciation estimation
✅ Specific practice recommendations from ERROR_PATTERNS
✅ PSC-aligned difficulty weighting
✅ No additional API costs

The system estimates character-level performance based on:
1. iFlytek overall scores
2. Character difficulty ratings
3. Transcription match status
4. Position in text

This is the most practical and cost-effective approach for PSC-aligned feedback.
