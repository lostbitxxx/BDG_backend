"""
ElevenLabs Transcription Service
Transcribes audio using ElevenLabs API
"""

import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ElevenLabsTranscriber:
    """Transcribes audio using ElevenLabs API"""

    def __init__(self):
        self.api_key = os.environ.get('ELEVENLABS_API_KEY')
        self.base_url = "https://api.elevenlabs.io"
        self.model_id = "scribe_v2"  # Scribe v2 transcription model

    def transcribe(self, audio_path: str, language: str = "zh") -> Dict[str, Any]:
        """
        Transcribe audio file using ElevenLabs API

        Args:
            audio_path: Path to the audio file
            language: Language code (zh for Chinese, auto for automatic detection)

        Returns:
            Dict with transcription and metadata
        """
        if not self.api_key or self.api_key == 'your_elevenlabs_api_key_here':
            logger.error("ElevenLabs API key not configured")
            return {
                'success': False,
                'error': 'ElevenLabs API key not configured. Please add ELEVENLABS_API_KEY to .env'
            }

        try:
            logger.info(f"ElevenLabs API Key present: {bool(self.api_key)}")
            logger.info(f"Model ID: {self.model_id}")
            logger.info(f"Language: {language}")

            # Open audio file
            with open(audio_path, 'rb') as audio_file:
                # Build multipart form data - model_id as form field, not JSON
                files = {
                    'file': (os.path.basename(audio_path), audio_file, 'audio/webm'),
                    'model_id': (None, self.model_id),
                }

                # Add language_code if provided
                if language and language != 'auto':
                    files['language_code'] = (None, language)

                headers = {
                    'xi-api-key': self.api_key
                }

                logger.info(f"Calling ElevenLabs transcription API...")

                # ElevenLabs speech-to-text endpoint
                endpoint = f"{self.base_url}/v1/speech-to-text"

                logger.info(f"Using endpoint: {endpoint}")

                try:
                    response = requests.post(
                        endpoint,
                        files=files,
                        headers=headers,
                        timeout=120
                    )
                except Exception as e:
                    error_msg = f"ElevenLabs request failed: {str(e)}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }

                if response.status_code != 200:
                    error_msg = f"ElevenLabs API error: {response.status_code} - {response.text[:200]}"
                    logger.error(error_msg)
                    return {
                        'success': False,
                        'error': error_msg
                    }

                # Success - parse response
                result = response.json()
                transcription = result.get('text', '')

                logger.info(f"Transcription successful: {transcription[:100]}...")

                return {
                    'success': True,
                    'transcription': transcription,
                    'language': result.get('language', language),
                    'model': self.model_id
                }

        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_path}")
            return {
                'success': False,
                'error': 'Audio file not found'
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {
                'success': False,
                'error': f'Request error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using simple character-based comparison
    Returns a score between 0 and 100
    """
    if not text1 or not text2:
        return 0.0

    # Remove spaces and convert to lowercase for comparison
    t1 = text1.replace(' ', '').lower()
    t2 = text2.replace(' ', '').lower()

    if t1 == t2:
        return 100.0

    # Simple character-level similarity
    len1, len2 = len(t1), len(t2)
    if len1 == 0 or len2 == 0:
        return 0.0

    # Count matching characters at same position
    matches = sum(1 for i in range(min(len1, len2)) if t1[i] == t2[i])

    # Calculate similarity as a percentage
    similarity = (matches / max(len1, len2)) * 100

    return round(similarity, 2)


def generate_simple_scores(transcription: str, expected_text: str) -> Dict[str, float]:
    """
    Generate simple similarity-based scores
    Note: These are NOT pronunciation/tone scores - just text matching scores
    """
    similarity = calculate_text_similarity(transcription, expected_text)

    # Convert similarity to a score (capped at 100)
    overall = min(similarity, 100.0)

    return {
        'pronunciation': overall * 0.4,  # Weight: 40%
        'fluency': overall * 0.3,         # Weight: 30%
        'tone': overall * 0.3,            # Weight: 30%
        'overall': overall
    }


def identify_errors(transcription: str, expected_text: str) -> list:
    """
    Identify errors by comparing transcribed text with expected text
    Returns list of error descriptions
    """
    errors = []

    if not transcription:
        errors.append({
            'type': 'no_speech',
            'description': 'No speech detected in audio'
        })
        return errors

    # Simple character-by-character comparison
    trans_chars = list(transcription.replace(' ', ''))
    expected_chars = list(expected_text.replace(' ', ''))

    i, j = 0, 0
    missing = []
    extra = []

    while i < len(trans_chars) or j < len(expected_chars):
        if i >= len(trans_chars):
            missing.append(expected_chars[j])
            j += 1
        elif j >= len(expected_chars):
            extra.append(trans_chars[i])
            i += 1
        elif trans_chars[i] == expected_chars[j]:
            i += 1
            j += 1
        else:
            # Character mismatch - could be substitution or different word
            # For simplicity, we record as potential issue
            j += 1  # Skip expected to continue

    if missing:
        errors.append({
            'type': 'missing_chars',
            'description': f"Missing characters: {''.join(missing[:5])}{'...' if len(missing) > 5 else ''}",
            'count': len(missing)
        })

    if extra:
        errors.append({
            'type': 'extra_chars',
            'description': f"Extra characters: {''.join(extra[:5])}{'...' if len(extra) > 5 else ''}",
            'count': len(extra)
        })

    return errors
