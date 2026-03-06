"""
AI Feedback Generator using OpenRouter (stepfun/step-3.5-flash:free)
Generates detailed pronunciation feedback with improvement suggestions
"""

import os
import logging
import json
import requests
from typing import Dict, List, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenRouter configuration
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1'
DEFAULT_MODEL = 'stepfun/step-3.5-flash:free'


class AIFeedbackGenerator:
    """Generate AI-powered feedback for PSC pronunciation"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or OPENROUTER_API_KEY
        self.model = DEFAULT_MODEL
        self.base_url = OPENROUTER_BASE_URL

    def generate_feedback(
        self,
        transcription: str,
        expected_text: str,
        errors: List[Dict[str, Any]],
        defects: List[Dict[str, Any]],
        scores: Dict[str, float],
        section: int = 4
    ) -> Dict[str, Any]:
        """
        Generate detailed feedback based on analysis results

        Args:
            transcription: What the user actually said
            expected_text: What they should have said
            errors: List of phonetic errors detected
            defects: List of phonetic defects detected
            scores: Score breakdown (pronunciation, tone, fluency, overall)
            section: PSC section (1-5)

        Returns:
            Detailed feedback dictionary
        """
        if not self.api_key:
            logger.warning("No OpenRouter API key, using fallback feedback")
            return self._fallback_feedback(scores, section)

        try:
            # Build the prompt
            prompt = self._build_prompt(
                transcription, expected_text, errors, defects, scores, section
            )

            # Call OpenRouter
            response = self._call_api(prompt)

            if response:
                return response
            else:
                return self._fallback_feedback(scores, section)

        except Exception as e:
            logger.error(f"AI feedback error: {e}")
            return self._fallback_feedback(scores, section)

    def _build_prompt(
        self,
        transcription: str,
        expected_text: str,
        errors: List[Dict],
        defects: List[Dict],
        scores: Dict,
        section: int
    ) -> str:
        """Build prompt for AI"""

        # Analyze error types
        error_summary = self._summarize_errors(errors, defects)

        prompt = f"""You are a Mandarin pronunciation assessment expert. Generate detailed feedback in BOTH English and Simplified Chinese based on the assessment results.

## Test Section
Section {section}

## Expected Content
{expected_text}

## Actual Reading
{transcription}

## Scores
- Overall: {scores.get('overall', 0)}
- Pronunciation: {scores.get('pronunciation', 0)}
- Tone: {scores.get('tone', 0)}
- Fluency: {scores.get('fluency', 0)}

## Errors Detected
{json.dumps(errors, ensure_ascii=False, indent=2) if errors else "None"}

## Defects Detected
{json.dumps(defects, ensure_ascii=False, indent=2) if defects else "None"}

## Error Type Analysis
{error_summary}

Please generate feedback in the following JSON format with BOTH languages:

{{
    "overall_assessment_en": "Overall assessment in English (1-2 sentences)",
    "overall_assessment_zh": "总体评价（1-2句话）",
    "key_issues_en": ["Issue 1", "Issue 2", "Issue 3"],
    "key_issues_zh": ["主要问题1", "主要问题2", "主要问题3"],
    "detailed_analysis": [
        {{
            "character": "字",
            "expected": "Correct pronunciation",
            "actual": "Actual pronunciation",
            "issue": "Issue type",
            "suggestion_en": "Improvement suggestion in English",
            "suggestion_zh": "改进建议"
        }}
    ],
    "improvement_tips_en": ["Tip 1 in English", "Tip 2", "Tip 3"],
    "improvement_tips_zh": ["练习建议1", "练习建议2", "练习建议3"],
    "practice_recommendations": {{
        "focus_areas_en": ["Areas to focus on in English"],
        "focus_areas_zh": ["需要加强的方面"],
        "suggested_exercises_en": ["Exercise 1", "Exercise 2"],
        "suggested_exercises_zh": ["推荐练习1", "练习建议2"],
        "daily_duration_en": "Recommended daily practice time",
        "daily_duration_zh": "建议每日练习时长"
    }},
    "encouragement_en": "Encouraging message in English",
    "encouragement_zh": "鼓励的话"
}}

Note:
1. If there are no errors, overall_assessment should be positive
2. detailed_analysis only includes characters with issues
3. Provide specific improvement suggestions based on error types
4. User may be a Cantonese speaker - focus on common pronunciation issues
5. Output valid JSON only, no extra text
"""

        return prompt

    def _summarize_errors(self, errors: List[Dict], defects: List[Dict]) -> str:
        """Summarize error types"""

        # Count by type
        error_types = {}
        for e in errors:
            issue = e.get('issue', e.get('type', 'unknown'))
            error_types[issue] = error_types.get(issue, 0) + 1

        defect_types = {}
        for d in defects:
            issue = d.get('issue', d.get('type', 'unknown'))
            defect_types[issue] = defect_types.get(issue, 0) + 1

        summary = []
        if error_types:
            summary.append(f"錯誤: {', '.join(f'{k}×{v}' for k, v in error_types.items())}")
        if defect_types:
            summary.append(f"缺陷: {', '.join(f'{k}×{v}' for k, v in defect_types.items())}")

        return '; '.join(summary) if summary else '無明顯錯誤'

    def _call_api(self, prompt: str) -> Optional[Dict]:
        """Call OpenRouter API"""

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://bodonggua.com',
            'X-Title': 'BoDongGua PSC'
        }

        payload = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一個專業的普通話語音評測專家，擅長分析發音錯誤並提供改進建議。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.7,
            'max_tokens': 1500
        }

        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']

                # Try to parse JSON from response
                # The AI might wrap JSON in markdown
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0]
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0]

                return json.loads(content.strip())
            else:
                logger.error(f"OpenRouter error: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"API call error: {e}")
            return None

    def _fallback_feedback(self, scores: Dict, section: int) -> Dict[str, Any]:
        """Fallback feedback when API is not available"""

        overall = scores.get('overall', 0)

        # Section-specific encouragement
        section_names = {1: "Single Characters", 2: "Polysyllabic Words", 3: "Choice", 4: "Reading Passage", 5: "Speaking"}
        section_names_zh = {1: "单音节字", 2: "多音节词语", 3: "选择判断", 4: "朗读短文", 5: "命题说话"}

        if overall >= 90:
            assessment_en = "Your Mandarin pronunciation is excellent! Keep it up!"
            assessment_zh = "你的普通话发音非常标准！继续保持。"
            encouragement_en = "Amazing! You've reached professional level!"
            encouragement_zh = "太棒了！你已经达到了专业水准。"
        elif overall >= 80:
            assessment_en = "Good pronunciation with minor areas to improve."
            assessment_zh = "发音良好，只有少许小问题需要注意。"
            encouragement_en = "Great job! More practice will make it perfect."
            encouragement_zh = "做得很好！多练习会更完美。"
        elif overall >= 70:
            assessment_en = "Generally correct pronunciation, but some tones and sounds need work."
            assessment_zh = "发音基本正确，但有一些声调或发音需要改进。"
            encouragement_en = "Nice work! Consistent practice will lead to big improvements."
            encouragement_zh = "不错！坚持练习会有很大进步。"
        elif overall >= 60:
            assessment_en = "Pronunciation needs improvement. Common issues are tones and retroflex sounds."
            assessment_zh = "发音有待提高，常见问题是声调和翘舌音。"
            encouragement_en = "Keep going! 10 minutes of daily practice will show results."
            encouragement_zh = "加油！每天练习10分钟会有明显改善。"
        else:
            assessment_en = "Need to strengthen basic pronunciation practice."
            assessment_zh = "需要加强基础发音练习。"
            encouragement_en = "Don't give up! Start from the basics and work your way up."
            encouragement_zh = "别气馒！从基础开始，一步一步来。"

        return {
            'overall_assessment_en': assessment_en,
            'overall_assessment_zh': assessment_zh,
            'key_issues_en': self._get_key_issues_en(scores),
            'key_issues_zh': self._get_key_issues_zh(scores),
            'detailed_analysis': [],
            'improvement_tips_en': self._get_improvement_tips_en(scores),
            'improvement_tips_zh': self._get_improvement_tips_zh(scores),
            'practice_recommendations': {
                'focus_areas_en': self._get_focus_areas_en(scores),
                'focus_areas_zh': self._get_focus_areas_zh(scores),
                'suggested_exercises_en': ['Read aloud for 10 minutes daily', 'Listen to standard Mandarin recordings'],
                'suggested_exercises_zh': ['每天朗读10分钟', '听标准普通话录音'],
                'daily_duration_en': '10-15 minutes',
                'daily_duration_zh': '10-15分钟'
            },
            'encouragement_en': f"Section {section} ({section_names.get(section, '')}): {encouragement_en}",
            'encouragement_zh': f"第{section}部分「{section_names_zh.get(section, '')}」：{encouragement_zh}"
        }

    def _get_key_issues(self, scores: Dict) -> List[str]:
        """Get key issues based on scores"""

        issues = []

        if scores.get('pronunciation', 100) < 80:
            issues.append('發音準確度需要提高')
        if scores.get('tone', 100) < 80:
            issues.append('聲調需要多加練習')
        if scores.get('fluency', 100) < 80:
            issues.append('流暢度有待改善')

        return issues if issues else ['整體表現良好']

    def _get_key_issues_en(self, scores: Dict) -> List[str]:
        """Get key issues based on scores (English)"""

        issues = []

        if scores.get('pronunciation', 100) < 80:
            issues.append('Pronunciation accuracy needs improvement')
        if scores.get('tone', 100) < 80:
            issues.append('Tones need more practice')
        if scores.get('fluency', 100) < 80:
            issues.append('Fluency needs improvement')

        return issues if issues else ['Overall performance is good']

    def _get_key_issues_zh(self, scores: Dict) -> List[str]:
        """Get key issues based on scores (Chinese)"""

        issues = []

        if scores.get('pronunciation', 100) < 80:
            issues.append('发音准确度需要提高')
        if scores.get('tone', 100) < 80:
            issues.append('声调需要多加练习')
        if scores.get('fluency', 100) < 80:
            issues.append('流畅度有待改善')

        return issues if issues else ['整体表现良好']

    def _get_improvement_tips(self, scores: Dict) -> List[str]:
        """Get improvement tips based on scores"""

        tips = []

        if scores.get('tone', 100) < 85:
            tips.append('練習四聲調：ā á ǎ à, ē é ě è, ī í ǐ ì, ū ú ǔ ù')
        if scores.get('pronunciation', 100) < 85:
            tips.append('注意翹舌音(zh, ch, sh, r)和扁舌音(z, c, s)的區別')
        if scores.get('fluency', 100) < 85:
            tips.append('多朗讀文章，注意句子中間的自然停頓')

        if not tips:
            tips.append('繼續保持當前練習節奏')

        return tips

    def _get_improvement_tips_en(self, scores: Dict) -> List[str]:
        """Get improvement tips based on scores (English)"""

        tips = []

        if scores.get('tone', 100) < 85:
            tips.append('Practice the four tones: ā á ǎ à, ē é ě è, ī í ǐ ì, ū ú ǔ ù')
        if scores.get('pronunciation', 100) < 85:
            tips.append('Pay attention to the difference between retroflex (zh, ch, sh, r) and flat (z, c, s) initials')
        if scores.get('fluency', 100) < 85:
            tips.append('Read more articles, pay attention to natural pauses in sentences')

        if not tips:
            tips.append('Keep up the current practice routine')

        return tips

    def _get_improvement_tips_zh(self, scores: Dict) -> List[str]:
        """Get improvement tips based on scores (Chinese)"""

        tips = []

        if scores.get('tone', 100) < 85:
            tips.append('练习四声调：ā á ǎ à, ē é ě è, ī í ǐ ì, ū ú ǔ ù')
        if scores.get('pronunciation', 100) < 85:
            tips.append('注意翘舌音(zh, ch, sh, r)和扁舌音(z, c, s)的区别')
        if scores.get('fluency', 100) < 85:
            tips.append('多朗读文章，注意句子中间的自然停顿')

        if not tips:
            tips.append('继续保持当前练习节奏')

        return tips

    def _get_focus_areas(self, scores: Dict) -> List[str]:
        """Get focus areas for practice"""

        areas = []

        if scores.get('tone', 100) < 80:
            areas.append('聲調訓練')
        if scores.get('pronunciation', 100) < 80:
            areas.append('發音訓練')
        if scores.get('fluency', 100) < 80:
            areas.append('朗讀流暢度')

        return areas if areas else ['綜合訓練']

    def _get_focus_areas_en(self, scores: Dict) -> List[str]:
        """Get focus areas for practice (English)"""

        areas = []

        if scores.get('tone', 100) < 80:
            areas.append('Tone training')
        if scores.get('pronunciation', 100) < 80:
            areas.append('Pronunciation training')
        if scores.get('fluency', 100) < 80:
            areas.append('Reading fluency')

        return areas if areas else ['Comprehensive training']

    def _get_focus_areas_zh(self, scores: Dict) -> List[str]:
        """Get focus areas for practice (Chinese)"""

        areas = []

        if scores.get('tone', 100) < 80:
            areas.append('声调训练')
        if scores.get('pronunciation', 100) < 80:
            areas.append('发音训练')
        if scores.get('fluency', 100) < 80:
            areas.append('朗读流畅度')

        return areas if areas else ['综合训练']


# Singleton instance
_ai_feedback = None


def get_ai_feedback() -> AIFeedbackGenerator:
    global _ai_feedback
    if _ai_feedback is None:
        _ai_feedback = AIFeedbackGenerator()
    return _ai_feedback
