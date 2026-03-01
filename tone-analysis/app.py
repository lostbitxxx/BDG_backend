"""
BoDongGua Audio Analysis API
Using Faster Whisper for local transcription + tone analysis
Fixed version with real scoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os
import time
import re

# Load .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from services.audio_preprocessor import AudioPreprocessor
from services.whisper_service import WhisperService
from services.tone_analyzer import ToneAnalyzer
from services.pinyin_db import get_char_info, analyze_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['TIMEOUT'] = 180

# Global services
_whisper_service = None
_tone_analyzer = None


def get_whisper_service():
    global _whisper_service
    if _whisper_service is None:
        logger.info("Loading Whisper service...")
        _whisper_service = WhisperService("base")
    return _whisper_service


def get_tone_analyzer():
    global _tone_analyzer
    if _tone_analyzer is None:
        logger.info("Loading Tone Analyzer...")
        _tone_analyzer = ToneAnalyzer()
    return _tone_analyzer


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'tone-analysis',
        'engine': 'Faster Whisper + Tone Analysis (Local)',
        'whisper_ready': _whisper_service is not None
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint using local Whisper + Tone Analysis"""
    start_time = time.time()
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
    
    audio_url = data.get('audio_url')
    expected_text = data.get('expected_text', '')
    section = data.get('section', 4)
    
    if not audio_url:
        return jsonify({'success': False, 'error': 'audio_url is required'}), 400
    
    logger.info(f"Analyzing: {audio_url}")
    logger.info(f"Expected text: {expected_text}")
    
    # Preprocess audio
    preprocessor = AudioPreprocessor()
    processed_audio = None
    
    try:
        logger.info("Step 1: Downloading and validating audio...")
        processed_audio = preprocessor.process(audio_url)
        
        if not processed_audio:
            return jsonify({'success': False, 'error': 'Failed to download/process audio'}), 400
        
        # Get audio duration for analysis
        audio_duration = preprocessor.get_duration(processed_audio)
        audio_size = os.path.getsize(processed_audio)
        
        logger.info(f"Audio duration: {audio_duration}s, size: {audio_size} bytes")
        
        # Check if audio is too short or empty
        if not audio_duration or audio_duration < 0.5:
            return jsonify({
                'success': True,
                'transcription': '',
                'expected': expected_text,
                'scores': {
                    'overall': 0,
                    'pronunciation': 0,
                    'tone': 0,
                    'fluency': 0,
                    'level': 'Below Level 3',
                    'grade': 'C',
                    'pass': False,
                    'details': {'error': 'Audio too short or empty'}
                },
                'feedback': '请录音后再试 (Please record and try again)',
                'processing_time': round(time.time() - start_time, 2),
                'engine': 'local'
            })
        
        # Check if audio is likely silence/noise
        if audio_size < 1000:
            return jsonify({
                'success': True,
                'transcription': '',
                'expected': expected_text,
                'scores': {
                    'overall': 0,
                    'pronunciation': 0,
                    'tone': 0,
                    'fluency': 0,
                    'level': 'Below Level 3',
                    'grade': 'C',
                    'pass': False,
                    'details': {'error': 'No speech detected - audio too short or silent'}
                },
                'feedback': '请录音后再试 (Please record and try again)',
                'processing_time': round(time.time() - start_time, 2),
                'engine': 'local'
            })
        
        # Step 2: Transcribe with Whisper
        logger.info("Step 2: Transcribing with Whisper...")
        whisper = get_whisper_service()
        
        transcription_result = whisper.transcribe(processed_audio, language='zh')
        
        transcription = ''
        if transcription_result.get('success'):
            transcription = transcription_result.get('text', '').strip()
            logger.info(f"Transcription: {transcription}")
        else:
            logger.warning(f"Whisper transcription failed: {transcription_result.get('error')}")
        
        # Step 3: Analyze pronunciation (text comparison)
        logger.info("Step 3: Analyzing pronunciation...")
        pronunciation_score, pronunciation_details = analyze_pronunciation(
            expected_text, 
            transcription
        )
        
        # Step 4: Analyze tones
        logger.info("Step 4: Analyzing tones...")
        tone_score, tone_details = analyze_tones_local(
            processed_audio, 
            expected_text
        )
        
        # Step 5: Analyze fluency
        logger.info("Step 5: Analyzing fluency...")
        fluency_score, fluency_details = analyze_fluency(
            audio_duration,
            transcription,
            expected_text
        )
        
        # Calculate overall score
        overall = (pronunciation_score * 0.4 + tone_score * 0.3 + fluency_score * 0.3)
        
        # Determine level
        if overall >= 97:
            level, grade = 'Level 1', 'A'
        elif overall >= 92:
            level, grade = 'Level 1', 'B'
        elif overall >= 87:
            level, grade = 'Level 2', 'A'
        elif overall >= 80:
            level, grade = 'Level 2', 'B'
        elif overall >= 70:
            level, grade = 'Level 3', 'A'
        elif overall >= 60:
            level, grade = 'Level 3', 'B'
        else:
            level, grade = 'Below Level 3', 'C'
        
        # Generate feedback
        feedback = generate_feedback(overall, level, grade, pronunciation_details, tone_details)
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'success': True,
            'transcription': transcription or '[未能识别语音]',
            'expected': expected_text,
            'scores': {
                'overall': round(overall, 1),
                'pronunciation': round(pronunciation_score, 1),
                'tone': round(tone_score, 1),
                'fluency': round(fluency_score, 1),
                'level': level,
                'grade': grade,
                'pass': overall >= 60,
                'details': {
                    'pronunciation': pronunciation_details,
                    'tone': tone_details,
                    'fluency': fluency_details,
                    'audio_duration': round(audio_duration, 2),
                    'audio_size': audio_size
                }
            },
            'feedback': feedback,
            'processing_time': processing_time,
            'engine': 'local-faster-whisper'
        })
            
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if preprocessor:
            preprocessor.cleanup()


def analyze_pronunciation(expected: str, actual: str) -> tuple:
    """
    Analyze pronunciation by comparing expected vs actual text
    Returns: (score, details)
    """
    # Normalize texts - keep only Chinese characters
    expected_clean = re.sub(r'[^\u4e00-\u9fff]', '', expected)
    actual_clean = re.sub(r'[^\u4e00-\u9fff]', '', actual.lower())
    
    if not expected_clean:
        return 0, {'error': 'No expected text provided'}
    
    if not actual_clean:
        return 10, {
            'expected': expected_clean,
            'actual': '',
            'correct': 0,
            'total': len(expected_clean),
            'match_rate': 0,
            'errors': []
        }
    
    # Character-by-character comparison
    expected_chars = list(expected_clean)
    actual_chars = list(actual_clean)
    
    correct = 0
    errors = []
    
    min_len = min(len(expected_chars), len(actual_chars))
    
    for i in range(min_len):
        if expected_chars[i] == actual_chars[i]:
            correct += 1
        else:
            errors.append({
                'position': i,
                'expected': expected_chars[i],
                'actual': actual_chars[i]
            })
    
    # Handle length differences
    # If actual is shorter, remaining expected chars are "missing"
    if len(actual_chars) < len(expected_chars):
        for i in range(len(actual_chars), len(expected_chars)):
            errors.append({
                'position': i,
                'expected': expected_chars[i],
                'actual': '[缺失]'
            })
    
    # If actual is longer, extra chars are "wrong"
    if len(actual_chars) > len(expected_chars):
        for i in range(len(expected_chars), len(actual_chars)):
            errors.append({
                'position': i,
                'expected': '[多余]',
                'actual': actual_chars[i]
            })
    
    # Calculate match rate
    match_rate = (correct / len(expected_chars)) * 100 if expected_chars else 0
    
    # Score: if 100% match = 100, decreases proportionally
    # But apply a penalty for partial matches
    if match_rate >= 95:
        score = 100
    elif match_rate >= 90:
        score = 90 + (match_rate - 90) * 2  # 90-100
    elif match_rate >= 70:
        score = 70 + (match_rate - 70) * 0.75  # 70-90
    else:
        score = match_rate * 0.9  # 0-70
    
    details = {
        'expected': expected_clean,
        'actual': actual_clean,
        'correct': correct,
        'total': len(expected_chars),
        'match_rate': round(match_rate, 1),
        'errors': errors[:10]  # Limit to first 10 errors
    }
    
    return round(score, 1), details


def analyze_tones_local(audio_path: str, expected_text: str) -> tuple:
    """
    Analyze tones using both text analysis and audio pitch detection
    Returns: (score, details)
    """
    # First, analyze expected tones from text
    expected_clean = re.sub(r'[^\u4e00-\u9fff]', '', expected_text)
    
    if not expected_clean:
        return 50, {'error': 'No text to analyze'}
    
    # Get expected tones from pinyin
    expected_tones = []
    char_infos = []
    
    for char in expected_clean:
        info = get_char_info(char)
        if info:
            expected_tones.append(info.get('tone', 0))
            char_infos.append(info)
    
    if not expected_tones:
        # Fallback: no tones could be determined
        return 70, {'note': 'Could not determine expected tones from text'}
    
    # Try to detect actual tones from audio using librosa
    try:
        tone_analyzer = get_tone_analyzer()
        
        # Convert expected chars to list for tone analyzer
        chars_list = list(expected_clean)
        tone_result = tone_analyzer.analyze_tones(audio_path, chars_list)
        
        if tone_result.get('success'):
            detected_tone = tone_result.get('detected_tone', 0)
            confidence = tone_result.get('confidence', 0)
            
            # Compare first tone (simplified)
            if expected_tones[0] == detected_tone:
                tone_score = 80 + confidence * 20  # 80-100
            elif detected_tone == 0:
                tone_score = 50  # Neutral/unclear
            else:
                # Wrong tone - calculate penalty
                tone_score = max(30, 70 - abs(expected_tones[0] - detected_tone) * 15)
            
            return round(tone_score, 1), {
                'expected_tone': expected_tones[0],
                'detected_tone': detected_tone,
                'confidence': round(confidence, 2),
                'tone_accuracy': tone_result.get('tone_accuracy', 0)
            }
    except Exception as e:
        logger.warning(f"Tone analysis failed: {e}")
    
    # Fallback: analyze based on expected text difficulty
    # Count difficult tones (3rd tone is hardest, retroflex sounds are hard for Cantonese)
    difficult_count = 0
    for info in char_infos:
        if info.get('tone') == 3:
            difficult_count += 1
        if info.get('is_retroflex'):
            difficult_count += 1
        if info.get('is_nasal'):
            difficult_count += 0.5
    
    # Base score considering difficulty
    difficulty_factor = min(difficult_count / max(len(char_infos), 1), 1)
    base_score = 75 - difficulty_factor * 20  # 55-75 range
    
    return round(base_score, 1), {
        'expected_tones': expected_tones[:5],  # First 5
        'note': 'Estimated - audio analysis unavailable'
    }


def analyze_fluency(audio_duration: float, transcription: str, expected_text: str) -> tuple:
    """
    Analyze fluency based on speaking rate
    Returns: (score, details)
    """
    if not transcription:
        return 5, {'error': 'No transcription'}
    
    if not expected_text:
        return 50, {'error': 'No expected text'}
    
    expected_clean = re.sub(r'[^\u4e00-\u9fff]', '', expected_text)
    actual_clean = re.sub(r'[^\u4e00-\u9fff]', '', transcription)
    
    if not expected_clean or not audio_duration:
        return 50, {'error': 'Missing data'}
    
    # Characters per minute
    cpm = (len(actual_clean) / audio_duration) * 60
    
    # Optimal CPM for Mandarin reading is roughly 180-240
    # Allow some flexibility
    
    if cpm < 60:
        # Too slow
        score = max(30, 60 - (60 - cpm) * 0.5)
    elif cpm < 120:
        # Slow but acceptable
        score = 60 + (cpm - 60) * 0.3
    elif cpm <= 280:
        # Good range
        score = 78 + min(22, (280 - abs(220 - cpm)) * 0.1)
    elif cpm <= 360:
        # Fast but okay
        score = 80 - (cpm - 280) * 0.15
    else:
        # Too fast
        score = max(40, 70 - (cpm - 360) * 0.1)
    
    details = {
        'cpm': round(cpm, 1),
        'characters': len(actual_clean),
        'duration': round(audio_duration, 2),
        'optimal_range': '180-280 CPM'
    }
    
    return round(score, 1), details


def generate_feedback(score: float, level: str, grade: str, 
                      pronunciation_details: dict, tone_details: dict) -> str:
    """Generate feedback based on scores"""
    
    # Get error info
    errors = pronunciation_details.get('errors', [])
    error_count = len(errors)
    
    # Basic message
    if score >= 90:
        msg = "🌟 非常优秀！你的发音很接近母语水平！"
    elif score >= 80:
        msg = "✅ 很好！继续保持！"
    elif score >= 70:
        msg = "👍 不错！继续加油！"
    elif score >= 60:
        msg = "📝 及格了！需要更多练习。"
    else:
        msg = "💪 加油！多听多说会有进步。"
    
    # Add specific feedback
    if error_count > 0:
        # Get first few errors
        first_errors = errors[:3]
        error_chars = [e.get('expected', '') for e in first_errors]
        if error_chars:
            msg += f"\n注意这些字的读音: {' '.join(error_chars)}"
    
    # Tone feedback
    if tone_details.get('expected_tone') and tone_details.get('detected_tone'):
        expected = tone_details.get('expected_tone')
        detected = tone_details.get('detected_tone')
        if expected != detected and detected != 0:
            tone_names = {1: '一声', 2: '二声', 3: '三声', 4: '四声', 0: '轻声'}
            msg += f"\n声调: 应该是{tone_names.get(expected, '')}, 听到的是{tone_names.get(detected, '')}"
    
    return msg


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Tone Analysis Service on port {port}")
    logger.info(f"Engine: Faster Whisper + Tone Analysis (Local)")
    app.run(host='0.0.0.0', port=port, debug=True)
