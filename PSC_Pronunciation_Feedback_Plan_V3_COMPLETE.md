# PSC-Aligned Pronunciation Feedback System - COMPLETE IMPLEMENTATION PLAN

## Executive Summary

This document outlines a complete, production-ready system for providing detailed PSC (Putonghua Shuiping Ceshi) pronunciation feedback. The system aligns 100% with official PSC testing requirements and provides character-level error analysis with actionable improvement suggestions.

---

# PART 1: PSC TESTING REQUIREMENTS ANALYSIS

## 1.1 PSC Test Structure (普通话水平测试)

| Section | Name | Duration | Max Score | Content |
|---------|------|----------|-----------|---------|
| Section 1 | 读单音节字词 | 3.5 min | 10 points | 100 single characters |
| Section 2 | 读多音节词语 | 2.5 min | 20 points | 50 polysyllabic words |
| Section 3 | 判断选择 | 3 min | 10 points | 30 questions |
| Section 4 | 朗读短文 | 4 min | 30 points | 1 passage (400 chars) |
| Section 5 | 命题说话 | 3 min | 30 points | 1 topic (40+ seconds) |
| **Total** | | ~16 min | **100 points** | |

## 1.2 PSC Scoring Criteria

### Error Types (错误类型)

| Type | Chinese | Description | Deduction |
|------|---------|-------------|-----------|
| Phonetic Error | 读错 | Completely wrong pronunciation | -0.1 per instance |
| Omission | 漏读 | Missing character | -0.1 per instance |
| Addition | 添加 | Extra character | -0.1 per instance |
| Defect | 缺陷 | Partial error, still understandable | -0.05 per instance |

### Tone Error Severity

| Severity | Chinese | Description | Impact |
|----------|---------|-------------|--------|
| Critical | 严重错误 | Completely wrong tone | Error level |
| Moderate | 明显缺陷 | Partially wrong tone | Defect level |
| Minor | 轻微缺陷 | Slight tone issue | Minor deduction |

### Level Determination (等级评定)

| Total Score | Level | Grade |
|-------------|-------|-------|
| 97-100 | 一级 | A |
| 92-96.9 | 一级 | B |
| 87-91.9 | 二级 | A |
| 80-86.9 | 二级 | B |
| 70-79.9 | 三级 | A |
| 60-69.9 | 三级 | B |
| <60 | Below Level 3 | C |

## 1.3 Pronunciation Components to Analyze

| Category | Components | PSC Relevance |
|----------|------------|---------------|
| **Initial (声母)** | 21 initials: b, p, m, f, d, t, n, l, g, k, h, j, q, x, zh, ch, sh, r, z, c, s | High - common errors |
| **Final (韵母)** | 39 finals: a, o, e, i, u, ü, ai, ei, ao, ou, an, en, in, un, ang, eng, ing, ong, etc. | High - common errors |
| **Tone (声调)** | 1(高平), 2(上升), 3(降升), 4(降), 0(轻声) | Critical - highest impact |
| **Tone Sandhi (变调)** | 不/一/第三声连读 | Medium - Section 2 |
| **Stress (重音)** | Word-level emphasis | Medium - Section 4/5 |
| **Rhythm (节奏)** | Speaking pace and flow | Medium - Section 4/5 |
| **Pausing (停顿)** | Appropriate breaks | Low-Medium |
| **Intonation (语调)** | Sentence-level melody | Low - Section 4/5 |

---

# PART 2: SYSTEM ARCHITECTURE

## 2.1 Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AUDIO INPUT PROCESSING                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │   Web/Mobile│───▶│   S3 Upload │───▶│   FFmpeg    │                │
│  │   Recorder  │    │   Storage   │    │   Convert   │                │
│  └─────────────┘    └─────────────┘    │  (16kHz PCM) │                │
│                                        └─────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        ANALYSIS ENGINE (Python)                        │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │  Whisper/Fast│───▶│    iFlytek │───▶│   Custom    │                │
│  │  Whisper     │    │   ISE API   │    │ Tone Analyzer│               │
│  │  (ASR)       │    │(Phoneme+    │    │  (Pitch)    │                │
│  │              │    │ Tone Score) │    │             │                │
│  └─────────────┘    └─────────────┘    └─────────────┘                │
│         │                   │                   │                     │
│         └───────────────────┼───────────────────┘                     │
│                             ▼                                         │
│                  ┌─────────────────────┐                               │
│                  │   Error Detection  │                               │
│                  │   & Classification │                               │
│                  └─────────────────────┘                               │
│                             │                                         │
│                             ▼                                         │
│                  ┌─────────────────────┐                               │
│                  │    AI Feedback      │                               │
│                  │    Generator       │                               │
│                  └─────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        SCORING ENGINE                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │   Section   │───▶│   Error     │───▶│   Level     │                │
│  │   Scorer    │    │   Calculator│    │   Determinator│              │
│  └─────────────┘    └─────────────┘    └─────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND DISPLAY                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                │
│  │  Character  │───▶│   Error     │───▶│   Practice  │                │
│  │  Display    │    │  Summary    │    │  Suggestion │                │
│  └─────────────┘    └─────────────┘    └─────────────┘                │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Data Models

### PronunciationError
```typescript
interface PronunciationError {
  id: string;
  character: string;
  position: number;

  // Error Classification
  category: ErrorCategory;
  subcategory: string;

  // What was expected vs what was said
  expected: {
    pinyin: string;
    tone: number;
    initial: string;
    final: string;
  };
  actual: {
    pinyin: string;
    tone: number;
    initial: string;
    final: string;
  };

  // PSC Classification
  severity: 'error' | 'defect' | 'minor_defect';
  psc_impact: number; // deduction in points

  // Source of detection
  detection_method: 'asr_mismatch' | 'iflytek' | 'tone_analyzer' | 'ai_analysis';
  confidence: number;

  // Feedback
  feedback: {
    en: string;
    zh: string;
    fix_tip_en: string;
    fix_tip_zh: string;
    practice_words: string[];
  };
}

type ErrorCategory =
  | 'initial_error'      // 声母错误
  | 'final_error'        // 韵母错误
  | 'tone_error'         // 声调错误
  | 'neutral_tone_error' // 轻声错误
  | 'tone_sandhi_error' // 变调错误
  | 'stress_error'       // 重音错误
  | 'rhythm_error'       // 节奏错误
  | 'pause_error'        // 停顿错误
  | 'omission'           // 漏读
  | 'addition';          // 添加
```

### AnalysisResult
```typescript
interface AnalysisResult {
  // Basic info
  id: string;
  timestamp: string;
  section: 1 | 2 | 3 | 4 | 5;

  // Texts
  expected_text: string;
  transcription: string;

  // Analysis
  character_results: CharacterResult[];
  errors: PronunciationError[];

  // Scores
  scores: {
    overall: number;
    pronunciation: number;
    tone: number;
    fluency: number;
    rhythm?: number;
    intonation?: number;
  };

  // PSC Results
  psc_level: string;
  psc_grade: string;
  total_score: number;
  max_score: number;

  // Feedback
  feedback: {
    overall_en: string;
    overall_zh: string;
    summary: {
      total_errors: number;
      total_defects: number;
      by_category: Record<ErrorCategory, number>;
    };
    practice_recommendations: PracticeRecommendation;
  };
}
```

---

# PART 3: COMPONENT SPECIFICATIONS

## 3.1 Audio Preprocessor

```python
# /backend/tone-analysis/services/audio_preprocessor.py

class AudioPreprocessor:
    """Prepare audio for analysis"""

    def process(self, audio_path: str) -> str:
        """Convert to 16kHz mono PCM"""
        # 1. Load audio (any format)
        # 2. Resample to 16kHz
        # 3. Convert to mono
        # 4. Normalize volume
        # 5. Apply noise reduction (optional)
        # 6. Save as PCM 16-bit
```

**Requirements:**
- Input: Any audio format (webm, mp3, wav, m4a)
- Output: PCM 16kHz mono
- Libraries: ffmpeg, pydub

## 3.2 ASR Service (Speech Recognition)

```python
# /backend/tone-analysis/services/asr_service.py

class ASRService:
    """Speech-to-text for Mandarin"""

    def recognize(self, audio_path: str) -> ASRResult:
        """Convert speech to text"""
```

**Options:**
1. **Faster Whisper** (Recommended - Free, local)
   - Model: base or small
   - Pros: Free, fast, runs locally
   - Cons: Not optimized for pronunciation scoring

2. **iFlytek ISE** (Recommended - PSC-aligned)
   - Provides phoneme-level scores
   - Pros: PSC-aligned, detailed feedback
   - Cons: Costs, complex API

3. **Google Cloud Speech-to-Text**
   - Pros: High accuracy
   - Cons: Costs, no tone info

**Recommendation:** Use Faster Whisper as primary ASR, use iFlytek for detailed scoring if budget allows.

## 3.3 Tone Analyzer

```python
# /backend/tone-analysis/services/tone_analyzer.py (ENHANCED)

class ToneAnalyzer:
    """Analyze Mandarin tones"""

    def analyze(self, audio_path: str, expected_text: str) -> ToneAnalysis:
        """Comprehensive tone analysis"""

    def extract_pitch_contour(self, audio_segment: np.array) -> np.array:
        """Extract F0 (fundamental frequency)"""

    def classify_tone(self, pitch_contour: np.array) -> ToneResult:
        """Classify tone based on contour"""

    def detect_tone_sandhi(self, text: str) -> List[ToneSandhi]:
        """Detect tone sandhi patterns"""
```

**Tone Detection Algorithm:**
1. Segment audio by character (using energy/VAD)
2. Extract pitch contour (pyin algorithm)
3. Classify based on:
   - Start pitch
   - End pitch
   - Contour shape (flat, rising, dipping, falling)
   - Duration
4. Compare with expected tones
5. Return error details

**Tone Patterns:**

| Tone | Name | Contour | F0 Range | Duration |
|------|------|---------|----------|----------|
| 1 | 高平 | Flat high | 280-360 Hz | 250-500ms |
| 2 | 上升 | Rising | 200→350 Hz | 250-500ms |
| 3 | 降升 | Dip-rising | 350→200→350 Hz | 250-500ms |
| 4 | 降 | Falling | 350→150 Hz | 150-350ms |
| 0 | 轻声 | Neutral | 150-250 Hz | <200ms |

## 3.4 Phoneme Analyzer

```python
# /backend/tone-analysis/services/phoneme_analyzer.py (NEW)

class PhonemeAnalyzer:
    """Analyze consonant and vowel sounds"""

    def analyze(self, audio_segment: np.array, expected_pinyin: str) -> PhonemeResult:
        """Analyze phoneme accuracy"""

    def extract_formants(self, audio_segment: np.array) -> Formants:
        """Extract F1, F2, F3 formants"""

    def detect_initial(self, audio_segment: np.array) -> InitialResult:
        """Detect initial consonant"""

    def detect_final(self, audio_segment: np.array) -> FinalResult:
        """Detect final (vowel/nasal)"""
```

**Acoustic Features:**

### Initial Detection (声母)
| Initial | Voicing | VOT | Place | Manner |
|---------|---------|-----|-------|--------|
| b | Voiceless | 0ms | Bilabial | Plosive |
| p | Voiced | +30ms | Bilabial | Plosive |
| d | Voiceless | 0ms | Alveolar | Plosive |
| t | Voiced | +30ms | Alveolar | Plosive |
| g | Voiceless | 0ms | Velar | Plosive |
| k | Voiced | +30ms | Velar | Plosive |
| zh | Voiceless | 0ms | Retroflex | Affricate |
| ch | Voiced | +30ms | Retroflex | Affricate |
| sh | N/A | N/A | Retroflex | Fricative |
| z | Voiceless | 0ms | Alveolar | Affricate |
| c | Voiced | +30ms | Alveolar | Affricate |
| s | N/A | N/A | Alveolar | Fricative |

### Final Detection (韵母)
Use formant frequencies (F1, F2) to classify:

| Final | F1 Range | F2 Range | Nasal? |
|-------|----------|----------|--------|
| a | 700-1000 | 1200-2000 | No |
| o | 400-600 | 700-1200 | No |
| e | 400-600 | 1200-2000 | No |
| i | 250-350 | 2000-2800 | No |
| u | 250-350 | 700-1200 | No |
| ü | 250-350 | 1500-2200 | No |
| an | 600-800 | 1200-1800 | Yes (-n) |
| ang | 600-800 | 1000-1600 | Yes (-ng) |
| en | 400-550 | 1200-1800 | Yes (-n) |
| eng | 400-550 | 1000-1600 | Yes (-ng) |
| in | 250-350 | 2000-2600 | Yes (-n) |
| ing | 250-350 | 1800-2400 | Yes (-ng) |

## 3.5 Error Detection Engine

```python
# /backend/tone-analysis/services/error_detector.py (NEW)

class ErrorDetector:
    """Detect and classify pronunciation errors"""

    def detect(self, expected: str, transcription: str,
               tone_analysis: ToneAnalysis,
               phoneme_analysis: PhonemeAnalysis) -> List[PronunciationError]:
        """Combine all analyses to detect errors"""

    def classify_severity(self, error: RawError) -> str:
        """Classify as error, defect, or minor_defect"""
```

**Error Detection Logic:**

1. **Character Mismatch Errors**
   - Compare expected vs transcribed text
   - Classify as: substitution, omission, addition

2. **Tone Errors**
   - Compare expected tone vs detected tone
   - Calculate confidence based on pitch contour match
   - Classify severity based on deviation

3. **Phoneme Errors**
   - Compare expected phoneme vs detected
   - Use acoustic distance (formants, VOT)
   - Map to common error patterns

4. **Fluency/Rhythm Errors**
   - Measure speaking rate (characters/second)
   - Detect unnatural pauses
   - Identify repeated words/sounds

## 3.6 Comprehensive Pinyin & Error Database

```python
# /backend/tone-analysis/services/pinyin_db.py (EXPANDED)

# Complete pinyin database
PINYIN_DATA = {
    "a": {"initial": None, "final": "a", "tone": None, "category": "simple_vowel"},
    "ba": {"initial": "b", "final": "a", "tone": None, "category": "initial_final"},
    # ... all 400+ pinyin combinations
}

# Initial (声母) database
INITIALS = {
    "b": {"name": "双唇音", "name_en": "Bilabial", "ipa": "p", "retroflex": False},
    "p": {"name": "双唇音", "name_en": "Bilabial", "ipa": "pʰ", "retroflex": False},
    "m": {"name": "双唇鼻音", "name_en": "Bilabial nasal", "ipa": "m", "retroflex": False},
    "f": {"name": "唇齿音", "name_en": "Labiodental", "ipa": "f", "retroflex": False},
    "d": {"name": "舌尖音", "name_en": "Alveolar", "ipa": "t", "retroflex": False},
    "t": {"name": "舌尖音", "name_en": "Alveolar", "ipa": "tʰ", "retroflex": False},
    "n": {"name": "舌尖鼻音", "name_en": "Alveolar nasal", "ipa": "n", "retroflex": False},
    "l": {"name": "舌尖边音", "name_en": "Alveolar lateral", "ipa": "l", "retroflex": False},
    "g": {"name": "舌根音", "name_en": "Velar", "ipa": "k", "retroflex": False},
    "k": {"name": "舌根音", "name_en": "Velar", "ipa": "kʰ", "retroflex": False},
    "h": {"name": "舌根擦音", "name_en": "Velar fricative", "ipa": "x", "retroflex": False},
    "j": {"name": "舌面音", "name_en": "Palatal", "ipa": "tɕ", "retroflex": False},
    "q": {"name": "舌面音", "name_en": "Palatal", "ipa": "tɕʰ", "retroflex": False},
    "x": {"name": "舌面擦音", "name_en": "Palatal fricative", "ipa": "ɕ", "retroflex": False},
    "zh": {"name": "翘舌音", "name_en": "Retroflex", "ipa": "ʈʂ", "retroflex": True},
    "ch": {"name": "翘舌音", "name_en": "Retroflex", "ipa": "ʈʂʰ", "retroflex": True},
    "sh": {"name": "翘舌擦音", "name_en": "Retroflex fricative", "ipa": "ʂ", "retroflex": True},
    "r": {"name": "翘舌近音", "name_en": "Retroflex approximant", "ipa": "ɻ", "retroflex": True},
    "z": {"name": "平舌音", "name_en": "Alveolar affricate", "ipa": "ts", "retroflex": False},
    "c": {"name": "平舌音", "name_en": "Alveolar affricate", "ipa": "tsʰ", "retroflex": False},
    "s": {"name": "平舌擦音", "name_en": "Alveolar fricative", "ipa": "s", "retroflex": False},
}

# Final (韵母) database
FINALS = {
    "a": {"name": "单元音", "category": "simple_vowel", "nasal": False},
    "o": {"name": "单元音", "category": "simple_vowel", "nasal": False},
    "e": {"name": "单元音", "category": "simple_vowel", "nasal": False},
    "i": {"name": "单元音", "category": "simple_vowel", "nasal": False},
    "u": {"name": "单元音", "category": "simple_vowel", "nasal": False},
    "ü": {"name": "单元音", "category": "simple_vowel", "nasal": False},
    "ai": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "ei": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "ui": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "ao": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "ou": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "iu": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "ie": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "üe": {"name": "复合元音", "category": "compound_vowel", "nasal": False},
    "er": {"name": "卷舌元音", "category": "rhotic_vowel", "nasal": False},
    "an": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "n"},
    "en": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "n"},
    "in": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "n"},
    "un": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "n"},
    "ün": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "n"},
    "ang": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "ng"},
    "eng": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "ng"},
    "ing": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "ng"},
    "ong": {"name": "鼻韵母", "category": "nasal_final", "nasal": True, "nasal_type": "ng"},
}

# Common error patterns
ERROR_PATTERNS = {
    # Cantonese speaker common errors
    ("zh", "z"): {
        "description_en": "Retroflex 'zh' pronounced as flat 'z'",
        "description_zh": "翘舌音zh读成平舌音z",
        "fix_en": "Curl your tongue tip back and up towards the palate",
        "fix_zh": "将舌尖翘起向上抵住硬腭",
        "practice": ["知道", "中国", "吃饭"]
    },
    ("ch", "c"): {
        "description_en": "Retroflex 'ch' pronounced as flat 'c'",
        "description_zh": "翘舌音ch读成平舌音c",
        "fix_en": "Curl tongue back and add strong aspiration",
        "fix_zh": "舌尖翘起并加强送气",
        "practice": ["吃饭", "出去", "车站"]
    },
    ("sh", "s"): {
        "description_en": "Retroflex 'sh' pronounced as flat 's'",
        "description_zh": "翘舌音sh读成平舌音s",
        "fix_en": "Curl tongue back, round lips slightly",
        "fix_zh": "舌尖翘起，轻微圆唇",
        "practice": ["是的", "老师", "水果"]
    },
    ("r", "y"): {
        "description_en": "'r' pronounced as 'y'",
        "description_zh": "r音读成y音",
        "fix_en": "Curl tongue back, vocalize (add voice)",
        "fix_zh": "舌尖翘起，声带振动",
        "practice": ["人民", "认识", "日本"]
    },
    ("n", "l"): {
        "description_en": "Nasal 'n' pronounced as lateral 'l'",
        "description_zh": "鼻音n读成边音l",
        "fix_en": "Press tongue tip to alveolar ridge, let air escape through nose",
        "fix_zh": "舌尖抵住上齿龈，气从鼻腔呼出",
        "practice": ["努力", "那里", "奶奶"]
    },
    ("l", "n"): {
        "description_en": "Lateral 'l' pronounced as nasal 'n'",
        "description_zh": "边音l读成鼻音n",
        "fix_en": "Press tongue tip to alveolar ridge, let air escape from sides",
        "fix_zh": "舌尖抵住上齿龈，气从两边呼出",
        "practice": ["来了", "了解", "快乐"]
    },
    # Tone errors
    ("1", "2"): {
        "description_en": "Tone 1 (high flat) pronounced as Tone 2 (rising)",
        "description_zh": "第一声（高平）读成第二声（上升）",
        "fix_en": "Keep pitch flat and high throughout",
        "fix_zh": "保持音调平坦且高音",
        "practice": ["春天", "天空", "妈妈"]
    },
    ("1", "3"): {
        "description_en": "Tone 1 (high flat) pronounced as Tone 3 (dipping)",
        "description_zh": "第一声（高平）读成第三声（降升）",
        "fix_en": "Keep pitch flat and high, don't dip",
        "fix_zh": "保持音调平坦，不要下降再上升",
        "practice": ["开会", "飞机", "工作"]
    },
    ("2", "3"): {
        "description_en": "Tone 2 (rising) pronounced as Tone 3 (dipping)",
        "description_zh": "第二声（上升）读成第三声（降升）",
        "fix_en": "Rise from mid to high without dipping first",
        "fix_zh": "从中调升到高音，不要先降",
        "practice": ["头发", "银行", "不行"]
    },
    ("3", "2"): {
        "description_en": "Tone 3 (dipping) pronounced as Tone 2 (rising)",
        "description_zh": "第三声（降升）读成第二声（上升）",
        "fix_en": "Start mid, dip low, then rise high",
        "fix_zh": "从中调开始，下降到低音，再升到高音",
        "practice": ["努力", "水果", "了解"]
    },
    ("4", "2"): {
        "description_en": "Tone 4 (falling) pronounced as Tone 2 (rising)",
        "description_zh": "第四声（下降）读成第二声（上升）",
        "fix_en": "Start high and fall, don't rise",
        "fix_zh": "从高音开始下降，不要上升",
        "practice": ["再见", "已经", "工作"]
    },
    # Nasal final errors
    ("an", "ang"): {
        "description_en": "'an' pronounced as 'ang'",
        "description_zh": "an音读成ang音",
        "fix_en": "Keep tongue front, end with -n not -ng",
        "fix_zh": "舌头保持前位，以n结尾不是ng",
        "practice": ["南方", "当然", "简单"]
    },
    ("ang", "an"): {
        "description_en": "'ang' pronounced as 'an'",
        "description_zh": "ang音读成an音",
        "fix_en": "Keep tongue back, end with -ng",
        "fix_zh": "舌头保持后位，以ng结尾",
        "practice": ["帮忙", "商场", "厂房"]
    },
    ("en", "eng"): {
        "description_en": "'en' pronounced as 'eng'",
        "description_zh": "en音读成eng音",
        "fix_en": "End with nasal -n, not -ng",
        "fix_zh": "以n结尾，不要加g",
        "practice": ["根本", "认真", "大门"]
    },
    ("eng", "en"): {
        "description_en": "'eng' pronounced as 'en'",
        "description_zh": "eng音读成en音",
        "fix_en": "End with -ng, add slight nasal resonance",
        "fix_zh": "以ng结尾，加一点鼻音",
        "practice": ["更冷", "朋友", "风筝"]
    },
    ("in", "ing"): {
        "description_en": "'in' pronounced as 'ing'",
        "description_zh": "in音读成ing音",
        "fix_en": "End with -n, tongue front",
        "fix_zh": "以n结尾，舌头前位",
        "practice": ["人民", "银行", "今天"]
    },
    ("ing", "in"): {
        "description_en": "'ing' pronounced as 'in'",
        "description_zh": "ing音读成in音",
        "fix_en": "End with -ng, add nasal resonance",
        "fix_zh": "以ng结尾，加鼻音",
        "practice": ["高兴", "明星", "卫星"]
    },
    # Neutral tone errors
    ("_neutral_wrong"): {
        "description_en": "Should be neutral tone but pronounced with full tone",
        "description_zh": "应该是轻声但读成了完整声调",
        "fix_en": "Make it short and light",
        "fix_zh": "读得又短又轻",
        "practice": ["桌子", "椅子", "房子"]
    },
}

# Tone sandhi rules
TONE_SANDHI_RULES = {
    # 一不变调
    ("一", "一"): ("yī", "yì"),    # 一 + 一声 → 一声变四声
    ("一", "四"): ("yī", "yì"),    # 一 + 四声 → 一声变四声
    ("一", "三"): ("yī", "yì"),    # 一 + 三声 → 一声变四声
    ("一", "二"): ("yī", "yí"),    # 一 + 二声 → 一声变二声
    # 不不变调
    ("不", "四"): ("bù", "bù"),    # 不 + 四声 → 不变四声
    ("不", "一"): ("bù", "bú"),    # 不 + 一声 → 不变二声
    ("不", "三"): ("bù", "bú"),    # 不 + 三声 → 不变二声
    # 三声连读
    ("三", "三"): ("sān", "sán"), # 两个三声 → 前三声变二声
}

# Neutral tone characters (common)
NEUTRAL_TONE_WORDS = {
    "的", "了", "着", "过", "吗", "呢", "吧", "啊", "呀", "哦",
    "们", "里", "上", "下", "来", "去", "会", "能", "这", "那",
}
```

## 3.7 AI Feedback Generator (Enhanced)

```python
# /backend/tone-analysis/services/ai_feedback.py (ENHANCED)

class AIFeedbackGenerator:
    """Generate comprehensive AI-powered feedback"""

    def generate(self, analysis: AnalysisData) -> FeedbackResult:
        """Generate detailed feedback with all error information"""

    def _build_structured_prompt(self, analysis: AnalysisData) -> str:
        """Build prompt with all analysis data"""

    def _parse_ai_response(self, response: str) -> FeedbackResult:
        """Parse AI response into structured format"""
```

**Enhanced Prompt:**

```
You are a PSC (Putonghua Shuiping Ceshi) pronunciation expert.

## Task
Analyze the pronunciation and provide detailed feedback.

## Input Data

### Expected Text
{expected_text}

### User's Transcription
{transcription}

### Character-by-Character Analysis
{character_analysis_json}

### Error List
{errors_json}

### Scores
- Overall: {overall}
- Pronunciation: {pronunciation}
- Tone: {tone}
- Fluency: {fluency}

### Section
PSC Section {section}

## Output Format (JSON)

{{
    "overall_assessment_en": "...",
    "overall_assessment_zh": "...",
    "character_analysis": [
        {{
            "character": "天",
            "position": 1,
            "expected_pinyin": "tiān",
            "expected_tone": 1,
            "expected_initial": "t",
            "expected_final": "ian",
            "actual_pinyin": "tián",
            "actual_tone": 2,
            "actual_initial": "t",
            "actual_final": "ian",
            "status": "tone_error",
            "severity": "error",
            "feedback_en": "Tone 1 should be flat high. You said Tone 2 (rising).",
            "feedback_zh": "第一声应该是高平调。你读成了第二声（上升）。",
            "fix_tip_en": "Practice: mā-mā-mā (flat high), then tiān-tiān-tiān",
            "fix_tip_zh": "练习：妈妈妈（高平调），然后天天天",
            "practice_words": ["春天", "天空", "天才"]
        }}
    ],
    "error_summary": {{
        "total_errors": 1,
        "total_defects": 0,
        "initial_errors": 0,
        "final_errors": 0,
        "tone_errors": 1,
        "neutral_errors": 0,
        "omissions": 0,
        "additions": 0
    }},
    "practice_recommendations": {{
        "focus_areas_en": ["Tone 1 practice"],
        "focus_areas_zh": ["第一声练习"],
        "exercises_en": ["Read tone pairs: ā-á, ō-ó", "Practice tone 1 words"],
        "exercises_zh": ["读声调对：ā-á, ō-ó", "练习第一声词语"],
        "daily_duration": "15 minutes"
    }}
}}

Important:
1. For EACH character with error, include in character_analysis
2. Use specific error types: initial_error, final_error, tone_error, neutral_error, stress_error
3. Provide actionable fix tips
4. Recommend 3 practice words per error
5. Output valid JSON only
```

## 3.8 PSC Scoring Calculator

```python
# /backend/tone-analysis/services/psc_scorer.py (NEW)

class PSCScorer:
    """Calculate PSC-aligned scores"""

    def score(self, errors: List[PronunciationError],
              section: int,
              duration: float) -> ScoreResult:
        """Calculate scores per PSC standards"""

    def calculate_section1(self, errors: List[PronunciationError],
                          duration: float) -> SectionScore:
        """Section 1: Single characters - 10 points max"""
        # Error: -0.1, Defect: -0.05

    def calculate_section2(self, errors: List[PronunciationError],
                          duration: float) -> SectionScore:
        """Section 2: Polysyllabic words - 20 points max"""
        # Error: -0.2, Defect: -0.1

    def calculate_section3(self, answers: Section3Answers,
                          duration: float) -> SectionScore:
        """Section 3: Choice - 10 points max"""

    def calculate_section4(self, errors: List[PronunciationError],
                          passage_length: int,
                          duration: float) -> SectionScore:
        """Section 4: Reading passage - 30 points max"""
        # Character error: -0.1
        # Tone defect: -0.1 or -0.2
        # Intonation: -0.5, -1, -2
        # Pause: -0.5, -1, -2
        # Fluency: -0.5, -1, -2

    def calculate_section5(self, analysis: Section5Analysis,
                          duration: float) -> SectionScore:
        """Section 5: Speaking - 30 points max"""
        # Pronunciation: 20 points (6 levels)
        # Vocabulary/Grammar: 5 points (3 levels)
        # Fluency: 5 points (3 levels)

    def determine_level(self, total_score: float) -> LevelResult:
        """Determine PSC level and grade"""
```

---

# PART 4: FRONTEND COMPONENTS

## 4.1 Main Feedback Component

```tsx
// /frontend/src/components/PronunciationFeedback.tsx

interface PronunciationFeedbackProps {
  result: AnalysisResult;
  showDetails?: boolean;
}

export const PronunciationFeedback: React.FC<PronunciationFeedbackProps> = ({
  result,
  showDetails = true
}) => {
  return (
    <div className="feedback-container">
      {/* Header with scores */}
      <ScoreHeader scores={result.scores} pscLevel={result.psc_level} />

      {/* Character display */}
      <CharacterDisplay
        expected={result.expected_text}
        transcription={result.transcription}
        characterResults={result.character_results}
      />

      {/* Error summary */}
      {showDetails && (
        <ErrorSummary errors={result.errors} />
      )}

      {/* Detailed analysis */}
      {showDetails && result.errors.length > 0 && (
        <ErrorDetails errors={result.errors} />
      )}

      {/* Practice recommendations */}
      <PracticeRecommendations
        recommendations={result.feedback.practice_recommendations}
      />
    </div>
  );
};
```

## 4.2 Character Display Component

```tsx
// /frontend/src/components/CharacterDisplay.tsx

interface CharacterDisplayProps {
  expected: string;
  transcription: string;
  characterResults: CharacterResult[];
}

export const CharacterDisplay: React.FC<CharacterDisplayProps> = ({
  expected,
  transcription,
  characterResults
}) => {
  const getCharacterStatus = (char: string, index: number): Status => {
    const result = characterResults.find(r => r.position === index);
    return result?.status || 'correct';
  };

  return (
    <div className="character-display">
      <div className="text-row">
        <span className="label">Expected:</span>
        <div className="characters">
          {expected.split('').map((char, index) => (
            <CharacterBadge
              key={index}
              character={char}
              status={getCharacterStatus(char, index)}
              result={characterResults.find(r => r.position === index)}
            />
          ))}
        </div>
      </div>

      <div className="text-row">
        <span className="label">You said:</span>
        <div className="characters transcription">
          {transcription.split('').map((char, index) => (
            <span key={index} className="char">{char}</span>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="legend">
        <span className="correct">✓ Correct</span>
        <span className="error">✗ Error</span>
        <span className="defect">◐ Defect</span>
      </div>
    </div>
  );
};
```

## 4.3 Error Details Component

```tsx
// /frontend/src/components/ErrorDetails.tsx

interface ErrorDetailsProps {
  errors: PronunciationError[];
}

export const ErrorDetails: React.FC<ErrorDetailsProps> = ({ errors }) => {
  return (
    <div className="error-details">
      <h3>Detailed Analysis</h3>

      {errors.map((error, index) => (
        <ErrorCard key={index} error={error} />
      ))}
    </div>
  );
};

const ErrorCard: React.FC<{error: PronunciationError}> = ({ error }) => {
  return (
    <div className={`error-card ${error.severity}`}>
      <div className="error-header">
        <span className="character">{error.character}</span>
        <span className="position">Position {error.position + 1}</span>
        <span className={`badge ${error.category}`}>
          {formatCategory(error.category)}
        </span>
      </div>

      <div className="comparison">
        <div className="expected">
          <span className="label">Expected:</span>
          <span className="value">
            {error.expected.pinyin} (Tone {error.expected.tone})
          </span>
        </div>
        <div className="arrow">→</div>
        <div className="actual">
          <span className="label">Actual:</span>
          <span className="value">
            {error.actual.pinyin} (Tone {error.actual.tone})
          </span>
        </div>
      </div>

      <div className="feedback">
        <p className="en">{error.feedback.en}</p>
        <p className="zh">{error.feedback.zh}</p>
      </div>

      <div className="fix-tip">
        <strong>How to fix:</strong>
        <p>{error.feedback.fix_tip_en}</p>
        <p className="zh">{error.feedback.fix_tip_zh}</p>
      </div>

      {error.feedback.practice_words.length > 0 && (
        <div className="practice-words">
          <strong>Practice:</strong>
          <div className="words">
            {error.feedback.practice_words.map((word, i) => (
              <span key={i} className="word">{word}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
```

## 4.4 Visual Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PRONUNCIATION ANALYSIS                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Score: 87/100  │  Level: 2B  │  Pronunciation: 88  Tone: 85  Fluency: 90│
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Expected:  春天来了                                                    │
│  You said:  春田来了                                                   │
│                                                                         │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                           │
│  │ 春  │ │ 天  │ │ 来  │ │ 了  │ │    │                           │
│  │ ✅  │ │ 🔴  │ │ ✅  │ │ ✅  │ │    │                           │
│  │chūn│ │tiān │ │lái │ │ le  │ │    │                           │
│  │T1  │ │T1→T2│ │T2  │ │T0  │ │    │                           │
│  └─────┘ └─────┘ └─────┘ └─────┘ │    │                           │
│                                    │    │                           │
│  Legend: ✓ Correct  ✗ Error  ◐ Defect                                │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ERROR SUMMARY                                                         │
│  • Total Errors: 1      • Total Defects: 0                            │
│  • Initial Errors: 0    • Final Errors: 0                             │
│  • Tone Errors: 1       • Neutral Tone: 0                             │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  DETAILED ANALYSIS                                                     │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ Character: 天 (Position 2)                              [Error] │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │ Expected: tiān (Tone 1)     →     Actual: tián (Tone 2)        │  │
│  ├─────────────────────────────────────────────────────────────────┤  │
│  │ Category: Tone Error                                               │  │
│  │                                                                       │  │
│  │ Feedback:                                                            │  │
│  │ English: Tone 1 should be flat and high. You said Tone 2 (rising). │  │
│  │ 中文: 第一声应该是高平调。你读成了第二声（上升）。                   │  │
│  │                                                                       │  │
│  │ How to Fix:                                                         │  │
│  │ Keep the pitch flat and high throughout. Practice "mā-mā-mā".     │  │
│  │ 保持音调平坦且高音。练习"妈妈妈"。                                 │  │
│  │                                                                       │  │
│  │ Practice Words: 春天 | 天空 | 天才                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  PRACTICE RECOMMENDATIONS                                              │
│                                                                         │
│  Focus Areas:                                                          │
│  • Tone 1 (高平) - flat high tone practice                            │
│                                                                         │
│  Daily Exercise:                                                       │
│  • Read tone pairs: ā-á, ō-ó, ī-í                                    │
│  • Practice tone 1 words: 春天、天空、妈妈、工作                      │
│  • Duration: 15 minutes daily                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# PART 5: IMPLEMENTATION ROADMAP

## Phase 1: Foundation (Week 1-2)

| Day | Task | Files |
|-----|------|-------|
| 1-2 | Set up project structure, install dependencies | package.json, requirements.txt |
| 3-4 | Implement audio preprocessor | audio_preprocessor.py |
| 5-6 | Implement ASR service (Faster Whisper) | asr_service.py |
| 7 | Implement basic tone analyzer | tone_analyzer.py |

## Phase 2: Analysis Engine (Week 3-4)

| Day | Task | Files |
|-----|------|-------|
| 8-10 | Expand pinyin database with complete data | pinyin_db.py |
| 11-12 | Implement phoneme analyzer | phoneme_analyzer.py |
| 13-14 | Implement error detector | error_detector.py |
| 15 | Integrate all services | app.py |

## Phase 3: Scoring & Feedback (Week 5-6)

| Day | Task | Files |
|-----|------|-------|
| 16-17 | Implement PSC scorer | psc_scorer.py |
| 18-19 | Enhance AI feedback generator | ai_feedback.py |
| 20-21 | Build error feedback rules database | error_feedback.py |

## Phase 4: Frontend (Week 7-8)

| Day | Task | Files |
|-----|------|-------|
| 22-23 | Create TypeScript types | types/pronunciation.ts |
| 24-25 | Build PronunciationFeedback component | PronunciationFeedback.tsx |
| 26-27 | Build CharacterDisplay component | CharacterDisplay.tsx |
| 28 | Build ErrorSummary component | ErrorSummary.tsx |

## Phase 5: Integration & Testing (Week 9-10)

| Day | Task |
|-----|------|
| 29-30 | Integrate frontend with backend |
| 31-32 | Test with native speakers |
| 33-35 | Refine error detection accuracy |
| 36-40 | Final polish and deployment |

---

# PART 6: TECHNICAL REQUIREMENTS

## Dependencies

### Python (Backend)
```
# requirements.txt
flask>=2.3.0
flask-cors>=4.0.0
numpy>=1.24.0
scipy>=1.11.0
librosa>=0.10.0
soundfile>=0.12.0
pydub>=0.25.0
faster-whisper>=0.10.0
pypinyin>=0.49.0
requests>=2.31.0
python-dotenv>=1.0.0
```

### Frontend
```
# package.json
react>=18.0.0
typescript>=5.0.0
@emotion/react>=11.0.0
@emotion/styled>=11.0.0
```

---

# PART 7: SUCCESS METRICS

| Metric | Target | Measurement |
|--------|--------|-------------|
| Error detection accuracy | >85% | Compare with native speaker assessment |
| Tone detection accuracy | >90% | Compare with manual labeling |
| Feedback relevance | >80% | User satisfaction survey |
| PSC score alignment | >95% | Compare with official test |
| Response time | <5 seconds | Server-side processing |
| User satisfaction | >4/5 | App store rating |

---

# APPENDIX A: Complete Error Code Reference

| Error Code | Category | Description | PSC Impact |
|------------|----------|-------------|------------|
| INIT_ZH_Z | initial_error | zh→z confusion | -0.1 |
| INIT_CH_C | initial_error | ch→c confusion | -0.1 |
| INIT_SH_S | initial_error | sh→s confusion | -0.1 |
| INIT_R_Y | initial_error | r→y confusion | -0.1 |
| INIT_N_L | initial_error | n→l confusion | -0.1 |
| INIT_L_N | initial_error | l→n confusion | -0.1 |
| FINAL_AN_ANG | final_error | an→ang confusion | -0.1 |
| FINAL_ANG_AN | final_error | ang→an confusion | -0.1 |
| FINAL_EN_ENG | final_error | en→eng confusion | -0.1 |
| FINAL_ENG_EN | final_error | eng→en confusion | -0.1 |
| FINAL_IN_ING | final_error | in→ing confusion | -0.1 |
| FINAL_ING_IN | final_error | ing→in confusion | -0.1 |
| TONE_1_2 | tone_error | Tone 1→2 | -0.1 |
| TONE_1_3 | tone_error | Tone 1→3 | -0.1 |
| TONE_1_4 | tone_error | Tone 1→4 | -0.1 |
| TONE_2_1 | tone_error | Tone 2→1 | -0.1 |
| TONE_2_3 | tone_error | Tone 2→3 | -0.1 |
| TONE_2_4 | tone_error | Tone 2→4 | -0.1 |
| TONE_3_1 | tone_error | Tone 3→1 | -0.1 |
| TONE_3_2 | tone_error | Tone 3→2 | -0.1 |
| TONE_3_4 | tone_error | Tone 3→4 | -0.1 |
| TONE_4_1 | tone_error | Tone 4→1 | -0.1 |
| TONE_4_2 | tone_error | Tone 4→2 | -0.1 |
| TONE_4_3 | tone_error | Tone 4→3 | -0.1 |
| NEUTRAL_FULL | neutral_tone_error | Neutral→full tone | -0.05 |
| FULL_NEUTRAL | neutral_tone_error | Full tone→neutral | -0.05 |
| SANDHI_YI | tone_sandhi_error | 一变调错误 | -0.1 |
| SANDHI_BU | tone_sandhi_error | 不变调错误 | -0.1 |
| SANDHI_SAN | tone_sandhi_error | 三声连读错误 | -0.1 |
| OMISSION | omission | Character omitted | -0.1 |
| ADDITION | addition | Extra character | -0.1 |

---

# APPENDIX B: Practice Word Lists

### Retroflex Practice (翘舌音)
```
zh: 知道、中国、吃饭、车站、睡觉、校长、工作
ch: 吃饭、出去、车站、长江、乘车、词典、床
sh: 是的、老师、学生、事情、说话、书、水果
r: 人民、认识、日本、然后、日子、认真、热
```

### Nasal Distinction Practice (鼻音)
```
n: 努力、那么、哪里、奶奶、男女、农民、头脑
l: 努力、来了、了解、快乐、道理、礼貌、老
```

### Tone 1 Practice (第一声)
```
春天、天空、工作、飞机、高兴、人民、发音
```

### Tone 2 Practice (第二声)
```
银行、头发、学习、人民币、谁、忙、运动
```

### Tone 3 Practice (第三声)
```
努力、了解、简单、水果、已经、准备、北方
```

### Tone 4 Practice (第四声)
```
再见、已经、工作、飞机、特别注意、再会
```

---

This is the complete, comprehensive plan for building a production-ready PSC-aligned pronunciation feedback system.
