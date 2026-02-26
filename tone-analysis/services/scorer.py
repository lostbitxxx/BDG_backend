"""
Scoring Service
Calculates pronunciation scores based on analysis results
"""

import logging
from typing import Dict, List, Optional
from .pinyin_db import get_char_info, is_retroflex, is_nasal

logger = logging.getLogger(__name__)


class Scorer:
    """
    Calculate pronunciation scores
    
    Score Components:
    - Pronunciation: How correctly user pronounced the text
    - Tone: Accuracy of tone production
    - Fluency: Speaking pace and smoothness
    - Overall: Weighted final score
    """
    
    # Score weights
    WEIGHTS = {
        "transcription_match": 0.30,  # How much matched expected text
        "phoneme_accuracy": 0.30,     # Correct phonemes
        "tone_accuracy": 0.25,        # Correct tones
        "fluency": 0.15              # Speaking flow
    }
    
    def __init__(self):
        pass
    
    def calculate_phoneme_accuracy(
        self, 
        expected: str, 
        actual: str
    ) -> Dict:
        """
        Calculate phoneme-level accuracy
        
        Focus on areas Cantonese speakers struggle with:
        - Retroflex initials (zh, ch, sh, r)
        - Nasal finals (an, en, in, ang, eng, etc.)
        """
        retroflex_errors = []
        nasal_errors = []
        other_errors = []
        
        expected_chars = list(expected)
        actual_chars = list(actual)
        
        for i, (exp, act) in enumerate(zip(expected_chars, actual_chars)):
            if exp == act:
                continue
            
            exp_info = get_char_info(exp)
            act_info = get_char_info(act)
            
            if not exp_info:
                continue
            
            # Check retroflex errors
            if exp_info.get("is_retroflex") and act_info:
                if exp_info.get("initial") != act_info.get("initial"):
                    retroflex_errors.append({
                        "position": i,
                        "char": exp,
                        "expected": exp_info.get("initial"),
                        "detected": act_info.get("initial", "unknown"),
                        "type": "retroflex"
                    })
            
            # Check nasal errors
            elif exp_info.get("is_nasal") and act_info:
                if exp_info.get("final") != act_info.get("final"):
                    nasal_errors.append({
                        "position": i,
                        "char": exp,
                        "expected": exp_info.get("final"),
                        "detected": act_info.get("final", "unknown"),
                        "type": "nasal"
                    })
            
            # Other errors
            else:
                other_errors.append({
                    "position": i,
                    "char": exp,
                    "expected": exp,
                    "detected": act,
                    "type": "other"
                })
        
        # Calculate accuracy
        total_chars = len(expected_chars)
        if total_chars == 0:
            phoneme_accuracy = 100.0
        else:
            correct = total_chars - len(retroflex_errors) - len(nasal_errors) - len(other_errors)
            phoneme_accuracy = (correct / total_chars) * 100
        
        return {
            "accuracy": round(phoneme_accuracy, 2),
            "total_chars": total_chars,
            "correct": total_chars - len(retroflex_errors) - len(nasal_errors) - len(other_errors),
            "errors": {
                "retroflex": retroflex_errors,
                "nasal": nasal_errors,
                "other": other_errors
            }
        }
    
    def calculate_tone_score(
        self, 
        tone_analysis: Dict,
        expected_text: str = ""
    ) -> Dict:
        """
        Calculate tone accuracy score
        """
        if not tone_analysis.get("success", False):
            return {
                "accuracy": 0,
                "error": tone_analysis.get("error", "Analysis failed")
            }
        
        # Get expected tones from text
        expected_tones = []
        for char in expected_text:
            info = get_char_info(char)
            if info:
                expected_tones.append(info.get("tone", 0))
        
        # Get detected tones from analysis
        detected_tones = tone_analysis.get("detected_tone", 0)
        
        # Simple comparison (can be enhanced)
        if expected_tones and detected_tones != 0:
            # Check if first detected tone matches expected
            if detected_tones == expected_tones[0]:
                tone_accuracy = 85.0
            else:
                tone_accuracy = 50.0
        else:
            # Use default if can't detect
            tone_accuracy = tone_analysis.get("tone_accuracy", 70.0)
        
        return {
            "accuracy": round(tone_accuracy, 2),
            "detected_tone": detected_tones,
            "expected_tones": expected_tones[:5],  # First 5
            "errors": tone_analysis.get("tone_errors", [])
        }
    
    def calculate_fluency(self, audio_duration: float, text_length: int) -> Dict:
        """
        Calculate fluency score based on speaking pace
        
        Ideal speaking rate: ~200-250 characters per minute for Mandarin
        """
        if audio_duration <= 0 or text_length <= 0:
            return {
                "score": 0,
                "reason": "Invalid duration or text"
            }
        
        # Characters per minute
        cpm = (text_length / audio_duration) * 60
        
        # Ideal range: 150-250 cpm
        if 150 <= cpm <= 250:
            # Perfect range
            base_score = 100 - abs(cpm - 200) / 2
        elif cpm < 150:
            # Too slow
            base_score = max(50, 100 - (150 - cpm))
        else:
            # Too fast
            base_score = max(50, 100 - (cpm - 250) / 2)
        
        return {
            "score": round(base_score, 1),
            "cpm": round(cpm, 1),
            "rating": "too_slow" if cpm < 150 else ("too_fast" if cpm > 250 else "good")
        }
    
    def calculate_overall_score(self, components: Dict) -> Dict:
        """
        Calculate weighted overall score
        """
        # Get component scores (default to 0 if missing)
        transcription = components.get("transcription_match", 0)
        phoneme = components.get("phoneme_accuracy", 0)
        tone = components.get("tone_accuracy", 0)
        fluency = components.get("fluency", 0)
        
        # Calculate weighted overall
        overall = (
            transcription * self.WEIGHTS["transcription_match"] +
            phoneme * self.WEIGHTS["phoneme_accuracy"] +
            tone * self.WEIGHTS["tone_accuracy"] +
            fluency * self.WEIGHTS["fluency"]
        )
        
        # Determine grade
        if overall >= 97:
            grade = "1-A"
            level = 1
        elif overall >= 92:
            grade = "1-B"
            level = 1
        elif overall >= 87:
            grade = "2-A"
            level = 2
        elif overall >= 80:
            grade = "2-B"
            level = 2
        elif overall >= 70:
            grade = "3-A"
            level = 3
        else:
            grade = "3-B"
            level = 3
        
        return {
            "overall": round(overall, 1),
            "grade": grade,
            "level": level,
            "pass": overall >= 80
        }
    
    def score(
        self,
        transcription_result: Dict,
        tone_analysis: Dict,
        expected_text: str,
        audio_duration: float
    ) -> Dict:
        """
        Calculate complete score breakdown
        """
        # Transcription match
        transcription_match = transcription_result.get("match_percentage", 0)
        
        # Phoneme accuracy
        actual_text = transcription_result.get("transcription", "")
        phoneme_result = self.calculate_phoneme_accuracy(expected_text, actual_text)
        
        # Tone score
        tone_result = self.calculate_tone_score(tone_analysis, expected_text)
        
        # Fluency
        fluency_result = self.calculate_fluency(audio_duration, len(expected_text))
        
        # Combine components
        components = {
            "transcription_match": transcription_match,
            "phoneme_accuracy": phoneme_result.get("accuracy", 0),
            "tone_accuracy": tone_result.get("accuracy", 0),
            "fluency": fluency_result.get("score", 0)
        }
        
        # Calculate overall
        overall = self.calculate_overall_score(components)
        
        return {
            "success": True,
            "pronunciation": round(components["transcription_match"] * 0.3 + 
                                  components["phoneme_accuracy"] * 0.4 +
                                  components["tone_accuracy"] * 0.3, 1),
            "tone": tone_result.get("accuracy", 0),
            "fluency": fluency_result.get("score", 0),
            "overall": overall["overall"],
            "grade": overall["grade"],
            "level": overall["level"],
            "pass": overall["pass"],
            "details": {
                "transcription_match": transcription_match,
                "phoneme_accuracy": phoneme_result.get("accuracy", 0),
                "phoneme_errors": phoneme_result.get("errors", {}),
                "tone_accuracy": tone_result.get("accuracy", 0),
                "tone_errors": tone_result.get("errors", []),
                "fluency": fluency_result.get("score", 0),
                "speaking_rate_cpm": fluency_result.get("cpm", 0)
            }
        }


# Global instance
_scorer: Optional[Scorer] = None


def get_scorer() -> Scorer:
    """Get or create scorer instance"""
    global _scorer
    if _scorer is None:
        _scorer = Scorer()
    return _scorer


def calculate_scores(
    transcription_result: Dict,
    tone_analysis: Dict,
    expected_text: str,
    audio_duration: float
) -> Dict:
    """Convenience function for scoring"""
    scorer = get_scorer()
    return scorer.score(transcription_result, tone_analysis, expected_text, audio_duration)
