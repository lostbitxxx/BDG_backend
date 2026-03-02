"""
iFlytek ISE - Fixed to match official demo
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
import struct

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Frame status constants (from demo)
STATUS_FIRST_FRAME = 0
STATUS_CONTINUE_FRAME = 1
STATUS_LAST_FRAME = 2


class IflytekISE:
    def __init__(self):
        self.app_id = os.environ.get('IFLYTEK_APP_ID', '')
        self.api_key = os.environ.get('IFLYTEK_API_KEY', '')
        self.api_secret = os.environ.get('IFLYTEK_API_SECRET', '')
        
    def _create_url(self):
        """Generate auth URL - matching demo exactly"""
        import datetime
        from wsgiref.handlers import format_date_time
        from urllib.parse import urlencode
        
        # Use the same host as demo
        host = "ise-api.xf-yun.cn"
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
        
        v = {
            "authorization": authorization,
            "date": date,
            "host": host
        }
        
        url = f"wss://{host}{path}?{urlencode(v)}"
        return url
    
    def evaluate(self, audio_path: str, text: str) -> dict:
        """Evaluate audio - matching demo logic"""
        
        # Read audio
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
        except Exception as e:
            return {'success': False, 'error': f'Cannot read audio: {e}'}
        
        logger.info(f"Audio size: {len(audio_data)} bytes")
        
        # Connect
        ws_url = self._create_url()
        logger.info(f"Connecting to {ws_url[:50]}...")
        
        # Use old websocket library like demo
        ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close
        )
        
        # Store for callbacks
        ws.audio_data = audio_data
        ws.text = text
        ws.result = None
        ws.error = None
        
        ws.on_open = self._on_open
        
        # Run (will close automatically)
        ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        
        if ws.error:
            return {'success': False, 'error': ws.error}
        
        if ws.result:
            return ws.result
            
        return {'success': False, 'error': 'No result received'}
    
    def _on_open(self, ws):
        """Handle connection open - matching demo exactly"""
        def run(*args):
            # Same as demo: 1280 bytes per frame
            frameSize = 1280
            intervel = 0.04  # 40ms like demo
            status = STATUS_FIRST_FRAME
            
            with open(ws.audio_path, "rb") as fp:  # Note: need to set this
                pass
            
            # Use stored audio data
            data = ws.audio_data
            text = ws.text
            text_with_bom = '\ufeff' + text
            
            fp_data = io.BytesIO(data)
            
            while True:
                buf = fp_data.read(frameSize)
                
                if not buf:
                    status = STATUS_LAST_FRAME
                
                # First frame - send params
                if status == STATUS_FIRST_FRAME:
                    d = {
                        "common": {"app_id": self.app_id},
                        "business": {
                            "category": "read_sentence",
                            "sub": "ise",
                            "ent": "cn_vip",  # Chinese
                            "cmd": "ssb",
                            "auf": "audio/L16;rate=16000",
                            "aue": "raw",
                            "text": text_with_bom,
                            "ttp_skip": True,
                            "aus": 1
                        },
                        "data": {"status": 0}
                    }
                    ws.send(json.dumps(d))
                    status = STATUS_CONTINUE_FRAME
                    
                # Continue frame
                elif status == STATUS_CONTINUE_FRAME:
                    d = {
                        "business": {"cmd": "auw", "aus": 2, "aue": "raw"},
                        "data": {"status": 1, "data": str(base64.b64encode(buf).decode())}
                    }
                    ws.send(json.dumps(d))
                    
                # Last frame
                elif status == STATUS_LAST_FRAME:
                    d = {
                        "business": {"cmd": "auw", "aus": 4, "aue": "raw"},
                        "data": {"status": 2, "data": str(base64.b64encode(buf).decode())}
                    }
                    ws.send(json.dumps(d))
                    time.sleep(1)
                    break
                
                time.sleep(intervel)
            
            ws.close()
        
        # Set audio path for callback
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(ws.audio_data)
            ws.audio_path = f.name
        
        import _thread as thread
        thread.start_new_thread(run, ())
    
    def _on_message(self, ws, message):
        """Handle received message"""
        try:
            data = json.loads(message)
            code = data.get("code", -1)
            sid = data.get("sid", "")
            
            if code != 0:
                errMsg = data.get("message", "Unknown error")
                ws.error = f"iFlytek error {code}: {errMsg}"
                logger.error(f"Error: {ws.error}")
            else:
                result_data = data.get("data", {})
                status = result_data.get("status")
                
                if status == 2:
                    xml_b64 = result_data.get("data")
                    if xml_b64:
                        xml = base64.b64decode(xml_b64).decode("gbk")
                        logger.info(f"XML result: {xml[:200]}")
                        ws.result = self._parse_xml(xml)
                        
        except Exception as e:
            logger.error(f"Parse error: {e}")
            ws.error = str(e)
    
    def _on_error(self, ws, error):
        logger.error(f"WebSocket error: {error}")
        ws.error = str(error)
    
    def _on_close(self, ws, close_status_code, close_msg):
        logger.info("WebSocket closed")
    
    def _parse_xml(self, xml: str) -> dict:
        """Parse XML response"""
        import re
        
        is_rejected = re.search(r'is_rejected="([^"]+)"', xml)
        if is_rejected and is_rejected.group(1) == 'true':
            return {'success': False, 'error': 'Audio rejected - speak more clearly'}
        
        total_match = re.search(r'total_score="([0-9.]+)"', xml)
        if not total_match:
            return {'success': False, 'error': 'Cannot parse scores'}
        
        score = float(total_match.group(1))
        
        return {
            'success': True,
            'scores': {
                'overall': score,
                'pronunciation': score,
                'fluency': score,
                'tone': score,
                'level': 'Level 1' if score >= 97 else 'Level 2' if score >= 87 else 'Level 3' if score >= 70 else 'Below Level 3',
                'grade': 'A' if score >= 90 else 'B' if score >= 80 else 'C',
                'pass': score >= 60
            }
        }


def evaluate_audio(audio_path: str, text: str) -> dict:
    evaluator = IflytekISE()
    return evaluator.evaluate(audio_path, text)
