"""
iFlytek ISE REST API Client
Alternative to WebSocket - uses REST API instead
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import requests
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class IflytekRESTEvaluator:
    """iFlytek ISE via REST API"""
    
    def __init__(self):
        self.app_id = os.environ.get('IFLYTEK_APP_ID', '')
        self.api_key = os.environ.get('IFLYTEK_API_KEY', '')
        self.api_secret = os.environ.get('IFLYTEK_API_SECRET', '')
        self.host = 'ise-api-sg.xf-yun.com'
        self.path = '/v2/ise'
        
    def _get_auth_header(self) -> dict:
        """Generate authentication header"""
        now = datetime.utcnow()
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"
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
        
        return {
            'Authorization': authorization,
            'Date': date,
            'Host': self.host
        }
    
    def evaluate(self, audio_path: str, reference_text: str) -> dict:
        """Evaluate using REST API"""
        
        # Read audio file
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
        except Exception as e:
            return {'success': False, 'error': f'Cannot read audio: {str(e)}'}
        
        logger.info(f"=== REST API: Sending {len(audio_data)} bytes ===")
        
        # Build request
        url = f"https://{self.host}{self.path}"
        headers = self._get_auth_header()
        headers['Content-Type'] = 'application/json'
        
        # Encode audio as base64
        audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        
        payload = {
            'common': {'app_id': self.app_id},
            'business': {
                'sub': 'ise',
                'ent': 'cn_vip',
                'category': 'read_sentence',
                'rstcd': 'utf8',
                'text': reference_text
            },
            'data': {
                'status': 2,
                'format': 'wav',
                'rate': 16000,
                'channels': 1,
                'bit_depth': 16,
                'codec': 'pcm',
                'audio': audio_b64
            }
        }
        
        try:
            logger.info("Sending REST API request...")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                code = result.get('code')
                
                if code == 0:
                    # Success - parse XML result
                    xml_data = result.get('data', {}).get('data')
                    if xml_data:
                        xml_decoded = base64.b64decode(xml_data).decode('utf-8')
                        logger.info(f"XML result: {xml_decoded[:300]}")
                        return self._parse_xml(xml_decoded)
                    return {'success': False, 'error': 'No data in response'}
                else:
                    return {'success': False, 'error': f"iFlytek error: {result.get('message')}"}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                
        except Exception as e:
            logger.error(f"REST API error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_xml(self, xml: str) -> dict:
        """Parse XML response"""
        import re
        
        # Check rejection
        is_rejected = re.search(r'is_rejected="([^"]+)"', xml)
        if is_rejected and is_rejected.group(1) == 'true':
            return {'success': False, 'error': 'Audio rejected - speak more clearly'}
        
        # Extract scores
        total_match = re.search(r'total_score="([0-9.]+)"', xml)
        pron_match = re.search(r'pronunciation_score="([0-9.]+)"', xml)
        fluency_match = re.search(r'fluency_score="([0-9.]+)"', xml)
        tone_match = re.search(r'tone_score="([0-9.]+)"', xml)
        
        if not total_match:
            return {'success': False, 'error': 'Cannot parse scores'}
        
        score = float(total_match.group(1))
        
        return {
            'success': True,
            'scores': {
                'overall': score,
                'pronunciation': float(pron_match.group(1)) if pron_match else score,
                'fluency': float(fluency_match.group(1)) if fluency_match else score,
                'tone': float(tone_match.group(1)) if tone_match else score,
                'level': self._get_level(score),
                'grade': self._get_grade(score),
                'pass': score >= 60
            }
        }
    
    def _get_level(self, score: float) -> str:
        if score >= 97: return 'Level 1'
        elif score >= 92: return 'Level 1'
        elif score >= 87: return 'Level 2'
        elif score >= 80: return 'Level 2'
        elif score >= 70: return 'Level 3'
        elif score >= 60: return 'Level 3'
        return 'Below Level 3'
    
    def _get_grade(self, score: float) -> str:
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'B+'
        elif score >= 70: return 'B'
        elif score >= 60: return 'C'
        return 'D'


def evaluate_with_rest(audio_path: str, text: str) -> dict:
    evaluator = IflytekRESTEvaluator()
    return evaluator.evaluate(audio_path, text)
