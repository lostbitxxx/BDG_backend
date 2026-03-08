# PSC-Aligned Pronunciation Feedback - OPTIMIZED PLAN

## The Real Situation

| Component | Current Status | What It Actually Does |
|-----------|---------------|----------------------|
| iFlytek ISE | ⚠️ Not fully integrated | Returns placeholder scores |
| ElevenLabs | ✅ Works | Basic text transcription |
| Tone Analyzer | ⚠️ Basic | Pitch detection only |
| AI Feedback | ✅ Working | Main intelligence layer |

**Key Insight**: Your AI feedback system is already doing the heavy lifting. The goal should be to **enhance the data going INTO it** and **improve how you display the output**.

---

## Recommended Approach: 3-Phase Implementation

### Phase 1: Fix iFlytek Integration (Week 1)
**Priority: CRITICAL**

The iFlytek ISE API actually provides detailed per-syllable feedback:
- Per-character pronunciation scores
- Tone assessments (correct/wrong)
- Fluency metrics
- Detailed XML/JSON response

**Action**: Fix the iFlytek integration to get real data:

```python
# Current: Returns placeholder
# Fix: Actually parse iFlytek's detailed response
# Expected response structure from iFlytek:
{
    "read_chapter": {
        "sentence": [...],
        "word": [...],
        "phoneme": [...],  # Per-phoneme feedback!
    }
}
```

**Files to update**:
- [iflytek_evaluator.py](BDG_backend/tone-analysis/services/iflytek_evaluator.py)

---

### Phase 2: Smart Error Mapping (Week 1-2)
**Priority: HIGH**

Instead of building complex DSP, build a practical error mapping system:

```python
# /backend/tone-analysis/services/error_mapper.py

class ErrorMapper:
    """Map transcription differences to actionable feedback"""

    def map_errors(self, expected: str, actual: str, iflytek_data: dict) -> List[PronunciationError]:
        """
        Combine:
        1. Character mismatch (from transcription)
        2. Per-syllable scores (from iFlytek)
        3. Tone analysis (from tone analyzer)
        """
```

**Key database** - expand [pinyin_db.py](BDG_backend/tone-analysis/services/pinyin_db.py):

```python
# Add error pattern mappings
ERROR_PATTERNS = {
    # (expected, actual) -> feedback
    ("春", "村"): {
        "category": "initial_error",
        "expected": "ch",
        "actual": "c",
        "feedback_en": "The 'ch' sound needs more aspiration. It's not 'c'.",
        "feedback_zh": "ch音需要更多送气，不是c音。",
        "fix_tip": "Practice: ch-ch-ch with strong airflow"
    },
    ("天", "田"): {
        "category": "tone_error",
        "expected_tone": 1,
        "actual_tone": 2,
        "feedback_en": "This should be Tone 1 (high flat), not Tone 2 (rising).",
        "feedback_zh": "应该是第一声（高平），不是第二声（上升）。",
        "fix_tip": "Practice: tiān (flat high) vs tián (rising)"
    },
    # ... 50+ common patterns
}
```

---

### Phase 3: Enhanced AI Prompt Engineering (Week 2)
**Priority: HIGH**

Your existing AI feedback is good. Make it better by providing structured input:

```python
# Update ai_feedback.py prompt

ENHANCED_PROMPT = """
You are a PSC pronunciation expert. Analyze this:

## Expected Text
{expected}

## What User Said
{transcription}

## iFlytek Per-Syllable Scores (if available)
{iflytek_scores}

## Tone Analysis
{tone_analysis}

## Your Task
For EACH character with issues, provide:
1. Character + position
2. Error type: [initial_error/final_error/tone_error/stress_error]
3. What they said vs what they should say
4. Specific fix in English + Chinese
5. One practice word

Format as JSON with "character_analysis" array.
"""
```

---

### Phase 4: Frontend Visualization (Week 2-3)
**Priority: MEDIUM**

Build the display components:

```
┌─────────────────────────────────────────────────┐
│  Expected: 春天来了                           │
│  You said:  春田来了                          │
├─────────────────────────────────────────────────┤
│  Character Analysis:                           │
│  ┌─────┬───────┬───────┬──────────┐          │
│  │ 字  │ 期望  │ 实际  │  问题     │          │
│  ├─────┼───────┼───────┼──────────┤          │
│  │ 春  │ chūn  │ chūn  │ ✅ 正确   │          │
│  │ 天  │ tiān  │ tián  │ 🔴 声调   │ ← 第1声  │
│  │ 来  │ lái   │ lái   │ ✅ 正确   │   → 第2声│
│  │ 了  │ le    │ le    │ ✅ 正确   │          │
│  └─────┴───────┴───────┴──────────┘          │
├─────────────────────────────────────────────────┤
│  Error Summary:                                 │
│  • 声母错误: 0  • 韵母错误: 0  • 声调错误: 1   │
├─────────────────────────────────────────────────┤
│  How to Fix "天":                               │
│  English: Tone 1 is flat high. Say "mā-mā-mā"  │
│  中文: 第一声要高平。说"妈妈妈"                 │
│                                                 │
│  Practice: 春天·天空·天才                       │
└─────────────────────────────────────────────────┘
```

---

## Why This Is Better

| Aspect | Original Plan | Optimized Plan |
|--------|--------------|----------------|
| Technical complexity | High (custom DSP) | Low (use existing APIs) |
| Timeline | 8 weeks | 3 weeks |
| Accuracy | Uncertain | Leverages iFlytek's trained models |
| Maintainability | Hard | Simple rule-based + AI |
| PSC alignment | Theoretical | iFlytek IS PSC-aligned |

---

## Implementation Priority Order

1. **Fix iFlytek** - Get real per-character data (most impactful)
2. **Build error mapper** - Map errors to feedback rules
3. **Enhance AI prompts** - Better structured input/output
4. **Build frontend** - Visual feedback display

---

## Quick Wins First

### Immediate improvements (no code needed):
1. **Improve the AI prompt** - Already exists, just needs better structured input
2. **Add more error patterns to pinyin_db.py** - Just data entry

### Files to create/modify:

```
NEW:
- /backend/tone-analysis/services/error_mapper.py

UPDATE:
- /backend/tone-analysis/services/iflytek_evaluator.py  (fix integration)
- /backend/tone-analysis/services/ai_feedback.py         (enhance prompts)
- /backend/tone-analysis/services/pinyin_db.py           (add error patterns)

NEW FRONTEND:
- /frontend/src/components/PronunciationFeedback.tsx
- /frontend/src/components/CharacterAnalysisCard.tsx
```

---

## Expected Results

After Phase 1-3:
- ✅ Per-character error classification
- ✅ Specific consonant/phoneme error identification
- ✅ Detailed tone error (expected vs actual)
- ✅ Actionable bilingual feedback
- ✅ PSC-aligned scoring breakdown

**Timeline: 3 weeks** instead of 8

---

## Note on iFlytek

iFlytek ISE (Intelligent Speech Evaluation) IS designed for PSC-style assessment. If properly integrated, it provides:
- Per-syllable scores (0-100)
- Tone correctness per syllable
- Fluency metrics
- The only issue is your current code doesn't parse the detailed response

Would you like me to start implementing Phase 1 - fixing the iFlytek integration to get real per-character data?
