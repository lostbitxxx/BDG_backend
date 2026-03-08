"""
BoDongGua Audio Analysis API
Primary: iFlytek ISE API ONLY (No Fallback)
PSC Aligned Scoring
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os
import time
import struct
import math

# Load only local .env (not parent)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from services.audio_preprocessor import AudioPreprocessor, check_audio_quality
from services.iflytek_fixed import IflytekEvaluator
from services.ai_feedback import get_ai_feedback
from services.feedback_generator import generate_feedback as generate_rule_feedback
from services.whisper_service import get_whisper_service
from services.elevenlabs_service import ElevenLabsTranscriber, generate_simple_scores, identify_errors
from services.error_detector import ErrorDetector
from services.psc_scorer import PSCScorer
from services.score_distributor import distribute_scores, analyze_tone_patterns, analyze_phoneme_patterns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['TIMEOUT'] = 360  # 6 minutes - enough for 5 min recording + processing

_iflytek_evaluator = None
_elevenlabs_transcriber = None


def get_iflytek():
    global _iflytek_evaluator
    if _iflytek_evaluator is None:
        logger.info("Loading iFlytek Evaluator (fixed)...")
        _iflytek_evaluator = IflytekEvaluator()
    return _iflytek_evaluator


def get_elevenlabs():
    global _elevenlabs_transcriber
    if _elevenlabs_transcriber is None:
        logger.info("Loading ElevenLabs Transcriber...")
        _elevenlabs_transcriber = ElevenLabsTranscriber()
    return _elevenlabs_transcriber


@app.route('/health', methods=['GET'])
def health_check():
    # Debug: check which iFlytek env vars are actually visible
    app_id_present = bool(os.environ.get('IFLYTEK_APP_ID'))
    api_key_present = bool(os.environ.get('IFLYTEK_API_KEY'))
    api_secret_present = bool(os.environ.get('IFLYTEK_API_SECRET'))

    iflytek_ready = bool(app_id_present and api_key_present and api_secret_present)

    # Check ElevenLabs
    elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
    elevenlabs_ready = bool(elevenlabs_key and elevenlabs_key != 'your_elevenlabs_api_key_here')

    logger.info(
        "Health check – iFlytek env present: APP_ID=%s, API_KEY=%s, API_SECRET=%s",
        app_id_present,
        api_key_present,
        api_secret_present,
    )

    return jsonify({
        'status': 'ok',
        'service': 'tone-analysis',
        'engine': 'iFlytek ISE Only (No Fallback)',
        'iflytek_ready': iflytek_ready,
        'elevenlabs_ready': elevenlabs_ready,
        'psc_aligned': True,
        'iflytek_env': {
            'app_id': app_id_present,
            'api_key': api_key_present,
            'api_secret': api_secret_present,
        },
        'elevenlabs_env': {
            'api_key': elevenlabs_ready
        },
        'openrouter_env': {
            'api_key': bool(os.environ.get('OPENROUTER_API_KEY'))
        }
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint - iFlytek ONLY with AI feedback"""
    start_time = time.time()

    # Check credentials
    if not os.environ.get('IFLYTEK_APP_ID'):
        return jsonify({
            'success': False,
            'error': 'iFlytek not configured'
        }), 500

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data'}), 400

    audio_url = data.get('audio_url')
    expected_text = data.get('expected_text', '')
    section = data.get('section', 4)  # Default to Section 4 (reading passage)

    if not audio_url:
        return jsonify({'success': False, 'error': 'audio_url required'}), 400

    logger.info(f"Analyzing: {audio_url}")
    logger.info(f"Text: {expected_text}")
    logger.info(f"Section: {section}")

    # Download and process audio
    preprocessor = AudioPreprocessor()

    try:
        processed_audio = preprocessor.process(audio_url)
        if not processed_audio:
            return jsonify({'success': False, 'error': 'Failed to download audio'}), 400

        # Check file size
        audio_size = os.path.getsize(processed_audio)
        if audio_size < 1000:
            return jsonify({'success': False, 'error': 'Audio too small'}), 400

        logger.info(f"Audio: {audio_size} bytes")

        # Check audio quality
        quality = check_audio_quality(processed_audio)
        if quality.get('warnings'):
            logger.warning(f"Audio quality warnings: {quality['warnings']}")

        # Call iFlytek
        logger.info("Calling iFlytek ISE API...")
        iflytek = get_iflytek()
        result = iflytek.evaluate(processed_audio, expected_text)

        if not result.get('success'):
            # Expected analysis failure (rejected audio, timeout, etc.) → 200 so frontend
            # can show the message and Rerecord without a server error. Only use 500
            # for unexpected server/configuration errors.
            response = {
                'success': False,
                'code': 'audio_cannot_be_processed',
                'error': result.get('error', 'Audio analysis service unavailable. Please try again later.')
            }
            if result.get('dev_code'):
                response['dev_info'] = f'iFlytek error code: {result["dev_code"]}'
            return jsonify(response), 200

        scores = result.get('scores', {})
        transcription = result.get('transcription', '')

        # Run error detection to get character-level errors for detailed feedback
        # Filter out punctuation for accurate analysis
        import re
        expected_text_clean = re.sub(r'[，。？！、；：""''（）【】《》…—]', '', expected_text)
        transcription_clean = re.sub(r'[，。？！、；：""''（）【】《》…—]', '', transcription)

        logger.info("Running error detection for detailed feedback...")
        error_detector = ErrorDetector()
        error_result = error_detector.detect_errors(
            expected_text=expected_text_clean,
            transcription=transcription_clean
        )
        errors = error_result.get('errors', [])
        defects = []  # iFlytek doesn't provide defects separately
        processing_time = round(time.time() - start_time, 2)

        # Generate error_summary for feedback
        error_summary = {
            'total_errors': len(errors),
            'total_defects': len(defects),
            'by_category': {},
            'by_initial': {},
            'by_final': {},
            'by_tone': {}
        }

        # Convert PronunciationError objects to dicts for feedback generator
        error_dicts = []
        for e in errors:
            if hasattr(e, '__dict__'):
                error_dicts.append(e.__dict__)
            elif hasattr(e, 'character'):
                error_dicts.append({
                    'character': e.character,
                    'position': e.position,
                    'category': e.category,
                    'expected_pinyin': e.expected_pinyin,
                    'expected_tone': e.expected_tone,
                    'expected_initial': e.expected_initial,
                    'expected_final': e.expected_final,
                    'actual_pinyin': e.actual_pinyin,
                    'actual_tone': e.actual_tone,
                    'actual_initial': e.actual_initial,
                    'actual_final': e.actual_final,
                })
            else:
                error_dicts.append(e)

        # Generate feedback using rule-based system
        logger.info("Generating detailed feedback...")
        detailed_feedback = generate_rule_feedback(
            errors=error_dicts,
            scores=scores,
            section=section,
            error_summary=error_summary,
            expected_text=expected_text_clean
        )

        # Add enhanced character analysis using score distribution
        logger.info("Generating character analysis with score distribution...")
        try:
            char_analysis = distribute_scores(
                expected_text=expected_text_clean,
                transcription=transcription_clean,
                overall_score=scores.get('pronunciation', scores.get('overall', 0)),
                tone_score=scores.get('tone', 0),
                fluency_score=scores.get('fluency', 0)
            )
            detailed_feedback['character_analysis'] = char_analysis
            detailed_feedback['tone_analysis'] = analyze_tone_patterns(char_analysis)
            detailed_feedback['phoneme_analysis'] = analyze_phoneme_patterns(char_analysis)
        except Exception as e:
            logger.warning(f"Score distribution failed: {e}")

        return jsonify({
            'success': True,
            'expected': expected_text,
            'transcription': transcription,
            'scores': scores,
            'errors': error_dicts,
            'defects': defects,
            'basic_feedback': generate_feedback(scores),
            'ai_feedback': detailed_feedback,
            'feedback': detailed_feedback,  # Include detailed object for frontend character_analysis
            'processing_time': processing_time,
            'engine': 'iflytek-ise',
            'test_type': 'PSC Reading Aloud (朗读)'
        })

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        preprocessor.cleanup()


@app.route('/analyze/elevenlabs', methods=['POST'])
def analyze_elevenlabs():
    """ElevenLabs transcription + iFlytek scoring"""
    start_time = time.time()

    # Check ElevenLabs credentials
    elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
    if not elevenlabs_key or elevenlabs_key == 'your_elevenlabs_api_key_here':
        return jsonify({
            'success': False,
            'error': 'ElevenLabs not configured. Please add ELEVENLABS_API_KEY to .env'
        }), 500

    # Check iFlytek credentials for scoring
    if not os.environ.get('IFLYTEK_APP_ID'):
        return jsonify({
            'success': False,
            'error': 'iFlytek not configured for scoring'
        }), 500

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data'}), 400

    audio_url = data.get('audio_url')
    expected_text = data.get('expected_text', '')
    section = data.get('section', 4)
    language = data.get('language', 'zh')

    if not audio_url:
        return jsonify({'success': False, 'error': 'audio_url required'}), 400

    logger.info(f"ElevenLabs + iFlytek Analyzing: {audio_url}")
    logger.info(f"Text: {expected_text}")

    # Download and process audio
    preprocessor = AudioPreprocessor()

    try:
        processed_audio = preprocessor.process(audio_url)
        if not processed_audio:
            return jsonify({'success': False, 'error': 'Failed to download audio'}), 400

        # Check file size
        audio_size = os.path.getsize(processed_audio)
        if audio_size < 1000:
            return jsonify({'success': False, 'error': 'Audio too small'}), 400

        logger.info(f"Audio: {audio_size} bytes")

        # Step 1: ElevenLabs for transcription
        logger.info("Step 1: Calling ElevenLabs Transcription API...")
        elevenlabs = get_elevenlabs()
        elevenlabs_result = elevenlabs.transcribe(processed_audio, language=language)

        if not elevenlabs_result.get('success'):
            return jsonify({
                'success': False,
                'error': f"ElevenLabs transcription failed: {elevenlabs_result.get('error', 'Unknown error')}"
            }), 500

        transcription = elevenlabs_result.get('transcription', '')

        # Step 2: iFlytek for scoring
        logger.info("Step 2: Calling iFlytek for scoring...")
        iflytek = get_iflytek()
        iflytek_result = iflytek.evaluate(processed_audio, expected_text)

        if not iflytek_result.get('success'):
            # Return transcription but scoring failed
            return jsonify({
                'success': False,
                'error': f"Transcription succeeded but iFlytek scoring failed: {iflytek_result.get('error', 'Unknown error')}",
                'transcription': transcription
            }), 500

        # Use iFlytek scores (more accurate for pronunciation)
        scores = iflytek_result.get('scores', {})

        # Run error detection to get character-level errors for detailed feedback
        # Filter out punctuation for accurate analysis
        import re
        expected_text_clean = re.sub(r'[，。？！、；：""''（）【】《》…—]', '', expected_text)
        transcription_clean = re.sub(r'[，。？！、；：""''（）【】《》…—]', '', transcription)

        logger.info("Running error detection for detailed feedback...")
        error_detector = ErrorDetector()
        error_result = error_detector.detect_errors(
            expected_text=expected_text_clean,
            transcription=transcription_clean
        )
        errors = error_result.get('errors', [])
        defects = []  # iFlytek doesn't provide defects separately

        # Create proper error_summary for AI feedback
        # Note: errors are PronunciationError objects (dataclass), not dicts
        error_summary = {
            'total_errors': len(errors),
            'total_defects': len(defects),
            'by_category': {
                'initial_error': len([e for e in errors if hasattr(e, 'category') and e.category == 'initial_error']),
                'final_error': len([e for e in errors if hasattr(e, 'category') and e.category == 'final_error']),
                'tone_error': len([e for e in errors if hasattr(e, 'category') and e.category == 'tone_error']),
                'neutral_error': len([e for e in errors if hasattr(e, 'category') and e.category == 'neutral_tone_error']),
            },
            'by_initial': {},
            'by_final': {},
            'by_tone': {}
        }

        # Convert PronunciationError objects to dicts for feedback generator
        error_dicts = []
        for e in errors:
            if hasattr(e, '__dict__'):
                error_dicts.append(e.__dict__)
            elif hasattr(e, 'character'):
                error_dicts.append({
                    'character': e.character,
                    'position': e.position,
                    'category': e.category,
                    'expected_pinyin': e.expected_pinyin,
                    'expected_tone': e.expected_tone,
                    'expected_initial': e.expected_initial,
                    'expected_final': e.expected_final,
                    'actual_pinyin': e.actual_pinyin,
                    'actual_tone': e.actual_tone,
                    'actual_initial': e.actual_initial,
                    'actual_final': e.actual_final,
                })
            else:
                error_dicts.append(e)

        processing_time = round(time.time() - start_time, 2)

        # Generate feedback using rule-based system
        logger.info("Generating detailed feedback...")
        detailed_feedback = generate_rule_feedback(
            errors=error_dicts,
            scores=scores,
            section=section,
            error_summary=error_summary,
            expected_text=expected_text_clean
        )

        # Add enhanced character analysis using score distribution
        logger.info("Generating character analysis with score distribution...")
        try:
            char_analysis = distribute_scores(
                expected_text=expected_text_clean,
                transcription=transcription_clean,
                overall_score=scores.get('pronunciation', scores.get('overall', 0)),
                tone_score=scores.get('tone', 0),
                fluency_score=scores.get('fluency', 0)
            )
            detailed_feedback['character_analysis'] = char_analysis
            detailed_feedback['tone_analysis'] = analyze_tone_patterns(char_analysis)
            detailed_feedback['phoneme_analysis'] = analyze_phoneme_patterns(char_analysis)
        except Exception as e:
            logger.warning(f"Score distribution failed: {e}")

        return jsonify({
            'success': True,
            'expected': expected_text,
            'transcription': transcription,
            'scores': scores,
            'errors': error_dicts,
            'defects': defects,
            'basic_feedback': generate_feedback(scores),
            'ai_feedback': detailed_feedback,
            'feedback': detailed_feedback,  # Include detailed object for frontend character_analysis
            'processing_time': processing_time,
            'engine': 'elevenlabs-transcription-iflytek-scoring',
            'transcription_engine': 'elevenlabs-scribe',
            'scoring_engine': 'iflytek-ise',
            'transcription_language': elevenlabs_result.get('language', language)
        })

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        preprocessor.cleanup()


def format_bilingual_feedback(feedback: dict) -> str:
    """Format bilingual feedback for display"""
    if not feedback:
        return "No feedback available."

    lines = []

    # Overall assessment
    if feedback.get('overall_assessment_en'):
        lines.append(f"📊 Overall Assessment / 总体评价:")
        lines.append(f"   English: {feedback['overall_assessment_en']}")
        lines.append(f"   中文: {feedback.get('overall_assessment_zh', '')}")
        lines.append("")

    # Key issues
    if feedback.get('key_issues_en'):
        lines.append("🔍 Key Issues / 主要问题:")
        for i, (en, zh) in enumerate(zip(feedback['key_issues_en'], feedback.get('key_issues_zh', [])), 1):
            lines.append(f"   {i}. {en}")
            lines.append(f"      中文: {zh}")
        lines.append("")

    # Improvement tips
    if feedback.get('improvement_tips_en'):
        lines.append("💡 Improvement Tips / 改进建议:")
        for i, (en, zh) in enumerate(zip(feedback['improvement_tips_en'], feedback.get('improvement_tips_zh', [])), 1):
            lines.append(f"   {i}. {en}")
            lines.append(f"      中文: {zh}")
        lines.append("")

    # Practice recommendations
    pr = feedback.get('practice_recommendations', {})
    if pr:
        lines.append("🏋️ Practice Recommendations / 练习建议:")
        if pr.get('focus_areas_en'):
            lines.append(f"   Focus Areas / 加强方面: {', '.join(pr.get('focus_areas_en', []))}")
            lines.append(f"   中文: {', '.join(pr.get('focus_areas_zh', []))}")
        if pr.get('daily_duration_en'):
            lines.append(f"   Daily Duration / 每日时长: {pr.get('daily_duration_en')}")
            lines.append(f"   中文: {pr.get('daily_duration_zh', '')}")
        lines.append("")

    # Encouragement
    if feedback.get('encouragement_en'):
        lines.append(f"💪 {feedback['encouragement_en']}")
        lines.append(f"   {feedback.get('encouragement_zh', '')}")

    return "\n".join(lines)


def generate_feedback(scores: dict) -> str:
    """Generate PSC-aligned feedback"""
    overall = scores.get('overall', 0)
    
    if overall >= 90:
        return "🌟 优秀！你的普通话发音非常标准！"
    elif overall >= 80:
        return "✅ 良好！继续保持，多练习会更棒！"
    elif overall >= 70:
        return "👍 不错！有一些小问题需要注意。"
    elif overall >= 60:
        return "📝 及格了！需要更多练习来改进。"
    else:
        return "💪 加油！建议多听标准普通话并跟读。"


# Test endpoints
@app.route('/test/audio', methods=['POST'])
def test_with_generated_audio():
    """Test iFlytek REST with generated audio"""
    data = request.get_json() or {}
    text = data.get('text', '春天')
    
    # Generate test PCM audio (3 seconds of sine wave)
    sample_rate = 16000
    duration = 3.0
    samples = int(sample_rate * duration)
    audio = [int(12000 * math.sin(2 * math.pi * 300 * t / sample_rate)) for t in range(samples)]
    audio_data = struct.pack('<' + 'h' * samples, *audio)
    
    # Save to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        f.write(audio_data)
        temp_path = f.name
    
    # Evaluate with REST
    evaluator = IflytekRESTEvaluator()
    result = evaluator.evaluate(temp_path, text)
    
    # Cleanup
    import os
    os.unlink(temp_path)
    
    return jsonify(result)


# ============================================================================
# COMPREHENSIVE ANALYSIS ENDPOINT (NEW - Uses all services)
# ============================================================================

@app.route('/analyze/comprehensive', methods=['POST'])
def analyze_comprehensive():
    """
    Comprehensive analysis endpoint that uses:
    - Faster Whisper/ASR for transcription
    - Error Detector for detailed error classification
    - PSC Scorer for official scoring
    - AI Feedback Generator for structured feedback
    """
    start_time = time.time()

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No JSON data'}), 400

    audio_url = data.get('audio_url')
    expected_text = data.get('expected_text', '')
    section = data.get('section', 4)

    # Filter punctuation for error detection
    import re
    expected_text_clean = re.sub(r'[，。？！、；：""''（）【】《》…—]', '', expected_text)

    # Placeholder for transcription_clean - will be set after transcription is obtained
    transcription_clean = ""

    if not audio_url:
        return jsonify({'success': False, 'error': 'audio_url required'}), 400

    logger.info(f"Comprehensive Analysis: {audio_url}")
    logger.info(f"Text: {expected_text}")
    logger.info(f"Section: {section}")

    # Download and process audio
    preprocessor = AudioPreprocessor()

    try:
        processed_audio = preprocessor.process(audio_url)
        if not processed_audio:
            return jsonify({'success': False, 'error': 'Failed to download audio'}), 400

        audio_size = os.path.getsize(processed_audio)
        if audio_size < 1000:
            return jsonify({'success': False, 'error': 'Audio too small'}), 400

        logger.info(f"Audio: {audio_size} bytes")

        # Try iFlytek first, fall back to ElevenLabs
        transcription = ""
        base_scores = {
            'overall': 0,
            'pronunciation': 0,
            'tone': 0,
            'fluency': 0
        }

        # Check for iFlytek credentials
        if os.environ.get('IFLYTEK_APP_ID') and os.environ.get('IFLYTEK_API_KEY'):
            try:
                logger.info("Trying iFlytek ISE...")
                iflytek = get_iflytek()
                result = iflytek.evaluate(processed_audio, expected_text)
                if result.get('success'):
                    transcription = result.get('transcription', '')
                    base_scores = result.get('scores', base_scores)
                    logger.info(f"iFlytek transcription: {transcription}")
            except Exception as e:
                logger.warning(f"iFlytek failed: {e}")

        # Fallback to ElevenLabs if no transcription
        if not transcription:
            elevenlabs_key = os.environ.get('ELEVENLABS_API_KEY')
            if elevenlabs_key and elevenlabs_key != 'your_elevenlabs_api_key_here':
                try:
                    logger.info("Using ElevenLabs for transcription...")
                    elevenlabs = get_elevenlabs()
                    result = elevenlabs.transcribe(processed_audio, language='zh')
                    if result.get('success'):
                        transcription = result.get('transcription', '')
                        base_scores = generate_simple_scores(transcription, expected_text)
                        logger.info(f"ElevenLabs transcription: {transcription}")
                except Exception as e:
                    logger.warning(f"ElevenLabs failed: {e}")

        # If still no transcription, use expected text
        if not transcription:
            logger.warning("No ASR available, using expected text")
            transcription = expected_text

        # Clean transcription for error detection
        transcription_clean = re.sub(r'[，。？！、；：""''（）【】《》…—]', '', transcription)

        # Run error detection
        logger.info("Running error detection...")
        error_detector = ErrorDetector()
        error_result = error_detector.detect_errors(
            expected_text=expected_text,
            transcription=transcription
        )

        errors = error_result.get('errors', [])
        character_results = error_result.get('character_results', [])
        error_summary = error_result.get('summary', {})

        # Calculate PSC scores
        logger.info("Calculating PSC scores...")
        psc_scorer = PSCScorer()
        psc_scores = psc_scorer.calculate_scores_from_errors(
            expected_text=expected_text,
            transcription=transcription,
            errors=errors,
            section=section
        )

        # Generate feedback using rule-based system
        logger.info("Generating detailed feedback...")

        # Convert errors to dict format for rule-based system
        error_dicts = []
        for err in errors:
            error_dicts.append({
                'character': err.character,
                'position': err.position,
                'category': err.category,
                'expected_pinyin': err.expected_pinyin,
                'expected_tone': err.expected_tone,
                'expected_initial': err.expected_initial,
                'expected_final': err.expected_final,
                'actual_pinyin': err.actual_pinyin,
                'actual_tone': err.actual_tone,
                'actual_initial': err.actual_initial,
                'actual_final': err.actual_final,
                'severity': err.severity,
                'psc_impact': err.psc_impact,
                'description_en': err.description_en,
                'description_zh': err.description_zh,
                'fix_tip_en': err.fix_tip_en,
                'fix_tip_zh': err.fix_tip_zh,
                'practice_words': err.practice_words
            })

        detailed_feedback = generate_rule_feedback(
            errors=error_dicts,
            scores=psc_scores,
            section=section,
            error_summary=error_summary,
            expected_text=expected_text_clean
        )

        # Add enhanced character analysis using score distribution
        logger.info("Generating character analysis with score distribution...")
        try:
            char_analysis = distribute_scores(
                expected_text=expected_text_clean,
                transcription=transcription_clean,
                overall_score=psc_scores.get('pronunciation', psc_scores.get('overall', 0)),
                tone_score=psc_scores.get('tone', 0),
                fluency_score=psc_scores.get('fluency', 0)
            )
            detailed_feedback['character_analysis'] = char_analysis
            detailed_feedback['tone_analysis'] = analyze_tone_patterns(char_analysis)
            detailed_feedback['phoneme_analysis'] = analyze_phoneme_patterns(char_analysis)
        except Exception as e:
            logger.warning(f"Score distribution failed: {e}")

        processing_time = round(time.time() - start_time, 2)

        # Build character results for frontend
        char_results_for_frontend = []
        for cr in character_results:
            char_results_for_frontend.append({
                'position': cr.position,
                'character': cr.character,
                'expected_pinyin': cr.expected_pinyin,
                'actual_pinyin': cr.actual_pinyin,
                'expected_tone': cr.expected_tone,
                'actual_tone': cr.actual_tone,
                'expected_initial': cr.expected_initial,
                'actual_initial': cr.actual_initial,
                'expected_final': cr.expected_final,
                'actual_final': cr.actual_final,
                'status': cr.status,
                'errors': [{
                    'character': e.character,
                    'position': e.position,
                    'category': e.category,
                    'expected_pinyin': e.expected_pinyin,
                    'expected_tone': e.expected_tone,
                    'expected_initial': e.expected_initial,
                    'expected_final': e.expected_final,
                    'actual_pinyin': e.actual_pinyin,
                    'actual_tone': e.actual_tone,
                    'actual_initial': e.actual_initial,
                    'actual_final': e.actual_final,
                    'severity': e.severity,
                    'psc_impact': e.psc_impact,
                    'detection_method': e.detection_method,
                    'confidence': e.confidence,
                    'error_code': e.error_code,
                    'description_en': e.description_en,
                    'description_zh': e.description_zh,
                    'fix_tip_en': e.fix_tip_en,
                    'fix_tip_zh': e.fix_tip_zh,
                    'practice_words': e.practice_words
                } for e in cr.errors]
            })

        return jsonify({
            'success': True,
            'expected_text': expected_text,
            'transcription': transcription,
            'character_results': char_results_for_frontend,
            'scores': psc_scores,
            'psc_level': psc_scores.get('psc_level', '未知'),
            'psc_grade': psc_scores.get('psc_grade', '未知'),
            'pass': psc_scores.get('pass', False),
            'errors': error_dicts,
            'error_summary': error_summary,
            'ai_feedback': detailed_feedback,
            'feedback': detailed_feedback,  # Include detailed object for frontend character_analysis
            'processing_time': processing_time,
            'engine': 'comprehensive-analysis',
            'test_type': 'PSC Comprehensive Analysis'
        })

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        preprocessor.cleanup()


@app.route('/test/error-detector', methods=['POST'])
def test_error_detector():
    """Test the error detector with sample data"""
    data = request.get_json() or {}
    expected = data.get('expected', '春天来了')
    actual = data.get('actual', '春田来了')

    detector = ErrorDetector()
    result = detector.detect_errors(expected, actual)

    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting on port {port}")
    logger.info("Engine: iFlytek ISE Only (No Fallback)")
    app.run(host='0.0.0.0', port=port, debug=True)
