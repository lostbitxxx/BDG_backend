# PSC Pronunciation Feedback System - Comprehensive Implementation Plan

## Executive Summary

This document outlines a complete, rule-based feedback system for PSC (Putonghua Shuiping Ceshi) pronunciation analysis. The system leverages the existing error pattern database (~800+ patterns) to provide detailed, actionable feedback WITHOUT relying on AI generation.

---

## Current System Analysis

### What Already Exists
1. **ERROR_PATTERNS Database** - 793+ error patterns with:
   - Error codes (e.g., INIT_ZH_Z, TONE_1_2)
   - Category (initial_error, tone_error, final_error)
   - Description in English and Chinese
   - Fix instructions in English and Chinese
   - Practice tips
   - Practice words list
   - Difficulty rating

2. **Error Detector** - Identifies:
   - Character mismatches
   - Initial errors
   - Final errors
   - Tone errors
   - Omissions/insertions

3. **Fallback Feedback** - Basic template-based feedback (currently used)

### What's Missing
- Detailed character-by-character analysis
- Personalized practice recommendations based on error patterns
- Section-specific feedback
- Progress tracking

---

## Implementation Plan

### Phase 1: Enhanced Error Analysis (Priority: HIGH)

#### 1.1 Error Classification Enhancement
- Map all detected errors to ERROR_PATTERNS
- Categorize by:
  - Initial (声母) errors
  - Final (韵母) errors
  - Tone (声调) errors
  - Neutral tone (轻声) errors
  - Tone sandhi (变调) errors
  - Rhotic/erhua (儿化) errors

#### 1.2 Error Statistics
```
error_stats = {
    'total_errors': int,
    'total_defects': int,
    'by_category': {'initial_error': 5, 'tone_error': 3, ...},
    'by_initial': {'zh-z': 2, 'n-l': 1, ...},
    'by_final': {'an-en': 1, ...},
    'by_tone': {'tone_3_to_2': 2, ...},
    'most_difficult': [{'error': str, 'count': int}],
    'accuracy_rate': float
}
```

### Phase 2: Detailed Character Analysis (Priority: HIGH)

#### 2.1 Character-Level Analysis Structure
```python
character_analysis = [
    {
        'character': '你',
        'expected_pinyin': 'nǐ',
        'expected_tone': 3,
        'expected_initial': 'n',
        'expected_final': 'i',
        'status': 'correct' | 'error' | 'defect',
        'error_type': 'initial_error' | 'tone_error' | 'final_error',
        'feedback_en': str,
        'feedback_zh': str,
        'fix_tip_en': str,
        'fix_tip_zh': str,
        'practice_words': [str]
    },
    ...
]
```

#### 2.2 Feedback Generation from ERROR_PATTERNS
- For each error, lookup in ERROR_PATTERNS
- Extract: description, fix, tip, practice_words
- Build character analysis array

### Phase 3: Section-Specific Feedback (Priority: HIGH)

#### 3.1 Section 1 & 2 (Reading)
- Focus on: tones, initials, finals
- Group errors by: initial type, final type, tone number
- Provide: character-by-character breakdown

#### 3.2 Section 3 (Choice & Judgment)
- Already handled by multiple choice scoring
- Provide: correct answer explanations

#### 3.3 Section 4 (Reading Passage)
- Include: rhythm, pausing, stress analysis
- Character-level feedback for problem characters

#### 3.4 Section 5 (Topic Speaking)
- Pronunciation accuracy
- Fluency assessment
- Topic relevance
- Vocabulary usage

### Phase 4: Practice Recommendations (Priority: MEDIUM)

#### 4.1 Focus Areas
Based on error statistics, generate:
```python
practice_recommendations = {
    'focus_areas_en': ['Retroflex consonants (zh, ch, sh)', 'Third tone'],
    'focus_areas_zh': ['翘舌音', '第三声'],
    'priority_errors': [
        {'error': 'zh-z', 'count': 5, 'difficulty': 'high'},
        {'error': 'tone_3_to_2', 'count': 3, 'difficulty': 'hard'}
    ],
    'daily_duration_en': '15-20 minutes',
    'daily_duration_zh': '15-20分钟',
    'practice_schedule': {
        'day1': ['zh-z contrast', 'tone 3 practice'],
        'day2': ['n-l contrast', ...},
        ...
    }
}
```

#### 4.2 Practice Words
- Extract from ERROR_PATTERNS practice_words
- Prioritize by: error frequency, difficulty
- Generate 5-10 words per error type

### Phase 5: Progress Tracking (Priority: LOW)

#### 5.1 Error History
- Track errors across tests
- Identify persistent errors
- Track improvement over time

---

## Technical Implementation

### File: services/feedback_generator.py (NEW)

```python
class FeedbackGenerator:
    """Rule-based PSC feedback generator"""

    def __init__(self):
        self.error_patterns = load_error_patterns()

    def generate(self, errors, scores, section, error_summary) -> Dict:
        """Generate comprehensive feedback"""

        # 1. Generate character analysis
        char_analysis = self._generate_character_analysis(errors)

        # 2. Generate overall assessment
        assessment = self._generate_assessment(scores, error_summary)

        # 3. Generate practice recommendations
        recommendations = self._generate_recommendations(errors, error_summary)

        # 4. Generate encouragement
        encouragement = self._generate_encouragement(scores, section)

        return {
            'overall_assessment_en': assessment['en'],
            'overall_assessment_zh': assessment['zh'],
            'character_analysis': char_analysis,
            'practice_recommendations': recommendations,
            'encouragement_en': encouragement['en'],
            'encouragement_zh': encouragement['zh'],
            'error_summary': error_summary,
            'tone_analysis': self._generate_tone_analysis(errors),
            'phoneme_analysis': self._generate_phoneme_analysis(errors)
        }
```

### File: app.py (MODIFY)

Replace AI feedback calls with:
```python
from services.feedback_generator import FeedbackGenerator

feedback_gen = FeedbackGenerator()
feedback = feedback_gen.generate(errors, scores, section, error_summary)
```

---

## Feedback Output Examples

### Example 1: Score 95+ (Excellent)
```
📊 Overall Assessment:
   English: Excellent! Your Mandarin pronunciation is near-native level.
   中文: 太棒了！你的普通话发音接近母语水平。

🔍 Detailed Analysis:
   • All 100 characters pronounced correctly
   • Tone accuracy: 100%
   • Initial consonants: Perfect
   • Final vowels: Perfect

💪 Encouragement:
   Keep up the excellent work! You're ready for a Level 1 certification.

📚 Practice Recommendations:
   • Maintain daily reading practice
   • Focus on advanced vocabulary
```

### Example 2: Score 80-89 (Good)
```
📊 Overall Assessment:
   English: Good pronunciation! Minor areas to improve.
   中文: 发音不错！只有一些小问题需要改进。

🔍 Detailed Analysis:
   • 95/100 characters correct
   • 5 errors found:
     - 2x zh/z confusion (知道, 吃饭)
     - 1x tone 3 error (努力)
     - 2x final error (an/en)

   Character Details:
   • 知 (zhī): zh→z initial error
     Fix: Curl tongue back
     Practice: 知道, 中国, 吃饭
   • 努 (nǔ): tone 3→2 error
     Fix: Dip then rise
     Practice: 努力, 了解

💪 Encouragement:
   Great progress! Focus on retroflex sounds.

📚 Practice Recommendations:
   Focus: Retroflex consonants (zh, ch, sh)
   Daily: 15-20 minutes
   Priority: 翘舌音练习
```

### Example 3: Score 60-69 (Needs Work)
```
📊 Overall Assessment:
   English: Basic pronunciation needs work. Focus on tones and initials.
   中文: 基础发音需要加强。重点练习声调和声母。

🔍 Detailed Analysis:
   • 70/100 characters correct
   • 30 errors found:
     - 10x initial errors (n/l, zh/z, ch/c)
     - 15x tone errors (especially tone 3)
     - 5x final errors

   Priority Issues:
   1. n/l confusion (5 occurrences)
      Practice: 努力, 那里, 来了
   2. Third tone (4 occurrences)
      Practice: 努力, 了解, 水果
   3. zh/z confusion (3 occurrences)
      Practice: 知道, 中国, 吃饭

💪 Encouragement:
   Don't give up! Start with basics.

📚 Practice Recommendations:
   Focus: Initial sounds & Tone 3
   Daily: 20-30 minutes
   Schedule:
   - Day 1-2: n/l contrast
   - Day 3-4: Tone 3 dipping
   - Day 5-6: Retroflex sounds
   - Day 7: Review & record
```

---

## Testing Plan

1. **Unit Tests**
   - Test each error pattern lookup
   - Test feedback generation for each score range
   - Test section-specific feedback

2. **Integration Tests**
   - Test full pipeline: audio → analysis → feedback
   - Compare with expected output

3. **User Testing**
   - Get feedback from native Cantonese speakers
   - Verify practice recommendations are helpful

---

## Migration Steps

1. **Backup** current ai_feedback.py
2. **Create** new feedback_generator.py
3. **Update** app.py to use new generator
4. **Test** all sections
5. **Remove** OpenRouter/AI dependencies
6. **Update** frontend to display new feedback format

---

## Conclusion

This plan provides a comprehensive, rule-based feedback system that:
- Uses existing ERROR_PATTERNS database (793+ patterns)
- Provides character-level analysis
- Generates personalized practice recommendations
- Works without AI/API dependencies
- Is deterministic and fast
- Can be extended with more patterns

The system will provide BETTER feedback than AI because:
1. Domain experts crafted the error patterns
2. Specific practice words are curated
3. Fix instructions are tested and clear
4. No API costs or reliability issues
