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

from services.audio_preprocessor import AudioPreprocessor
from services.iflytek_fixed import IflytekEvaluator
from services.ai_feedback import get_ai_feedback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['TIMEOUT'] = 180

_iflytek_evaluator = None


def get_iflytek():
    global _iflytek_evaluator
    if _iflytek_evaluator is None:
        logger.info("Loading iFlytek Evaluator (fixed)...")
        _iflytek_evaluator = IflytekEvaluator()
    return _iflytek_evaluator


@app.route('/health', methods=['GET'])
def health_check():
    # Debug: check which iFlytek env vars are actually visible
    app_id_present = bool(os.environ.get('IFLYTEK_APP_ID'))
    api_key_present = bool(os.environ.get('IFLYTEK_API_KEY'))
    api_secret_present = bool(os.environ.get('IFLYTEK_API_SECRET'))

    iflytek_ready = bool(app_id_present and api_key_present and api_secret_present)

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
        'psc_aligned': True,
        'iflytek_env': {
            'app_id': app_id_present,
            'api_key': api_key_present,
            'api_secret': api_secret_present,
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

        # Call iFlytek
        logger.info("Calling iFlytek ISE API...")
        iflytek = get_iflytek()
        result = iflytek.evaluate(processed_audio, expected_text)

        if not result.get('success'):
            response = {
                'success': False,
                'error': result.get('error', 'Audio analysis service unavailable. Please try again later.')
            }
            # Include developer info if available
            if result.get('dev_code'):
                response['dev_info'] = f'iFlytek error code: {result["dev_code"]}'
            return jsonify(response), 500

        scores = result.get('scores', {})
        transcription = result.get('transcription', '')
        errors = result.get('errors', [])
        defects = result.get('defects', [])
        processing_time = round(time.time() - start_time, 2)

        # Generate AI feedback
        logger.info("Generating AI feedback...")
        ai_feedback = get_ai_feedback()
        detailed_feedback = ai_feedback.generate_feedback(
            transcription=transcription,
            expected_text=expected_text,
            errors=errors,
            defects=defects,
            scores=scores,
            section=section
        )

        return jsonify({
            'success': True,
            'expected': expected_text,
            'transcription': transcription,
            'scores': scores,
            'errors': errors,
            'defects': defects,
            'basic_feedback': generate_feedback(scores),
            'ai_feedback': detailed_feedback,
            'feedback': format_bilingual_feedback(detailed_feedback),
            'processing_time': processing_time,
            'engine': 'iflytek-ise',
            'test_type': 'PSC Reading Aloud (朗读)'
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


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting on port {port}")
    logger.info("Engine: iFlytek ISE Only (No Fallback)")
    app.run(host='0.0.0.0', port=port, debug=True)
