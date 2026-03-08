# PSC-Aligned Pronunciation Feedback System - Implementation Plan

## Executive Summary

This plan outlines enhancements to your existing BDG audio analysis system to provide detailed, PSC-aligned pronunciation feedback. The system will identify and categorize specific pronunciation errors including consonant (声母) errors, phonetic/phoneme (韵母) errors, tone errors, and other common pronunciation issues.

---

## Current System Analysis

### Existing Components
| Component | Status | Notes |
|-----------|--------|-------|
| Audio Recording | ✅ Working | MediaRecorder API with waveform |
| Audio Upload | ✅ Working | S3 storage |
| Tone Analysis | ✅ Basic | Pitch-based detection (librosa/pyin) |
| iFlytek ISE | ✅ Working | Pronunciation scoring |
| AI Feedback | ✅ Basic | OpenRouter-powered feedback |
| PSC Scoring | ✅ Working | Section 1-5 scoring formulas |

### Gap Analysis
The current system provides:
- Overall pronunciation score
- Tone accuracy percentage
- Fluency score
- Generic AI feedback

**Missing:**
- Per-character error classification
- Specific consonant/phoneme error identification
- Detailed tone error analysis (which tone, expected vs actual)
- Error severity categorization (error vs defect per PSC standards)
- Specific improvement suggestions per error type

---

## PSC Testing Requirements Alignment

### PSC Error Categories (普通话水平测试)
| Category | Description | PSC Impact |
|----------|-------------|------------|
| 读错 (Misread) | Completely wrong pronunciation | -0.1 per character |
| 漏读 (Omission) | Missing character | -0.1 per character |
| 添加 (Addition) | Extra character added | -0.1 per character |
| 缺陷 (Defect) | Partial error, understandable | -0.05 per instance |
| 声调错误 (Tone Error) | Wrong tone | Graded by severity |
| 声母错误 (Initial Error) | Wrong consonant | Error level |
| 韵母错误 (Final Error) | Wrong vowel/final | Error level |

---

## Phase 1: Enhanced Phonetic Analysis Engine

### 1.1 Expand Pinyin Database
**Priority: HIGH**

Create comprehensive phoneme mapping:

```
/backend/tone-analysis/services/phoneme_db.py (NEW)
```

**Key additions:**
- Complete initial (声母) mapping with IPA equivalents
- Complete final (韵母) mapping with IPA equivalents
- Common error patterns for Cantonese speakers
- Common error patterns for other L1 backgrounds
- Phoneme similarity scoring

```python
# Example structure
INITIAL_ERROR_PATTERNS = {
    # Cantonese speaker common errors
    "zh": {"confused_with": "z", "ipa": "ʈʂ", "difficulty": "high"},
    "ch": {"confused_with": "c", "ipa": "ʈʂʰ", "difficulty": "high"},
    "sh": {"confused_with": "s", "ipa": "ʂ", "difficulty": "high"},
    "r":  {"confused_with": "y", "ipa": "ɻ", "difficulty": "medium"},
    # Dental vs retroflex
    "n":  {"confused_with": "l", "ipa": "n", "difficulty": "medium"},
    "l":  {"confused_with": "n", "ipa": "l", "difficulty": "medium"},
}

FINAL_ERROR_PATTERNS = {
    # Nasal final confusions
    "an":  {"confused_with": "ang", "ipa": "an", "difficulty": "medium"},
    "en":  {"confused_with": "eng", "ipa": "ən", "difficulty": "medium"},
    "in":  {"confused_with": "ing", "ipa": "in", "difficulty": "medium"},
    "un":  {"confused_with": "ong", "ipa": "un", "difficulty": "high"},
    "ün":  {"confused_with": "iong", "ipa": "yn", "difficulty": "high"},
    # Front/back vowel issues
    "i":   {"confused_with": "ü", "ipa": "i", "difficulty": "medium"},
    "ü":   {"confused_with": "i", "ipa": "y", "difficulty": "medium"},
}
```

### 1.2 Enhanced Tone Analyzer
**Priority: HIGH**

Expand `/backend/tone-analysis/services/tone_analyzer.py`:

```python
class EnhancedToneAnalyzer:
    def detect_tone_errors(self, audio_path: str, expected_text: str) -> List[ToneError]:
        """
        Returns detailed tone errors:
        - Character position
        - Expected tone vs detected tone
        - Confidence score
        - Error severity (error/defect)
        """

    def analyze_tone_contour(self, pitch_contour: np.array) -> Dict:
        """Analyze if tone matches expected contour pattern"""

    def detect_tone_3_dipping(self, pitch_data: np.array) -> bool:
        """Special detection for tone 3 (214 contour)"""

    def detect_neutral_tone(self, audio_segment: np.array) -> bool:
        """Detect if character should be neutral tone"""
```

**Tone Detection Parameters:**
| Tone | Target F0 Range | Contour Pattern | Duration |
|------|-----------------|-----------------|----------|
| 1 (高平) | 300-350 Hz | Flat | 250-500ms |
| 2 (上升) | 200-350 Hz | Rising | 250-500ms |
| 3 (降升) | 350-200-350 Hz | Dip-Rise | 250-500ms |
| 4 (降) | 350-150 Hz | Falling | 150-350ms |
| 0 (轻声) | 150-250 Hz | Flat/Variable | <200ms |

### 1.3 Phonetic Error Detector
**Priority: HIGH**

Create `/backend/tone-analysis/services/phoneme_detector.py (NEW)`:

```python
class PhonemeDetector:
    """Detect consonant and phoneme errors"""

    def detect_initial_errors(self, audio_segment: np.array, expected: str) -> InitialError:
        """Detect initial (声母) errors"""
        # Use acoustic features:
        # - Voice onset time (VOT)
        # - Place of articulation
        # - Manner of articulation
        # - Aspiration differences

    def detect_final_errors(self, audio_segment: np.array, expected: str) -> FinalError:
        """Detect final (韵母) errors"""
        # Use formant analysis:
        # - F1 (openness)
        # - F2 (frontness)
        # - F3 (rhoticity)
        # - Duration

    def classify_error_severity(self, phoneme_match: float) -> str:
        """Classify as 'error' or 'defect' per PSC standards"""
```

---

## Phase 2: Detailed Error Classification System

### 2.1 Error Type Taxonomy
**Priority: HIGH**

Create comprehensive error categorization:

```typescript
// /frontend/src/types/pronunciation-errors.ts

export type ErrorCategory =
  | 'initial_error'      // 声母错误
  | 'final_error'        // 韵母错误
  | 'tone_error'         // 声调错误
  | 'neutral_tone_error' // 轻声错误
  | 'stress_error'       // 重音错误
  | 'rhythm_error'       // 节奏错误
  | 'pause_error'        // 停顿错误
  | 'fluency_error';     // 流利度错误

export interface PronunciationError {
  character: string;
  position: number;
  category: ErrorCategory;
  expected: string;        // What they should have said
  actual: string;          // What they actually said
  error_type: 'error' | 'defect';  // PSC classification
  confidence: number;       // Detection confidence 0-1
  suggestion: string;      // How to fix
  psc_impact: number;     // Score deduction
}
```

### 2.2 Error Impact Calculator
**Priority: HIGH**

Update `/backend/src/services/scoring/pscScoring.ts`:

```typescript
function calculateErrorImpact(errors: PronunciationError[]): ScoreBreakdown {
  // Map specific errors to PSC scoring formula
  return {
    initial_errors: {
      count: errors.filter(e => e.category === 'initial_error').length,
      deduction: errors.filter(e => e.category === 'initial_error').length * 0.1
    },
    final_errors: {
      count: errors.filter(e => e.category === 'final_error').length,
      deduction: errors.filter(e => e.category === 'final_error').length * 0.1
    },
    tone_errors: {
      count: errors.filter(e => e.category === 'tone_error').length,
      // Tone errors have variable impact based on severity
      deduction: calculateToneErrorDeduction(errors.filter(e => e.category === 'tone_error'))
    },
    // ... etc
  };
}
```

---

## Phase 3: Intelligent Feedback Generation

### 3.1 Rule-Based Error Feedback
**Priority: MEDIUM**

Create feedback rules in `/backend/tone-analysis/services/error_feedback.py`:

```python
ERROR_FEEDBACK_RULES = {
    "zh→z": {
        "en": "Your retroflex 'zh' sounds like flat 'z'. Curl your tongue tip back.",
        "zh": "您的翘舌音zh听起来像平舌音z。卷起舌尖向后。",
        "tip": "Practice: zh-zh-zh, z-z-z"
    },
    "ch→c": {
        "en": "Your aspirated 'ch' needs more aspiration. Push more air.",
        "zh": "您的送气音ch需要更多送气。向外推气。",
        "tip": "Practice: ch-ch-ch with strong aspiration"
    },
    "an→ang": {
        "en": "You're using a nasal ending. Keep the 'a' pure before 'n'.",
        "zh": "您加了鼻音。在n之前保持纯粹的a。",
        "tip": "Practice: an-an-an, keep tongue flat"
    },
    "2→3": {
        "en": "Tone 2 should rise from mid to high (like asking 'what?').",
        "zh": "声调2应从中调升到高调（像问"什么？"）。",
        "tip": "Practice: má (what?)"
    },
    # ... comprehensive rule database
}
```

### 3.2 Enhanced AI Feedback Prompt
**Priority: MEDIUM**

Enhance the AI prompt in `/backend/tone-analysis/services/ai_feedback.py`:

```python
# New prompt structure with detailed error breakdown
ENHANCED_PROMPT = """
You are a PSC (Putonghua Shuiping Ceshi) pronunciation expert.

## Assessment Details
- Section: {section}
- Expected: {expected_text}
- Actual: {transcription}

## Detailed Error Analysis
{error_breakdown_json}

## Per-Character Analysis Required
For EACH character with error, provide:
1. Character: [char]
2. Expected Pinyin: [pinyin with tone]
3. Your Pinyin: [detected pinyin]
4. Error Category: [initial/final/tone/neutral/stress/rhythm]
5. Specific Issue: [what went wrong]
6. How to Fix: [specific technique]
7. Practice Words: [3 example words to practice this sound]

## PSC Alignment
Your feedback must align with PSC scoring:
- 声母错误 (Initial errors): Major impact
- 韵母错误 (Final errors): Major impact
- 声调错误 (Tone errors): Critical impact
- 缺陷 (Defects): Minor impact but still affects score

Output in JSON format:
{{
    "overall_assessment_en": "...",
    "overall_assessment_zh": "...",
    "character_analysis": [
        {{
            "character": "...",
            "position": 0,
            "expected_pinyin": "...",
            "actual_pinyin": "...",
            "error_category": "...",
            "error_description_en": "...",
            "error_description_zh": "...",
            "how_to_fix_en": "...",
            "how_to_fix_zh": "...",
            "practice_words": ["...", "...", "..."],
            "psc_impact": "error/defect"
        }}
    ],
    "error_summary": {{
        "total_errors": 0,
        "initial_errors": 0,
        "final_errors": 0,
        "tone_errors": 0,
        "neutral_errors": 0,
        "defects": 0
    }},
    "practice_recommendations": {{
        "focus_areas": ["..."],
        "daily_exercises": ["..."]
    }}
}}
"""
```

---

## Phase 4: Frontend Visualization

### 4.1 Error Display Component
**Priority: MEDIUM**

Create `/frontend/src/components/PronunciationFeedback.tsx`:

```tsx
interface Props {
  errors: PronunciationError[];
  expectedText: string;
  transcription: string;
}

export const PronunciationFeedback: React.FC<Props> = ({ errors, expectedText, transcription }) => {
  // Display with color coding:
  // 🔴 Red: Error (major impact)
  // 🟡 Yellow: Defect (minor impact)
  // 🟢 Green: Correct

  return (
    <div className="feedback-container">
      <CharacterDisplay
        text={expectedText}
        errors={errors}
        transcription={transcription}
      />

      <ErrorBreakdownPanel errors={errors} />

      <PracticeSuggestions errors={errors} />
    </div>
  );
};
```

### 4.2 Visual Feedback Design

```
Expected: 春天来了
Transcription: 春田来了

Character Analysis:
┌─────────┬──────────┬──────────┬────────────┬──────────────┐
│ Character│ Expected │ Actual   │ Error Type │ Fix          │
├─────────┼──────────┼──────────┼────────────┼──────────────┤
│ 春      │ chūn     │ chūn    │ ✅ Correct │              │
│ 天      │ tiān     │ tián    │ ⚠️ Tone    │ Should be 1st │
│         │          │          │            │ tone, not 2nd│
│ 来了    │ lái le   │ lái le  │ ✅ Correct │              │
└─────────┴──────────┴──────────┴────────────┴──────────────┘

Error Summary:
• 声母错误 (Initial): 0
• 韵母错误 (Final): 0
• 声调错误 (Tone): 1
• 轻声错误 (Neutral): 0
• 缺陷 (Defects): 0

Practice Focus: 声调练习 - Tone 1 (高平)
```

---

## Phase 5: PSC Section-Specific Analysis

### 5.1 Section-Specific Feedback

| PSC Section | Focus | Error Detection |
|-------------|-------|-----------------|
| Section 1 | Single characters | Individual tone + phoneme |
| Section 2 | Polysyllabic words | Tone sandhi, compound tones |
| Section 3 | Choice/Judgment | Listening comprehension |
| Section 4 | Reading passage | Fluency, pause, rhythm, intonation |
| Section 5 | Speaking | Topic coherence, vocabulary, fluency |

### 5.2 Tone Sandhi Detection
**Priority: MEDIUM**

Add tone sandhi rules for Section 2:

```python
TONE_SANDHI_RULES = {
    # 不 (bù) tone change
    ("不", "不"): ("bù", "bù"),  # 不 + 不 = bù bù
    ("不", None): ("bù", "bù"),   # standalone 不

    # 一 (yī) tone change
    ("一", "一"): ("yī", "yì"),   # 一 + 一 = yī yì
    ("一", "不"): ("yī", "bù"),   # 一 + 不 = yī bù

    # Third tone transformation
    ("马", "马"): ("mǎ", "má"),   # 3+3 → 2+3
}
```

---

## Implementation Roadmap

### Phase 1 (Week 1-2): Core Analysis Engine
- [ ] Expand phoneme database with error patterns
- [ ] Implement enhanced tone analyzer
- [ ] Add phonetic error detection
- [ ] Create error classification system

### Phase 2 (Week 3): Scoring Integration
- [ ] Update PSC scoring with detailed breakdowns
- [ ] Implement error impact calculator
- [ ] Add section-specific scoring

### Phase 3 (Week 4): Feedback System
- [ ] Create rule-based error feedback database
- [ ] Enhance AI prompts
- [ ] Add bilingual feedback generation

### Phase 4 (Week 5-6): Frontend
- [ ] Build PronunciationFeedback component
- [ ] Add character-by-character display
- [ ] Create error breakdown visualization
- [ ] Add practice suggestion panel

### Phase 5 (Week 7-8): Testing & Refinement
- [ ] Test with native Mandarin speakers
- [ ] Validate against PSC scoring
- [ ] Refine error detection accuracy
- [ ] Add more error patterns

---

## Technical Dependencies

### New Python Packages
```
# requirements.txt additions
librosa>=0.10.0      # Audio analysis
praat-parselmouth>=0.4.0  # Advanced pitch analysis
scipy>=1.11.0        # Signal processing
soundfile>=0.12.0    # Audio I/O
```

### Frontend Dependencies
```
# package.json additions
@types/d3>=7.0.0     # Data visualization
react-syntax-highlighter>=15.0  # Code display
```

---

## File Structure Changes

```
BDG_backend/
├── tone-analysis/
│   ├── services/
│   │   ├── phoneme_db.py          (NEW) - Comprehensive phoneme mapping
│   │   ├── tone_analyzer.py       (UPDATE) - Enhanced tone detection
│   │   ├── phoneme_detector.py    (NEW) - Initial/final error detection
│   │   ├── error_feedback.py     (NEW) - Rule-based feedback
│   │   ├── ai_feedback.py         (UPDATE) - Enhanced prompts
│   │   └── scorer.py               (UPDATE) - Detailed scoring
│   └── app.py                     (UPDATE) - New endpoints

BDG_backend/src/
├── services/
│   └── scoring/
│       └── pscScoring.ts          (UPDATE) - Enhanced breakdown
└── routes/
    └── audio.ts                   (UPDATE) - New response format

BDG_frontend/src/
├── components/
│   ├── PronunciationFeedback.tsx  (NEW)
│   ├── CharacterDisplay.tsx       (NEW)
│   ├── ErrorBreakdown.tsx         (NEW)
│   └── PracticeSuggestions.tsx    (NEW)
├── hooks/
│   └── usePronunciationAnalysis.ts (NEW)
├── services/
│   └── api.ts                     (UPDATE)
└── types/
    └── pronunciation-errors.ts    (NEW)
```

---

## API Response Format (Updated)

```json
{
  "success": true,
  "data": {
    "transcription": "春田来了",
    "expected": "春天来了",
    "scores": {
      "overall": 85.5,
      "pronunciation": 88,
      "tone": 80,
      "fluency": 90,
      "psc_level": "2B"
    },
    "errors": [
      {
        "character": "天",
        "position": 1,
        "category": "tone_error",
        "expected_pinyin": "tiān",
        "actual_pinyin": "tián",
        "error_type": "error",
        "confidence": 0.92,
        "expected_tone": 1,
        "actual_tone": 2,
        "psc_impact": 0.1
      }
    ],
    "character_analysis": [
      {"character": "春", "status": "correct", "pinyin": "chūn", "tone": 1},
      {"character": "天", "status": "error", "pinyin": "tián", "tone": 2, "expected_tone": 1},
      {"character": "来", "status": "correct", "pinyin": "lái", "tone": 2},
      {"character": "了", "status": "correct", "pinyin": "le", "tone": 0}
    ],
    "feedback": {
      "overall_assessment_en": "Good effort! One tone error detected.",
      "overall_assessment_zh": "不错！检测到一个声调错误。",
      "key_issues": [
        "Tone 1 pronounced as Tone 2 in '天'"
      ],
      "how_to_fix": {
        "en": "Tone 1 (高平) should be flat and high. Practice: mā mā mā",
        "zh": "声调1（高平）应该是平坦且高音。练习：妈妈妈"
      },
      "practice_words": ["春天", "天空", "天才"]
    },
    "error_summary": {
      "total_errors": 1,
      "initial_errors": 0,
      "final_errors": 0,
      "tone_errors": 1,
      "neutral_errors": 0,
      "defects": 0
    }
  }
}
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Error detection accuracy | >85% |
| Tone detection accuracy | >90% |
| Feedback relevance | >80% user satisfaction |
| PSC scoring alignment | >95% match with official scoring |
| Response time | <5 seconds |

---

## Recommendations

### Priority 1 (Must Have)
1. **Enhanced phoneme database** - Foundation for all error detection
2. **Detailed error classification** - Core value proposition
3. **Per-character feedback display** - User-facing impact

### Priority 2 (Should Have)
1. **Tone sandhi detection** - Critical for Section 2
2. **Section-specific analysis** - PSC alignment
3. **Bilingual feedback** - User experience

### Priority 3 (Nice to Have)
1. **Visual pitch contour** - Advanced visualization
2. **Practice exercise generation** - Gamification
3. **Progress tracking** - Long-term engagement

---

## Notes

- The system should distinguish between **errors** (completely wrong) and **defects** (partially wrong but understandable) per PSC standards
- Cantonese speakers will have different error patterns - consider adding L1 detection
- The iFlytek API already provides some of this data - first integrate with their detailed response, then enhance with custom analysis
- Test extensively with native speakers to validate error detection accuracy

