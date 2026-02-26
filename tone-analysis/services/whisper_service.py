"""
Whisper Service
Speech-to-text transcription using Faster Whisper (open-source, no API key needed)
"""

import logging
from typing import Optional, Dict, List
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class WhisperService:
    """Whisper-based speech recognition service using Faster Whisper"""
    
    # Model options: tiny, base, small, medium, large
    DEFAULT_MODEL = "base"
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Faster Whisper model"""
        try:
            logger.info(f"Loading Faster Whisper model: {self.model_name}")
            
            # Faster Whisper uses different model naming
            # tiny, base, small, medium, large-v1, large-v2
            model_size = self.model_name
            
            # Load model - using CPU with int8 for speed
            self.model = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8"
            )
            
            logger.info(f"Faster Whisper model loaded successfully: {model_size}")
            
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def transcribe(self, audio_path: str, language: str = "zh") -> Dict:
        """
        Transcribe audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (zh for Chinese)
            
        Returns:
            Dict with transcription and metadata
        """
        try:
            logger.info(f"Transcribing: {audio_path}")
            
            # Run transcription
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                vad_filter=True,  # Voice activity detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Collect all segments
            transcription = ""
            segments_list = []
            
            for segment in segments:
                transcription += segment.text
                segments_list.append({
                    "text": segment.text,
                    "start": segment.start,
                    "end": segment.end,
                })
            
            transcription = transcription.strip()
            
            logger.info(f"Transcription complete: {transcription[:100]}...")
            
            return {
                "success": True,
                "text": transcription,
                "language": info.language if info.language else "zh",
                "segments": segments_list,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def compare_texts(self, expected: str, actual: str) -> Dict:
        """
        Compare expected text with actual transcription
        
        Args:
            expected: What user should have said
            actual: What Whisper transcribed
            
        Returns:
            Dict with comparison results
        """
        import re
        
        # Normalize texts - keep only Chinese characters
        expected_clean = re.sub(r'[^\u4e00-\u9fff]', '', expected)
        actual_clean = re.sub(r'[^\u4e00-\u9fff]', '', actual.lower())
        
        # Calculate match percentage
        if not expected_clean:
            return {
                "match_percentage": 0,
                "missing": [],
                "extra": [],
                "errors": []
            }
        
        expected_chars = list(expected_clean)
        actual_chars = list(actual_clean)
        
        # Simple comparison
        missing = []
        extra = []
        
        # Find missing characters
        for i, char in enumerate(expected_chars):
            if i >= len(actual_chars) or actual_chars[i] != char:
                missing.append({
                    "char": char,
                    "position": i
                })
        
        # Find extra characters
        for i, char in enumerate(actual_chars):
            if i >= len(expected_chars) or expected_chars[i] != char:
                extra.append({
                    "char": char,
                    "position": i
                })
        
        # Calculate match percentage
        correct = len(expected_chars) - len(missing)
        match_percentage = (correct / len(expected_chars) * 100) if expected_chars else 0
        
        return {
            "match_percentage": round(match_percentage, 2),
            "expected": expected_clean,
            "actual": actual_clean,
            "missing": missing,
            "extra": extra,
            "correct_count": correct,
            "expected_count": len(expected_chars)
        }
    
    def analyze(self, audio_path: str, expected_text: str = "") -> Dict:
        """
        Full analysis combining transcription and comparison
        
        Args:
            audio_path: Path to audio file
            expected_text: What user should have said
            
        Returns:
            Complete analysis result
        """
        # Step 1: Transcribe
        transcribe_result = self.transcribe(audio_path)
        
        if not transcribe_result.get("success"):
            return {
                "success": False,
                "error": transcribe_result.get("error", "Transcription failed")
            }
        
        # Step 2: Compare with expected
        if expected_text:
            comparison = self.compare_texts(
                expected_text,
                transcribe_result["text"]
            )
        
        return {
            "success": True,
            "transcription": transcribe_result["text"],
            "match_percentage": comparison.get("match_percentage", 0) if expected_text else 100,
            "comparison": comparison if expected_text else {},
            "model": self.model_name,
            "language": transcribe_result.get("language", "zh")
        }


# Global instance (lazy loaded)
_whisper_service: Optional[WhisperService] = None


def get_whisper_service(model: str = "base") -> WhisperService:
    """Get or create Whisper service instance"""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService(model)
    return _whisper_service


def transcribe_audio(audio_path: str, expected_text: str = "") -> Dict:
    """Convenience function for transcription"""
    service = get_whisper_service()
    if expected_text:
        return service.analyze(audio_path, expected_text)
    return service.transcribe(audio_path)
