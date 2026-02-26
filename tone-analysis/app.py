"""
BoDongGua Audio Analysis API
Flask microservice for pronunciation analysis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import time
import tempfile
import requests

from services.audio_preprocessor import AudioPreprocessor
from services.whisper_service import WhisperService
from services.tone_analyzer import ToneAnalyzer
from services.scorer import Scorer
from services.pinyin_db import analyze_text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['TIMEOUT'] = 120  # 2 minutes timeout

# Initialize services (lazy loaded)
whisper_service = None
tone_analyzer = None
scorer = None


def get_whisper():
    global whisper_service
    if whisper_service is None:
        model = os.environ.get('WHISPER_MODEL', 'base')
        whisper_service = WhisperService(model)
    return whisper_service


def get_tone_analyzer():
    global tone_analyzer
    if tone_analyzer is None:
        tone_analyzer = ToneAnalyzer()
    return tone_analyzer


def get_scorer_instance():
    global scorer
    if scorer is None:
        scorer = Scorer()
    return scorer


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'tone-analysis',
        'whisper_model': os.environ.get('WHISPER_MODEL', 'base')
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Main analysis endpoint
    
    Request JSON:
    {
        "audio_url": "https://s3.../audio.webm",
        "expected_text": "春天来了",
        "section": 4  // PSC section (optional)
    }
    
    Response JSON:
    {
        "success": true,
        "transcription": "...",
        "scores": {...},
        "feedback": "..."
    }
    """
    start_time = time.time()
    
    # Validate request
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
    
    audio_url = data.get('audio_url')
    expected_text = data.get('expected_text', '')
    section = data.get('section', 4)
    
    if not audio_url:
        return jsonify({'success': False, 'error': 'audio_url is required'}), 400
    
    logger.info(f"Analyzing audio from: {audio_url}")
    logger.info(f"Expected text: {expected_text}")
    
    # Create preprocessor but don't cleanup until done
    preprocessor = AudioPreprocessor()
    processed_audio = None
    
    try:
        # Step 1: Preprocess audio
        logger.info("Step 1: Preprocessing audio...")
        processed_audio = preprocessor.process(audio_url)
        
        if not processed_audio:
            return jsonify({
                'success': False,
                'error': 'Failed to process audio'
            }), 400
        
        # Get audio duration
        import subprocess
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', processed_audio],
            capture_output=True, text=True, timeout=10
        )
        try:
            duration_str = result.stdout.strip()
            audio_duration = float(duration_str) if duration_str and duration_str != 'N/A' else 5.0
        except (ValueError, AttributeError):
            audio_duration = 5.0
        
        # Step 2: Whisper transcription
        logger.info("Step 2: Transcribing with Whisper...")
        whisper = get_whisper()
        transcription_result = whisper.analyze(processed_audio, expected_text)
        
        if not transcription_result.get('success'):
            return jsonify({
                'success': False,
                'error': 'Transcription failed: ' + transcription_result.get('error', 'Unknown')
            }), 500
        
        # Step 3: Tone analysis
        logger.info("Step 3: Analyzing tones...")
        tone_analysis_result = get_tone_analyzer().analyze_tones(
            processed_audio, 
            list(expected_text)
        )
        
        # Step 4: Calculate scores
        logger.info("Step 4: Calculating scores...")
        scores = get_scorer_instance().score(
            transcription_result,
            tone_analysis_result,
            expected_text,
            audio_duration
        )
        
        # Step 5: Generate feedback
        logger.info("Step 5: Generating feedback...")
        feedback = generate_feedback(scores, transcription_result, expected_text)
        
        # Return results
        processing_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'transcription': transcription_result.get('transcription', ''),
            'expected': expected_text,
            'scores': scores,
            'feedback': feedback,
            'processing_time': round(processing_time, 2),
            'model': 'whisper-' + os.environ.get('WHISPER_MODEL', 'base')
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # Always cleanup
        if preprocessor:
            preprocessor.cleanup()


def generate_feedback(scores: dict, transcription: dict, expected: str) -> str:
    """Generate personalized feedback based on scores"""
    
    feedback_parts = []
    
    # Overall assessment
    overall = scores.get('overall', 0)
    if overall >= 90:
        feedback_parts.append("🌟 Excellent! Your pronunciation is very clear.")
    elif overall >= 80:
        feedback_parts.append("✅ Good job! You passed the test.")
    elif overall >= 70:
        feedback_parts.append("👍 Not bad! Keep practicing to improve.")
    else:
        feedback_parts.append("💪 Keep practicing! You'll improve with time.")
    
    # Specific feedback
    details = scores.get('details', {})
    
    # Tone issues
    tone_errors = details.get('tone_errors', [])
    if tone_errors:
        feedback_parts.append("🎯 Focus on your tones. The tones didn't match the expected pattern.")
    
    # Retroflex issues
    phoneme_errors = details.get('phoneme_errors', {})
    retroflex_errors = phoneme_errors.get('retroflex', [])
    if retroflex_errors:
        feedback_parts.append("👅 Practice the retroflex sounds (zh, ch, sh, r) - these are tricky for many learners.")
    
    # Nasal issues
    nasal_errors = phoneme_errors.get('nasal', [])
    if nasal_errors:
        feedback_parts.append("👃 Pay attention to the nasal finals (an, en, ang, eng).")
    
    # Fluency
    fluency = details.get('fluency', 0)
    if fluency < 60:
        feedback_parts.append("⏱️ Try to speak at a more steady pace - not too fast or slow.")
    
    # Transcription match
    match = details.get('transcription_match', 0)
    if match < 70:
        feedback_parts.append("📖 Try to speak more clearly and match the expected text closer.")
    
    return " ".join(feedback_parts)


@app.route('/models', methods=['GET'])
def list_models():
    """List available Whisper models"""
    models = [
        {"name": "tiny", "speed": "fastest", "accuracy": "good", "ram": "1GB"},
        {"name": "base", "speed": "fast", "accuracy": "very_good", "ram": "1GB"},
        {"name": "small", "speed": "medium", "accuracy": "excellent", "ram": "2GB"},
    ]
    return jsonify({
        'models': models,
        'current': os.environ.get('WHISPER_MODEL', 'base')
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Starting Tone Analysis Service on port {port}")
    logger.info(f"Whisper model: {os.environ.get('WHISPER_MODEL', 'base')}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
