"""
Tone Analyzer Service
Analyzes Mandarin Chinese tones from audio using pitch detection
"""

import numpy as np
import librosa
import logging
from typing import Dict, List, Optional, Tuple
import os

logger = logging.getLogger(__name__)


class ToneAnalyzer:
    """
    Analyze Mandarin Chinese tones from audio
    
    Tone patterns:
    - Tone 1 (高平): Flat, high pitch ~300Hz
    - Tone 2 (上升): Rising from low to high
    - Tone 3 (降升): Dipping low then rising
    - Tone 4 (降): Falling from high to low
    - Tone 0 (轻声): Short, low, no clear contour
    """
    
    # Tone detection parameters
    SAMPLE_RATE = 16000
    HOP_LENGTH = 512
    FRAME_LENGTH = 2048
    
    # Tone pitch ranges (in Hz) for different tones
    # These are approximate and vary by speaker
    TONE_F0_RANGES = {
        1: (250, 350),  # High flat
        2: (200, 350),  # Rising
        3: (180, 300),  # Dipping
        4: (350, 150),  # Falling
    }
    
    def __init__(self):
        self.min_freq = 80   # Minimum pitch frequency (Hz)
        self.max_freq = 500  # Maximum pitch frequency (Hz)
    
    def extract_pitch(self, audio_path: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Extract pitch contour from audio using librosa
        
        Returns:
            Tuple of (times, pitches) or None if failed
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.SAMPLE_RATE)
            
            # Extract pitch using pyin algorithm
            # f0: fundamental frequency
            # voiced_flag: whether frame is voiced
            # voiced_probs: probability of being voiced
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=librosa.note_to_hz('E2'),  # ~82 Hz
                fmax=librosa.note_to_hz('C6'),  # ~1047 Hz
                sr=sr,
                hop_length=self.HOP_LENGTH
            )
            
            # Replace NaN values with interpolation
            f0 = np.nan_to_num(f0, nan=0.0)
            
            # Create time array
            times = librosa.times_like(f0, sr=sr, hop_length=self.HOP_LENGTH)
            
            # Filter out unvoiced frames
            voiced_times = times[voiced_flag & (f0 > self.min_freq)]
            voiced_pitches = f0[voiced_flag & (f0 > self.min_freq)]
            
            if len(voiced_pitches) == 0:
                logger.warning("No voiced segments detected")
                return None
            
            return (voiced_times, voiced_pitches)
            
        except Exception as e:
            logger.error(f"Pitch extraction error: {e}")
            return None
    
    def detect_tone_contour(self, pitches: np.ndarray, times: np.ndarray) -> Dict:
        """
        Detect the overall tone contour from pitch sequence
        
        Returns:
            Dict with tone type and confidence
        """
        if len(pitches) < 3:
            return {"tone": 0, "confidence": 0, "pattern": "unknown"}
        
        # Get start, middle, and end pitches
        start_pitch = np.mean(pitches[:len(pitches)//3])
        mid_pitch = np.mean(pitches[len(pitches)//3:2*len(pitches)//3])
        end_pitch = np.mean(pitches[2*len(pitches)//3:])
        
        # Calculate pitch changes
        rise = end_pitch - start_pitch
        fall = start_pitch - end_pitch
        
        # Tone classification
        # Tone 1: Flat (small change)
        if abs(rise) < 30:
            tone = 1
            confidence = 0.8
        
        # Tone 2: Rising
        elif rise > 30 and rise < 150:
            tone = 2
            confidence = 0.7
        
        # Tone 3: Dipping
        elif start_pitch > mid_pitch and end_pitch > mid_pitch:
            tone = 3
            confidence = 0.6
        
        # Tone 4: Falling
        elif rise < -30:
            tone = 4
            confidence = 0.7
        
        else:
            tone = 0  # Neutral
            confidence = 0.5
        
        return {
            "tone": tone,
            "confidence": confidence,
            "start_pitch": round(start_pitch, 1),
            "end_pitch": round(end_pitch, 1),
            "rise": round(rise, 1)
        }
    
    def segment_by_energy(self, audio_path: str) -> List[Tuple[float, float]]:
        """
        Segment audio by energy/amplitude to find word boundaries
        
        Returns:
            List of (start_time, end_time) segments
        """
        try:
            y, sr = librosa.load(audio_path, sr=self.SAMPLE_RATE)
            
            # Calculate RMS energy
            hop = self.HOP_LENGTH
            rms = librosa.feature.rms(y=y, hop_length=hop)[0]
            
            # Get times
            times = librosa.times_like(rms, sr=sr, hop_length=hop)
            
            # Find segments where energy is above threshold
            threshold = np.mean(rms) * 0.3
            above_threshold = rms > threshold
            
            # Find contiguous segments
            segments = []
            start = None
            
            for i, is_above in enumerate(above_threshold):
                if is_above and start is None:
                    start = times[i]
                elif not is_above and start is not None:
                    segments.append((start, times[i]))
                    start = None
            
            # Handle last segment
            if start is not None:
                segments.append((start, times[-1]))
            
            # Filter out very short segments
            segments = [(s, e) for s, e in segments if e - s > 0.1]
            
            return segments
            
        except Exception as e:
            logger.error(f"Segmentation error: {e}")
            return [(0.0, 10.0)]  # Return entire audio as one segment
    
    def analyze_tones(self, audio_path: str, expected_chars: List[str]) -> Dict:
        """
        Full tone analysis
        
        Args:
            audio_path: Path to audio file
            expected_chars: List of expected characters
            
        Returns:
            Dict with tone analysis results
        """
        # Extract pitch
        pitch_data = self.extract_pitch(audio_path)
        
        if pitch_data is None:
            return {
                "success": False,
                "error": "Could not extract pitch from audio"
            }
        
        times, pitches = pitch_data
        
        # Segment audio
        segments = self.segment_by_energy(audio_path)
        
        # Analyze overall contour
        contour = self.detect_tone_contour(pitches, times)
        
        # Compare with expected tones
        tone_errors = []
        
        if expected_chars:
            # Get expected tones
            from .pinyin_db import get_char_info
            
            expected_tones = []
            for char in expected_chars:
                info = get_char_info(char)
                if info:
                    expected_tones.append(info.get("tone", 0))
            
            # Compare (simplified - assumes 1 char = 1 segment)
            num_expected = len(expected_tones)
            num_segments = len(segments)
            
            if num_expected > 0 and num_segments > 0:
                # Calculate tone accuracy
                # This is simplified - in production would do segment-by-segment
                tone_accuracy = 70.0  # Placeholder
                
                if contour["tone"] != 0:
                    # Check if detected tone matches expected
                    if num_expected <= num_segments:
                        expected = expected_tones[0]
                        if contour["tone"] != expected:
                            tone_errors.append({
                                "position": 0,
                                "expected": expected,
                                "detected": contour["tone"]
                            })
                            tone_accuracy = 50.0
                        else:
                            tone_accuracy = 85.0
        
        return {
            "success": True,
            "detected_tone": contour["tone"],
            "tone_name": ["neutral", "flat", "rising", "dipping", "falling"][contour["tone"]],
            "confidence": contour["confidence"],
            "start_pitch": contour.get("start_pitch"),
            "end_pitch": contour.get("end_pitch"),
            "tone_accuracy": tone_accuracy if 'tone_accuracy' in dir() else 70.0,
            "tone_errors": tone_errors,
            "segments": len(segments)
        }


# Global instance
_tone_analyzer: Optional[ToneAnalyzer] = None


def get_tone_analyzer() -> ToneAnalyzer:
    """Get or create tone analyzer instance"""
    global _tone_analyzer
    if _tone_analyzer is None:
        _tone_analyzer = ToneAnalyzer()
    return _tone_analyzer


def analyze_tones(audio_path: str, expected_chars: List[str] = None) -> Dict:
    """Convenience function for tone analysis"""
    analyzer = get_tone_analyzer()
    return analyzer.analyze_tones(audio_path, expected_chars or [])
