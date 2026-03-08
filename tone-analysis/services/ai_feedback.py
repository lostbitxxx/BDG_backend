"""
AI Feedback Generator using OpenRouter
Generates detailed PSC-aligned pronunciation feedback with structured character analysis
"""

import os
import logging
import json
import time
import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenRouter configuration - read lazily to ensure .env is loaded
def _get_openrouter_key():
    """Get API key, reading from environment each time"""
    return os.environ.get('OPENROUTER_API_KEY', '')

OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
DEFAULT_MODEL = 'stepfun/step-3.5-flash:free'


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class CharacterAnalysis:
    """Character-level pronunciation analysis"""
    character: str
    position: int
    expected_pinyin: str = ""
    expected_tone: int = 0
    expected_initial: str = ""  # Consonant/声母
    expected_final: str = ""    # Vowel/韵母
    actual_pinyin: str = ""
    actual_tone: int = 0
    actual_initial: str = ""   # Consonant/声母
    actual_final: str = ""      # Vowel/韵母
    status: str = "pending"     # correct, error, defect
    error_type: str = ""        # initial_error, final_error, tone_error, etc.
    feedback_en: str = ""        # MUST include TONE, CONSONANT, VOWEL details
    feedback_zh: str = ""       # MUST include 声调、声母、韵母 details
    fix_tip_en: str = ""
    fix_tip_zh: str = ""
    practice_words: List[str] = field(default_factory=list)


@dataclass
class FeedbackResult:
    """Complete feedback result"""
    overall_assessment_en: str
    overall_assessment_zh: str
    character_analysis: List[CharacterAnalysis]
    error_summary: Dict[str, Any]
    practice_recommendations: Dict[str, Any]
    encouragement_en: str = ""
    encouragement_zh: str = ""
    tone_analysis: Dict[str, Any] = field(default_factory=dict)
    phoneme_analysis: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# AI FEEDBACK GENERATOR CLASS
# ============================================================================

class AIFeedbackGenerator:
    """Generate AI-powered structured feedback for PSC pronunciation"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or _get_openrouter_key()
        self.model = DEFAULT_MODEL
        self.base_url = OPENROUTER_BASE_URL

    def generate_feedback(
        self,
        expected_text: str,
        transcription: str,
        errors: List[Dict[str, Any]],
        error_summary: Dict[str, Any],
        scores: Dict[str, float],
        section: int = 4
    ) -> Dict[str, Any]:
        """
        Generate detailed structured feedback based on analysis results

        Args:
            expected_text: What the user should have said
            transcription: What the user actually said
            errors: List of detected errors from error_detector
            error_summary: Summary of errors by category
            scores: Score breakdown
            section: PSC section (1-5)

        Returns:
            Structured feedback dictionary
        """
        if not self.api_key:
            logger.warning("No OpenRouter API key, using fallback feedback")
            return self._fallback_feedback(scores, section, error_summary)

        try:
            # Build structured prompt
            prompt = self._build_structured_prompt(
                expected_text, transcription, errors, error_summary, scores, section
            )

            # Call OpenRouter
            response = self._call_api(prompt)

            if response:
                return response
            else:
                return self._fallback_feedback(scores, section, error_summary)

        except Exception as e:
            logger.error(f"AI feedback error: {e}")
            return self._fallback_feedback(scores, section, error_summary)

    def _build_structured_prompt(
        self,
        expected_text: str,
        transcription: str,
        errors: List[Dict[str, Any]],
        error_summary: Dict[str, Any],
        scores: Dict[str, float],
        section: int
    ) -> str:
        """Build a prompt that asks for structured JSON output"""

        # Build character analysis from errors
        character_errors = []
        for error in errors:
            char_analysis = {
                "character": error.get("character", ""),
                "position": error.get("position", 0),
                "expected_pinyin": error.get("expected_pinyin", ""),
                "expected_tone": error.get("expected_tone", 0),
                "expected_initial": error.get("expected_initial", ""),
                "expected_final": error.get("expected_final", ""),
                "actual_pinyin": error.get("actual_pinyin", ""),
                "actual_tone": error.get("actual_tone", 0),
                "actual_initial": error.get("actual_initial", ""),
                "actual_final": error.get("actual_final", ""),
                "error_type": error.get("category", "unknown"),
                "severity": error.get("severity", "error"),
                "fix_tip_en": error.get("fix_tip_en", ""),
                "fix_tip_zh": error.get("fix_tip_zh", ""),
                "practice_words": error.get("practice_words", [])
            }
            character_errors.append(char_analysis)

        prompt = f"""You are a PSC (Putonghua Shuiping Ceshi) pronunciation expert. Your task is to provide detailed, actionable feedback for Mandarin pronunciation practice.

## INPUT DATA

### Expected Text
{expected_text}

### User's Transcription
{transcription}

### Scores
- Overall: {scores.get('overall', 0)}
- Pronunciation: {scores.get('pronunciation', 0)}
- Tone: {scores.get('tone', 0)}
- Fluency: {scores.get('fluency', 0)}

### Error Summary
- Total Errors: {error_summary.get('total_errors', 0)}
- Total Defects: {error_summary.get('total_defects', 0)}
- By Category: {json.dumps(error_summary.get('by_category', {}))}
- By Initial: {json.dumps(error_summary.get('by_initial', {}))}
- By Final: {json.dumps(error_summary.get('by_final', {}))}
- By Tone: {json.dumps(error_summary.get('by_tone', {}))}

### Character-Level Errors (DETAILED)
{json.dumps(character_errors, ensure_ascii=False, indent=2) if character_errors else "None"}

## YOUR TASK

Generate detailed pronunciation feedback in this EXACT JSON format:

{{
    "overall_assessment_en": "Your overall assessment in English (1-2 sentences)",
    "overall_assessment_zh": "你的总体评价（1-2句话）",
    "character_analysis": [
        {{
            "character": "字",
            "position": 0,
            "expected_pinyin": "pin",
            "expected_tone": 1,
            "expected_initial": "b",
            "expected_final": "in",
            "actual_pinyin": "pin",
            "actual_tone": 2,
            "actual_initial": "p",
            "actual_final": "in",
            "status": "correct/error/defect",
            "error_type": "initial_error/final_error/tone_error/neutral_error/stress_error/none",
            "feedback_en": "What was wrong and how to fix it in English. MUST include: TONE (expected Tone X, you said Tone Y), CONSONANT/INITIAL (expected [initial], you said [initial]), VOWEL/FINAL (expected [final], you said [final]), PHONEME details",
            "feedback_zh": "问题所在和改进方法（中文）。必须包括：声调（期望X声，实际Y声）、声母（期望[声母]，实际[声母]）、韵母（期望[韵母]，实际[韵母]）、音素详情",
            "fix_tip_en": "Specific tip to fix this error in English. Focus on: TONE correction method, INITIAL consonant pronunciation, FINAL vowel pronunciation",
            "fix_tip_zh": "具体改进建议（中文）。重点：声调纠正方法、声母发音、韵母发音",
            "practice_words": ["word1", "word2", "word3"]
        }}
    ],
    "error_summary": {{
        "total_errors": 0,
        "total_defects": 0,
        "initial_errors": 0,
        "final_errors": 0,
        "tone_errors": 0,
        "neutral_errors": 0,
        "omissions": 0,
        "additions": 0
    }},
    "practice_recommendations": {{
        "focus_areas_en": ["Areas to focus on in English - specifically TONE, INITIAL(CONSONANT), FINAL(VOWEL)"],
        "focus_areas_zh": ["需要加强的方面 - 重点：声调、声母、韵母"],
        "exercises_en": ["Specific exercises in English - include tone drills, initial drills, final drills"],
        "exercises_zh": ["具体练习 - 包括声调练习、声母练习、韵母练习"],
        "daily_duration_en": "Recommended daily practice time",
        "daily_duration_zh": "建议每日练习时长"
    }},
    "encouragement_en": "Encouraging message in English",
    "encouragement_zh": "鼓励的话",
    "tone_analysis": {{
        "total_tones": 0,
        "correct_tones": 0,
        "tone_accuracy": "0%",
        "common_errors": ["Tone X -> Tone Y", "etc"]
    }},
    "phoneme_analysis": {{
        "initial_errors": [],
        "final_errors": [],
        "consonant_issues": ["list of consonant/initial issues"],
        "vowel_issues": ["list of vowel/final issues"]
    }}
}}

## IMPORTANT RULES

1. Include ALL characters in character_analysis, mark correct ones with status "correct"
2. For EVERY character (both correct and error), provide:
   - expected_pinyin, expected_tone, expected_initial (consonant), expected_final (vowel)
   - actual_pinyin, actual_tone, actual_initial (consonant), actual_final (vowel)
3. For error characters, provide SPECIFIC feedback including:
   - TONE: "Expected Tone X, you said Tone Y. [explanation]"
   - CONSONANT/INITIAL: "Expected [initial] sound, you said [actual]. [pronunciation tip]"
   - VOWEL/FINAL: "Expected [final] sound, you said [actual]. [pronunciation tip]"
   - PHONEME: Detailed phonetic analysis
4. Each error should have 3 practice words
5. Focus areas should be based on actual error patterns found - specifically mention TONE, INITIAL(CONSONANT), FINAL(VOWEL)
6. Output valid JSON only - no markdown, no extra text
7. For correct characters, feedback_en and feedback_zh can be empty strings but include all expected/actual fields
8. Include a "phoneme_analysis" section with detailed breakdown of consonant and vowel issues

PSC Section {section} context:
- Section 1: Single characters - focus on tone and phoneme accuracy (声调、音素准确性)
- Section 2: Polysyllabic words - focus on tone sandhi and compound tones (变调、复合声调)
- Section 3: Choice/Judgment - focus on listening comprehension
- Section 4: Reading passage - focus on fluency, intonation, pauses (语调、停顿)
- Section 5: Speaking - focus on topic coherence and natural flow

Begin your response with {{ and end with }}"""

        return prompt

    def _call_api(self, prompt: str) -> Optional[Dict]:
        """Call OpenRouter API with retry logic"""

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://bodonggua.com',
            'X-Title': 'BoDongGua PSC'
        }

        payload = {
            'model': self.model,
            'response_format': {'type': 'json_object'},
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一個專業的普通話語音評測專家。你必須只輸出有效的JSON，不要有任何其他文字或解釋。確保JSON鍵使用英文，例如overall_assessment_en, overall_assessment_zh, character_analysis等。'
                },
                {
                    'role': 'user',
                    'content': prompt + '\n\nIMPORTANT: Output ONLY valid JSON. No explanation, no intro text, no markdown. Start with { and end with }'
                }
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                logger.info(f"Calling OpenRouter API (attempt {attempt + 1}/{max_retries}) with model: {self.model}")
                response = requests.post(
                    f'{self.base_url}/chat/completions',
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                logger.info(f"OpenRouter response status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    message = result['choices'][0]['message']
                    # Some models put content in 'content', others in 'reasoning'
                    message_content = message.get('content') or message.get('reasoning') or ''
                    content = message_content if message_content else ''
                    logger.info(f"OpenRouter response content length: {len(content) if content else 0}")

                    if not content:
                        logger.warning(f"Empty response from OpenRouter API (attempt {attempt + 1}/{max_retries})")
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        return None

                    # Try to parse JSON from response - find JSON in text
                    import re

                    # Method 1: Find balanced braces starting from any position
                    # Find all potential JSON objects using regex to find { }
                    def find_json_objects(text):
                        """Find potential JSON objects in text"""
                        # Find all brace pairs
                        stack = []
                        matches = []
                        for i, char in enumerate(text):
                            if char == '{':
                                stack.append(i)
                            elif char == '}' and stack:
                                start = stack.pop()
                                if not stack:  # Found a complete object
                                    matches.append((start, i+1))
                        return matches

                    matches = find_json_objects(content)
                    for start_idx, end_idx in matches:
                        json_str = content[start_idx:end_idx]
                        # Clean up common issues
                        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)  # trailing commas
                        try:
                            parsed = json.loads(json_str)
                            # Validate it's our expected format
                            if 'overall_assessment_en' in parsed or 'character_analysis' in parsed:
                                logger.info(f"Successfully parsed JSON from position {start_idx}")
                                return parsed
                        except (json.JSONDecodeError, KeyError):
                            continue

                    # Method 2: Look for markdown code blocks
                    if '```json' in content:
                        json_start = content.find('```json') + 7
                        json_end = content.find('```', json_start)
                        if json_end > json_start:
                            json_str = content[json_start:json_end]
                            try:
                                return json.loads(json_str)
                            except json.JSONDecodeError:
                                pass
                else:
                    logger.error(f"OpenRouter error: {response.status_code} (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return None

            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None
            except Exception as e:
                logger.warning(f"API call error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return None

        return None

    def _fallback_feedback(
        self,
        scores: Dict,
        section: int,
        error_summary: Dict = None
    ) -> Dict[str, Any]:
        """Fallback feedback when API is not available"""

        overall = scores.get('overall', 0)
        error_summary = error_summary or {}

        # Section-specific context
        section_names = {
            1: "Single Characters (讀單音節字詞)",
            2: "Polysyllabic Words (讀多音節詞語)",
            3: "Choice & Judgment (選擇判斷)",
            4: "Reading Passage (朗讀短文)",
            5: "Topic Speaking (命題說話)"
        }

        # Section-specific feedback
        if section == 3:
            # Section 3: Choice & Judgment (詞語判斷/量詞搭配/語法判斷)
            if overall >= 90:
                assessment_en = "Excellent! You have a strong grasp of Mandarin vocabulary, classifiers, and grammar."
                assessment_zh = "太棒了！你對普通話詞彙、量詞和語法掌握得很好。"
            elif overall >= 80:
                assessment_en = "Good understanding of vocabulary and grammar. Minor classifier usage errors."
                assessment_zh = "詞彙和語法理解不錯。量詞使用有一些小錯誤。"
            elif overall >= 70:
                assessment_en = "Fair vocabulary and grammar. Focus on classifier (量詞) usage."
                assessment_zh = "詞彙和語法一般。重點練習量詞搭配。"
            elif overall >= 60:
                assessment_en = "Basic vocabulary knowledge. Need more practice on grammar patterns."
                assessment_zh = "詞彙基礎一般。語法模式需要更多練習。"
            else:
                assessment_en = "Vocabulary and grammar need significant improvement."
                assessment_zh = "詞彙和語法需要大幅改進。"
        elif section == 5:
            # Section 5: Topic Speaking (命題說話)
            if overall >= 90:
                assessment_en = "Excellent speaking! Your pronunciation is natural and fluent."
                assessment_zh = "說得很棒！你的發音自然流暢。"
            elif overall >= 80:
                assessment_en = "Good speaking skills. Minor pronunciation issues."
                assessment_zh = "口語表達不錯。有一些小發音問題。"
            elif overall >= 70:
                assessment_en = "Decent speaking. Work on pronunciation and fluency."
                assessment_zh = "口語表達還可以。加強發音和流暢度練習。"
            elif overall >= 60:
                assessment_en = "Basic speaking ability. Focus on continuous speech."
                assessment_zh = "基本口語能力。加強連續說話練習。"
            else:
                assessment_en = "Speaking needs significant improvement."
                assessment_zh = "口語表達需要大幅改進。"
        else:
            # Sections 1, 2, 4: Reading sections
            if overall >= 90:
                assessment_en = "Excellent! Your Mandarin pronunciation is near-native."
                assessment_zh = "太棒了！你的普通話發音接近母語水平。"
                encouragement_en = "Keep up the excellent work!"
                encouragement_zh = "繼續保持！"
            elif overall >= 80:
                assessment_en = "Good pronunciation! Minor areas to improve."
                assessment_zh = "發音不錯！只有一些小問題需要改進。"
                encouragement_en = "Great progress! You're on the right track."
                encouragement_zh = "進步很大！繼續保持。"
            elif overall >= 70:
                assessment_en = "Decent pronunciation. Focus on tone accuracy."
                assessment_zh = "發音還可以。加強聲調準確性練習。"
                encouragement_en = "Keep practicing! Regular practice will help."
                encouragement_zh = "堅持練習！規律練習會有幫助。"
            elif overall >= 60:
                assessment_en = "Basic pronunciation needs work. Focus on tones and initials."
                assessment_zh = "基礎發音需要加強。重點練習聲調和聲母。"
                encouragement_en = "Don't give up! Start with basics."
                encouragement_zh = "別氣餒！從基礎開始。"
            else:
                assessment_en = "Significant pronunciation issues. Focus on fundamentals."
                assessment_zh = "發音問題較多。從基礎開始練習。"
                encouragement_en = "Every expert was once a beginner."
                encouragement_zh = "每個專家都曾是初學者。"

        # Generate focus areas based on error summary
        focus_areas_en = []
        focus_areas_zh = []

        if error_summary.get('by_category', {}).get('initial_error', 0) > 0:
            focus_areas_en.append('Initial consonant sounds (声母)')
            focus_areas_zh.append('声母练习')

        if error_summary.get('by_category', {}).get('final_error', 0) > 0:
            focus_areas_en.append('Final vowel sounds (韵母)')
            focus_areas_zh.append('韵母练习')

        if error_summary.get('by_category', {}).get('tone_error', 0) > 0:
            focus_areas_en.append('Tone practice (声调)')
            focus_areas_zh.append('声调练习')

        if not focus_areas_en:
            focus_areas_en = ['Overall pronunciation']
            focus_areas_zh = ['综合发音']

        return {
            'overall_assessment_en': assessment_en,
            'overall_assessment_zh': assessment_zh,
            'character_analysis': [],
            'error_summary': error_summary,
            'practice_recommendations': {
                'focus_areas_en': focus_areas_en,
                'focus_areas_zh': focus_areas_zh,
                'exercises_en': [
                    'Practice reading aloud for 15 minutes daily',
                    'Listen to native Mandarin speakers'
                ],
                'exercises_zh': [
                    '每天朗读15分钟',
                    '听标准普通话录音'
                ],
                'daily_duration_en': '15-20 minutes',
                'daily_duration_zh': '15-20分钟'
            },
            'encouragement_en': f"Section {section}: {encouragement_en}",
            'encouragement_zh': f"第{section}部分：{encouragement_zh}",
            'tone_analysis': {
                'total_tones': error_summary.get('by_category', {}).get('tone_error', 0) * 10,
                'correct_tones': 100 - error_summary.get('by_category', {}).get('tone_error', 0) * 10,
                'tone_accuracy': f"{max(0, 100 - error_summary.get('by_category', {}).get('tone_error', 0) * 10)}%",
                'common_errors': []
            },
            'phoneme_analysis': {
                'initial_errors': [],
                'final_errors': [],
                'consonant_issues': ['Initial consonant practice recommended'] if error_summary.get('by_category', {}).get('initial_error', 0) > 0 else [],
                'vowel_issues': ['Vowel/final practice recommended'] if error_summary.get('by_category', {}).get('final_error', 0) > 0 else []
            }
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_ai_feedback_instance = None


def get_ai_feedback() -> AIFeedbackGenerator:
    """Get singleton instance of AI feedback generator"""
    global _ai_feedback_instance
    if _ai_feedback_instance is None:
        _ai_feedback_instance = AIFeedbackGenerator()
    return _ai_feedback_instance


def generate_feedback(
    expected_text: str,
    transcription: str,
    errors: List[Dict[str, Any]],
    error_summary: Dict[str, Any],
    scores: Dict[str, float],
    section: int = 4
) -> Dict[str, Any]:
    """Convenience function to generate feedback"""
    generator = get_ai_feedback()
    return generator.generate_feedback(
        expected_text=expected_text,
        transcription=transcription,
        errors=errors,
        error_summary=error_summary,
        scores=scores,
        section=section
    )
