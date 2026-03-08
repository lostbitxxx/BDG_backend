"""
Rule-Based PSC Pronunciation Feedback Generator
Generates detailed, actionable feedback without AI
"""

import logging
from typing import Dict, List, Any, Optional
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import error patterns from pinyin_db
from .pinyin_db import ERROR_PATTERNS


# ============================================================================
# FEEDBACK GENERATOR CLASS
# ============================================================================

class FeedbackGenerator:
    """Generate comprehensive PSC-aligned feedback using rule-based system"""

    def __init__(self):
        self.error_patterns = ERROR_PATTERNS

    def generate(
        self,
        errors: List[Dict],
        scores: Dict[str, float],
        section: int,
        error_summary: Dict[str, Any],
        expected_text: str = "",
        transcription: str = ""
    ) -> Dict[str, Any]:
        """
        Generate comprehensive feedback based on errors and scores

        Args:
            errors: List of detected errors from error_detector
            scores: Score breakdown (overall, pronunciation, tone, fluency)
            section: PSC section (1-5)
            error_summary: Summary of errors by category
            expected_text: Original expected text for character analysis
            transcription: Actual transcription for analysis

        Returns:
            Detailed feedback dictionary
        """
        overall = scores.get('overall', 0)

        # Generate character analysis - include all characters, not just errors
        char_analysis = self._generate_character_analysis(errors, expected_text, scores, transcription)

        # Generate overall assessment
        assessment = self._generate_assessment(overall, section, error_summary)

        # Generate practice recommendations
        recommendations = self._generate_recommendations(errors, error_summary, section)

        # Generate encouragement
        encouragement = self._generate_encouragement(overall, section)

        # Generate tone analysis
        tone_analysis = self._generate_tone_analysis(errors, scores)

        # Generate phoneme analysis
        phoneme_analysis = self._generate_phoneme_analysis(errors, scores)

        return {
            'overall_assessment_en': assessment['en'],
            'overall_assessment_zh': assessment['zh'],
            'character_analysis': char_analysis,
            'practice_recommendations': recommendations,
            'encouragement_en': encouragement['en'],
            'encouragement_zh': encouragement['zh'],
            'error_summary': error_summary,
            'tone_analysis': tone_analysis,
            'phoneme_analysis': phoneme_analysis,
            'key_issues_en': self._get_key_issues(errors)['en'],
            'key_issues_zh': self._get_key_issues(errors)['zh'],
            'improvement_tips_en': self._get_improvement_tips(errors)['en'],
            'improvement_tips_zh': self._get_improvement_tips(errors)['zh']
        }

    def _generate_character_analysis(self, errors: List[Dict], expected_text: str = "", scores: Dict = None, transcription: str = "") -> List[Dict]:
        """Generate character-level analysis from errors and expected text"""
        char_analysis = []
        overall_score = scores.get('overall', 0) if scores else 100

        # Build a dict of error characters for quick lookup
        error_chars = {}
        for error in errors:
            char = error.get('character', '')
            error_chars[char] = error

        # Import pinyin_db to get pinyin for characters
        from . import pinyin_db

        # Analyze transcription for length differences
        expected_clean = expected_text
        transcription_clean = transcription
        for p in '，。？！、；：""''（）【】《》…—':
            expected_clean = expected_clean.replace(p, '')
            transcription_clean = transcription_clean.replace(p, '')

        length_diff = len(expected_clean) - len(transcription_clean)

        # Process each character in expected text
        for char in expected_text:
            # Skip punctuation
            if char in '，。？！、；：""''（）【】《》…—':
                continue

            if char in error_chars:
                # Character has error
                error = error_chars[char]
                expected_pinyin = error.get('expected_pinyin', '')
                expected_initial = error.get('expected_initial', '')
                expected_final = error.get('expected_final', '')
                expected_tone = error.get('expected_tone', 0)
                actual_initial = error.get('actual_initial', '')
                actual_final = error.get('actual_final', '')
                actual_tone = error.get('actual_tone', 0)
                category = error.get('category', 'unknown')

                error_info = self._lookup_error_info(
                    expected_initial, actual_initial,
                    expected_tone, actual_tone,
                    expected_final, actual_final
                )

                entry = {
                    'character': char,
                    'expected_pinyin': expected_pinyin,
                    'expected_tone': expected_tone,
                    'expected_initial': expected_initial,
                    'expected_final': expected_final,
                    'status': 'error' if category in ['initial_error', 'tone_error', 'final_error'] else 'defect',
                    'error_type': category,
                }

                if error_info:
                    entry['feedback_en'] = error_info.get('description_en', '')
                    entry['feedback_zh'] = error_info.get('description_zh', '')
                    entry['fix_tip_en'] = error_info.get('fix_en', '')
                    entry['fix_tip_zh'] = error_info.get('fix_zh', '')
                    entry['practice_words'] = error_info.get('practice_words', [])
                else:
                    entry['feedback_en'] = self._get_generic_feedback(category, expected_initial, expected_tone)['en']
                    entry['feedback_zh'] = self._get_generic_feedback(category, expected_initial, expected_tone)['zh']
                    entry['fix_tip_en'] = 'Practice this sound regularly'
                    entry['practice_words'] = self._get_practice_words(expected_initial, expected_tone)
            else:
                # Character is correct - get pinyin from database
                pinyin_info = pinyin_db.get_char_info(char) or {}
                pinyin = pinyin_info.get('pinyin', '')
                tone = pinyin_info.get('tone', 0)
                initial = pinyin_info.get('initial', '')
                final = pinyin_info.get('final', '')

                # Determine status based on score and analysis
                status = 'correct'
                error_type = 'none'
                feedback_en = ''
                feedback_zh = ''
                fix_tip_en = ''
                fix_tip_zh = ''

                # Track character index for showing length error only once
                char_index = len([c for c in expected_text[:expected_text.index(char)+1] if c not in '，。？！、；：""''（）【】《》…—'])

                if overall_score < 80 and len(error_chars) == 0:
                    # Low score but no character mismatch - likely pronunciation issues
                    if length_diff != 0 and char_index == 1:
                        # Only show length mismatch on first character
                        status = 'review'
                        error_type = 'length_mismatch'
                        if length_diff > 0:
                            feedback_en = f'Possible omission detected ({length_diff} chars less in transcription)'
                            feedback_zh = f'检测到漏读（转录文本少{length_diff}个字符）'
                        else:
                            feedback_en = f'Possible addition detected ({abs(length_diff)} extra chars in transcription)'
                            feedback_zh = f'检测到增读（转录文本多{abs(length_diff)}个字符）'
                    else:
                        status = 'review'
                        error_type = 'pronunciation_needs_work'
                        feedback_en = 'Pronunciation needs improvement'
                        feedback_zh = '发音需要改进'
                        fix_tip_en = 'Focus on tone accuracy and clear pronunciation'
                        fix_tip_zh = '注意声调准确性和清晰发音'

                entry = {
                    'character': char,
                    'expected_pinyin': pinyin,
                    'expected_tone': tone,
                    'expected_initial': initial,
                    'expected_final': final,
                    'status': status,
                    'error_type': error_type,
                }

                if feedback_en:
                    entry['feedback_en'] = feedback_en
                if feedback_zh:
                    entry['feedback_zh'] = feedback_zh
                if fix_tip_en:
                    entry['fix_tip_en'] = fix_tip_en
                if fix_tip_zh:
                    entry['fix_tip_zh'] = fix_tip_zh

            char_analysis.append(entry)

        return char_analysis

    def _lookup_error_info(
        self,
        expected_initial: str,
        actual_initial: str,
        expected_tone: int,
        actual_tone: int,
        expected_final: str = None,
        actual_final: str = None
    ) -> Optional[Dict]:
        """Look up error pattern from database"""

        # Check initial error
        if expected_initial and actual_initial and expected_initial != actual_initial:
            key = (expected_initial, actual_initial)
            if key in self.error_patterns:
                return self.error_patterns[key]

        # Check tone error
        if expected_tone and actual_tone and expected_tone != actual_tone:
            key = f"tone_{expected_tone}_to_{actual_tone}"
            if key in self.error_patterns:
                return self.error_patterns[key]

        return None

    def _get_generic_feedback(self, category: str, initial: str, tone: int) -> Dict[str, str]:
        """Get generic feedback when specific pattern not found"""
        feedbacks = {
            'initial_error': {
                'en': f'Initial sound {initial} was not pronounced correctly',
                'zh': f'声母{initial}发音不正确'
            },
            'tone_error': {
                'en': f'Tone {tone} was not accurate',
                'zh': f'第{tone}声不准确'
            },
            'final_error': {
                'en': 'Final vowel sound needs improvement',
                'zh': '韵母发音需要改进'
            },
            'omission': {
                'en': 'Character was not pronounced',
                'zh': '字符未被朗读'
            }
        }
        return feedbacks.get(category, {'en': 'Needs practice', 'zh': '需要练习'})

    def _get_practice_words(self, initial: str, tone: int) -> List[str]:
        """Get practice words for specific initial or tone"""
        # Common practice words lookup
        words_by_initial = {
            'zh': ['知道', '中国', '吃饭', '车站'],
            'ch': ['吃饭', '出去', '车站', '长江'],
            'sh': ['是的', '老师', '学生', '说话'],
            'r': ['人民', '认识', '日本', '然后'],
            'n': ['努力', '那里', '哪里', '奶奶'],
            'l': ['来了', '了解', '快乐', '道理']
        }
        return words_by_initial.get(initial, ['学习', '练习'])

    def _generate_assessment(
        self,
        overall: float,
        section: int,
        error_summary: Dict
    ) -> Dict[str, str]:
        """Generate overall assessment based on score and section"""

        section_names = {
            1: "Single Characters (讀單音節字詞)",
            2: "Polysyllabic Words (讀多音節詞語)",
            3: "Choice & Judgment (選擇判斷)",
            4: "Reading Passage (朗讀短文)",
            5: "Topic Speaking (命題說話)"
        }

        section_name = section_names.get(section, "Reading")

        # Score-based assessment
        if overall >= 97:
            return {
                'en': f'Excellent! Your {section_name} pronunciation is perfect or near-perfect. Outstanding work!',
                'zh': f'太棒了！你的{section_name}发音完美或接近完美。出色！'
            }
        elif overall >= 92:
            return {
                'en': f'Excellent! Your {section_name} pronunciation is very good with minor areas to refine.',
                'zh': f'优秀！你的{section_name}发音很好，只有一些小地方需要改进。'
            }
        elif overall >= 87:
            return {
                'en': f'Good! Your {section_name} pronunciation is good. Keep practicing to reach excellence.',
                'zh': f'良好！你的{section_name}发音不错。继续练习达到优秀。'
            }
        elif overall >= 80:
            return {
                'en': f'Good pronunciation! Minor areas to improve in {section_name}.',
                'zh': f'发音不错！{section_name}只有一些小问题需要改进。'
            }
        elif overall >= 70:
            return {
                'en': f'Fair pronunciation in {section_name}. Focus on accuracy and consistency.',
                'zh': f'{section_name}发音一般。加强准确性和稳定性练习。'
            }
        elif overall >= 60:
            return {
                'en': f'Basic pronunciation needs work in {section_name}. Focus on tones and initials.',
                'zh': f'{section_name}基础发音需要加强。重点练习声调和声母。'
            }
        else:
            return {
                'en': f'{section_name} needs significant improvement. Start with basic sounds and tones.',
                'zh': f'{section_name}需要大幅改进。从基础音调和声母开始。'
            }

    def _generate_recommendations(
        self,
        errors: List[Dict],
        error_summary: Dict,
        section: int
    ) -> Dict[str, Any]:
        """Generate practice recommendations based on errors"""

        # Count error types
        error_counts = Counter()
        for error in errors:
            category = error.get('category', 'unknown')
            error_counts[category] += 1

        # Determine focus areas
        focus_areas_en = []
        focus_areas_zh = []

        if error_counts.get('initial_error', 0) > 0:
            focus_areas_en.append('Initial consonants (声母)')
            focus_areas_zh.append('声母练习')

        if error_counts.get('tone_error', 0) > 0:
            focus_areas_en.append('Tone practice (声调)')
            focus_areas_zh.append('声调练习')

        if error_counts.get('final_error', 0) > 0:
            focus_areas_en.append('Final vowels (韵母)')
            focus_areas_zh.append('韵母练习')

        if not focus_areas_en:
            focus_areas_en = ['Overall pronunciation']
            focus_areas_zh = ['综合发音']

        # Determine daily duration
        if section in [1, 2]:
            daily_en = '10-15 minutes'
            daily_zh = '10-15分钟'
        elif section == 3:
            daily_en = '15 minutes vocabulary + 10 minutes listening'
            daily_zh = '15分钟词汇 + 10分钟听力'
        elif section == 4:
            daily_en = '15-20 minutes'
            daily_zh = '15-20分钟'
        else:  # Section 5
            daily_en = '20-30 minutes'
            daily_zh = '20-30分钟'

        return {
            'focus_areas_en': focus_areas_en,
            'focus_areas_zh': focus_areas_zh,
            'exercises_en': [
                'Practice reading aloud for 15 minutes daily',
                'Listen to native Mandarin speakers',
                'Record and compare your pronunciation'
            ],
            'exercises_zh': [
                '每天朗读15分钟',
                '听标准普通话录音',
                '录音对比自己的发音'
            ],
            'daily_duration_en': daily_en,
            'daily_duration_zh': daily_zh
        }

    def _generate_encouragement(self, overall: float, section: int) -> Dict[str, str]:
        """Generate encouraging message"""

        if overall >= 90:
            return {
                'en': f'Section {section}: Outstanding performance! You are ready for Level 1 certification!',
                'zh': f'第{section}部分：表现出色！你已准备好考一级！'
            }
        elif overall >= 80:
            return {
                'en': f'Section {section}: Great progress! Keep up the excellent work!',
                'zh': f'第{section}部分：进步很大！继续保持！'
            }
        elif overall >= 70:
            return {
                'en': f'Section {section}: Good progress! Regular practice will help you improve faster.',
                'zh': f'第{section}部分：进步不错！规律练习会让你进步更快。'
            }
        elif overall >= 60:
            return {
                'en': f'Section {section}: Don\'t give up! Start with basics and practice daily.',
                'zh': f'第{section}部分：别气馁！从基础开始，每天练习。'
            }
        else:
            return {
                'en': f'Section {section}: Every expert was once a beginner. Keep practicing!',
                'zh': f'第{section}部分：每个专家都曾是初学者。继续加油！'
            }

    def _generate_tone_analysis(self, errors: List[Dict], scores: Dict = None) -> Dict[str, Any]:
        """Generate tone-specific analysis"""
        tone_errors = [e for e in errors if e.get('category') == 'tone_error']

        # Count tone errors
        tone_counts = {}
        for error in tone_errors:
            expected = error.get('expected_tone', 0)
            actual = error.get('actual_tone', 0)
            if expected and actual:
                key = f"{expected}→{actual}"
                tone_counts[key] = tone_counts.get(key, 0) + 1

        # Calculate totals from scores if available
        tone_score = scores.get('tone', 0) if scores else 0
        total_tones = len(errors) + 10  # Estimate
        correct_tones = int(total_tones * tone_score / 100) if tone_score > 0 else total_tones - len(tone_errors)
        accuracy = f"{tone_score:.0f}%" if tone_score > 0 else f"{((correct_tones/max(total_tones,1))*100):.0f}%"

        return {
            'total_tones': total_tones,
            'correct_tones': correct_tones,
            'tone_accuracy': accuracy,
            'total_tone_errors': len(tone_errors),
            'tone_error_distribution': tone_counts,
            'common_tone_issues': list(tone_counts.keys())[:3]
        }

    def _generate_phoneme_analysis(self, errors: List[Dict], scores: Dict = None) -> Dict[str, Any]:
        """Generate phoneme (initial/final) analysis"""
        initial_errors = [e for e in errors if e.get('category') == 'initial_error']
        final_errors = [e for e in errors if e.get('category') == 'final_error']

        # Count initial errors
        initial_counts = {}
        for error in initial_errors:
            expected = error.get('expected_initial', '')
            actual = error.get('actual_initial', '')
            if expected and actual:
                key = f"{expected}/{actual}"
                initial_counts[key] = initial_counts.get(key, 0) + 1

        # Count final errors
        final_counts = {}
        for error in final_errors:
            expected = error.get('expected_final', '')
            actual = error.get('actual_final', '')
            if expected and actual:
                key = f"{expected}/{actual}"
                final_counts[key] = final_counts.get(key, 0) + 1

        # Get pronunciation score for accuracy calculation
        pron_score = scores.get('pronunciation', 0) if scores else 0

        return {
            'pronunciation_accuracy': f"{pron_score:.0f}%" if pron_score > 0 else "N/A",
            'total_initial_errors': len(initial_errors),
            'total_final_errors': len(final_errors),
            'initial_error_distribution': initial_counts,
            'final_error_distribution': final_counts,
            'consonant_issues': list(initial_counts.keys())[:3],
            'vowel_issues': list(final_counts.keys())[:3],
            'common_initial_issues': list(initial_counts.keys())[:3],
            'common_final_issues': list(final_counts.keys())[:3]
        }

    def _get_key_issues(self, errors: List[Dict]) -> Dict[str, List[str]]:
        """Get key issues from errors"""
        issues_en = []
        issues_zh = []

        # Count by category
        initial_errors = sum(1 for e in errors if e.get('category') == 'initial_error')
        tone_errors = sum(1 for e in errors if e.get('category') == 'tone_error')
        final_errors = sum(1 for e in errors if e.get('category') == 'final_error')

        if initial_errors > 0:
            issues_en.append(f'{initial_errors} initial consonant errors')
            issues_zh.append(f'{initial_errors}个声母错误')

        if tone_errors > 0:
            issues_en.append(f'{tone_errors} tone errors')
            issues_zh.append(f'{tone_errors}个声调错误')

        if final_errors > 0:
            issues_en.append(f'{final_errors} final vowel errors')
            issues_zh.append(f'{final_errors}个韵母错误')

        return {'en': issues_en, 'zh': issues_zh}

    def _get_improvement_tips(self, errors: List[Dict]) -> Dict[str, List[str]]:
        """Get improvement tips based on errors"""
        tips_en = []
        tips_zh = []

        # Count by category
        initial_errors = sum(1 for e in errors if e.get('category') == 'initial_error')
        tone_errors = sum(1 for e in errors if e.get('category') == 'tone_error')

        if initial_errors > tone_errors:
            tips_en.append('Focus on initial consonants - practice zh/ch/sh retroflex sounds')
            tips_zh.append('重点练习声母 - 翘舌音zh/ch/sh')
            tips_en.append('Pay attention to n/l and zh/z distinctions')
            tips_zh.append('注意n/l和zh/z区分')
        elif tone_errors > initial_errors:
            tips_en.append('Focus on tone practice - especially third tone dipping')
            tips_zh.append('重点练习声调 - 特别是第三声')
            tips_en.append('Practice tone pairs daily')
            tips_zh.append('每天练习声调对')
        else:
            tips_en.append('Balance practice between tones and consonants')
            tips_zh.append('平衡声调和声母练习')

        return {'en': tips_en, 'zh': tips_zh}


# Convenience function
def generate_feedback(
    errors: List[Dict],
    scores: Dict[str, float],
    section: int,
    error_summary: Dict[str, Any],
    expected_text: str = "",
    transcription: str = ""
) -> Dict[str, Any]:
    """Generate comprehensive feedback"""
    generator = FeedbackGenerator()
    return generator.generate(errors, scores, section, error_summary, expected_text, transcription)
