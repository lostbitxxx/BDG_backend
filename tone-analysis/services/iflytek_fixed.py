"""
iFlytek ISE - Based on official demo (simplified)
"""

import websocket
import json
import base64
import hashlib
import hmac
import ssl
import time
import logging
import os
import io
import re
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IflytekEvaluator:
    def __init__(self):
        self.app_id = os.environ.get('IFLYTEK_APP_ID', '')
        self.api_key = os.environ.get('IFLYTEK_API_KEY', '')
        self.api_secret = os.environ.get('IFLYTEK_API_SECRET', '')
        
    def create_url(self):
        """Create auth URL"""
        import datetime
        from wsgiref.handlers import format_date_time
        from urllib.parse import urlencode
        
        host = "ise-api-sg.xf-yun.com"
        path = "/v2/ise"
        
        now = datetime.datetime.now()
        date = format_date_time(time.mktime(now.timetuple()))
        
        signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')
        
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha_base64}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')
        
        v = {"authorization": authorization, "date": date, "host": host}
        return f"wss://{host}{path}?{urlencode(v)}"
    
    def evaluate(self, audio_path: str, text: str) -> dict:
        """Evaluate audio"""
        
        # Read audio
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        logger.info(f"Audio: {len(audio_data)} bytes, Text: {text}")
        
        result = {'success': False, 'error': 'Timeout'}
        result_ready = False
        
        def on_message(ws, message):
            nonlocal result, result_ready
            try:
                data = json.loads(message)
                code = data.get('code', -1)
                logger.info(f"Response: {message[:200]}")
                
                if code != 0:
                    result = {'success': False, 'error': f"iFlytek error {code}: {data.get('message', '')}"}
                    result_ready = True
                else:
                    status = data.get('data', {}).get('status')
                    if status == 2:
                        xml_b64 = data.get('data', {}).get('data')
                        if xml_b64:
                            xml = base64.b64decode(xml_b64).decode('gbk')
                            logger.info(f"XML (full): {xml}")
                            result = self._parse_xml(xml)
                        result_ready = True
                        ws.close()
            except Exception as e:
                logger.error(f"Parse error: {e}")
                result = {'success': False, 'error': str(e)}
                result_ready = True
        
        def on_error(ws, error):
            nonlocal result
            logger.error(f"WebSocket error: {error}")
            result = {'success': False, 'error': str(error)}
            result_ready = True
        
        def on_close(ws, close_status_code, close_msg):
            logger.info(f"WebSocket closed: {close_status_code} {close_msg}")
        
        def on_open(ws):
            def run():
                try:
                    # Same as demo: 1280 bytes per frame
                    frameSize = 1280
                    interval = 0.04
                    status = 0  # First frame
                    
                    text_bom = '\ufeff' + text
                    fp = io.BytesIO(audio_data)
                    
                    # First frame - send params
                    logger.info("Sending first frame with params...")
                    d = {
                        "common": {"app_id": self.app_id},
                        "business": {
                            "category": "read_sentence",
                            "sub": "ise",
                            "ent": "cn_vip",
                            "cmd": "ssb",
                            "auf": "audio/L16;rate=16000",
                            "aue": "raw",
                            "text": text_bom,
                            "ttp_skip": True,
                            "aus": 1
                        },
                        "data": {"status": 0}
                    }
                    ws.send(json.dumps(d))
                    logger.info("First frame sent")
                    
                    # Read all audio data
                    audio_bytes = audio_data
                    total_len = len(audio_bytes)
                    
                    # Send in 1280-byte chunks
                    frameSize = 1280
                    chunk_num = 0
                    num_chunks = (total_len + frameSize - 1) // frameSize
                    
                    for i in range(0, total_len, frameSize):
                        chunk = audio_bytes[i:i+frameSize]
                        is_last = (i + frameSize) >= total_len
                        
                        if is_last:
                            # Last chunk - send with status 2, aus 4
                            d = {
                                "business": {"cmd": "auw", "aus": 4, "aue": "raw"},
                                "data": {"status": 2, "data": str(base64.b64encode(chunk).decode())}
                            }
                            logger.info(f"Sending last chunk {num_chunks}...")
                        else:
                            # Continue chunk - send with status 1, aus 2
                            chunk_num += 1
                            d = {
                                "business": {"cmd": "auw", "aus": 2, "aue": "raw"},
                                "data": {"status": 1, "data": str(base64.b64encode(chunk).decode())}
                            }
                        
                        ws.send(json.dumps(d))
                        
                        if chunk_num % 10 == 0:
                            logger.info(f"Sent {chunk_num} chunks...")
                        
                        time.sleep(0.04)
                    
                    logger.info("All audio sent, closing...")
                    time.sleep(1)
                    ws.close()
                    
                except Exception as e:
                    logger.error(f"Send error: {e}")
                    try:
                        ws.close()
                    except:
                        pass
            
            threading.Thread(target=run).start()
        
        ws_url = self.create_url()
        logger.info(f"Connecting to {ws_url[:60]}...")
        
        ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_error=on_error, on_close=on_close)
        ws.on_open = on_open
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        
        # Wait for result (allow up to 4 min for long recordings / slow iFlytek)
        timeout = 240
        start = time.time()
        while not result_ready and time.time() - start < timeout:
            time.sleep(0.1)

        if not result_ready:
            logger.error("Timeout waiting for result")
            result = {'success': False, 'error': 'Timeout'}
        
        return result
    
    def _parse_xml(self, xml: str) -> dict:
        # Check for rejection with more detail
        is_rejected = re.search(r'is_rejected="([^"]+)"', xml)
        except_info = re.search(r'except_info="([^"]+)"', xml)
        
        if is_rejected and is_rejected.group(1) == 'true':
            error_code = except_info.group(1) if except_info else "unknown"
            
            # User-friendly error messages (reason + solution in one line)
            # Reference: https://www.xfyun.cn/document/error-code
            user_messages = {
                # Audio quality issues (286xx)
                '28675': 'Audio format error. Please try recording again.',
                '28676': 'Audio quality is too low. Please speak more clearly and try again.',
                '28677': 'Too much background noise. Please record in a quieter environment.',
                '28678': 'Audio is too short. Please speak longer (at least 3 seconds).',
                '28679': 'No speech detected. Please speak directly into the microphone.',
                '28680': 'Audio volume is too low. Please speak louder.',
                '28681': 'Audio volume is too loud. Please speak softer.',
                '28682': 'Audio has too many silences. Please speak continuously.',
                '28683': 'Speech speed is too fast. Please speak at a normal pace.',
                '28684': 'Speech speed is too slow. Please speak at a normal pace.',
                '28689': 'Audio quality is too low. Please speak more clearly and try again.',
                
                # Authentication/Service errors (1xxxxx)
                '10001': 'Service authentication failed. Please contact support.',
                '10002': 'Invalid request parameter. Please try again.',
                '10003': 'Missing required parameter. Please try again.',
                '10004': 'Service is temporarily unavailable. Please try again later.',
                
                # Other errors
                '10163': 'Audio format not supported. Please try recording again.',
            }
            
            user_msg = user_messages.get(error_code, 'Audio quality not suitable. Please try again with a clearer recording.')
            
            return {
                'success': False, 
                'error': user_msg,
                'dev_code': error_code  # For developers to check exact error
            }
        
        m = re.search(r'total_score="([0-9.]+)"', xml)
        if not m:
            return {'success': False, 'error': 'Cannot parse score'}
        
        # Extract individual scores from XML
        # iFlytek provides: phone_score (pronunciation), fluency_score, tone_score
        pronunciation_match = re.search(r'phone_score="([0-9.]+)"', xml)
        fluency_match = re.search(r'fluency_score="([0-9.]+)"', xml)
        tone_match = re.search(r'tone_score="([0-9.]+)"', xml)
        
        pronunciation = float(pronunciation_match.group(1)) if pronunciation_match else float(m.group(1))
        fluency = float(fluency_match.group(1)) if fluency_match else float(m.group(1))
        tone = float(tone_match.group(1)) if tone_match else float(m.group(1))
        
        # Calculate weighted overall score based on PSC standards
        # Pronunciation: 40%, Fluency: 30%, Tone: 30%
        overall_score = round((pronunciation * 0.4) + (fluency * 0.3) + (tone * 0.3), 2)
        
        logger.info(f"Individual scores - Pronunciation: {pronunciation}, Fluency: {fluency}, Tone: {tone}")
        logger.info(f"Calculated overall score (weighted): {overall_score}")
        
        # Determine PSC Level and Grade based on official standards
        # Level 1: 97-100 (First Class - 一级甲等)
        # Level 2: 87-96.99 (Second Class Grade A - 二级甲等)
        # Level 3: 80-86.99 (Second Class Grade B - 二级乙等)  
        # Level 4: 70-79.99 (Third Class - 三级甲等)
        # Level 5: 60-69.99 (Third Class Grade B - 三级乙等)
        # Below 60: Below Level 3 (不入级)
        
        if overall_score >= 97:
            level = "Level 1 - 一级甲等 (First Class)"
            grade = "A"
        elif overall_score >= 87:
            level = "Level 2 - 二级甲等 (Second Class, Grade A)"
            grade = "A"
        elif overall_score >= 80:
            level = "Level 2 - 二级乙等 (Second Class, Grade B)"
            grade = "B"
        elif overall_score >= 70:
            level = "Level 3 - 三级甲等 (Third Class, Grade A)"
            grade = "B"
        elif overall_score >= 60:
            level = "Level 3 - 三级乙等 (Third Class, Grade B)"
            grade = "C"
        else:
            level = "Below Level 3 - 不入级 (Not Qualified)"
            grade = "D"
        
        # Extract transcription (recognized speech)
        # iFlytek ISE returns the recognized text in multiple ways
        transcription = ""
        
        # Try to extract from 'recog' attribute (most common)
        recog_match = re.search(r'recg="([^"]+)"', xml)
        if recog_match:
            transcription = recog_match.group(1)
        else:
            # Try 'content' attribute
            content_match = re.search(r'content="([^"]+)"', xml)
            if content_match:
                transcription = content_match.group(1)
            else:
                # Try sentence element
                sentence_match = re.search(r'<sentence[^>]*>([^<]+)</sentence>', xml)
                if sentence_match:
                    transcription = sentence_match.group(1)
        
        logger.info(f"Extracted transcription: {transcription}")
        
        return {
            'success': True,
            'transcription': transcription,
            'scores': {
                'overall': overall_score,
                'pronunciation': round(pronunciation, 2),
                'fluency': round(fluency, 2),
                'tone': round(tone, 2),
                'level': level,
                'grade': grade,
                'pass': overall_score >= 60
            }
        }
