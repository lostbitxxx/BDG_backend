"""
iFlytek ISE (Pronunciation Evaluation) Service
Clean implementation for Mandarin Chinese pronunciation scoring

PSC Test Aligned:
- Reading Aloud (朗读) - primary focus
- Returns: pronunciation, fluency, tone scores
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import re
import ssl
import time
import asyncio
import struct
import math
import websockets
from datetime import datetime
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class IflytekISEEvaluator:
    """iFlytek Pronunciation Evaluation API"""
    
    def __init__(self):
        self.app_id = os.environ.get('IFLYTEK_APP_ID', '')
        self.api_key = os.environ.get('IFLYTEK_API_KEY', '')
        self.api_secret = os.environ.get('IFLYTEK_API_SECRET', '')
        self.host = 'ise-api-sg.xf-yun.com'
        self.path = '/v2/ise'
        
    def _get_auth_url(self) -> str:
        """Generate authenticated WebSocket URL"""
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
        
        params = {
            'authorization': authorization,
            'date': date,
            'host': self.host
        }
        return f"wss://{self.host}{self.path}?{urlencode(params)}"
    
    def _generate_test_audio(self, duration_secs: float = 3.0) -> bytes:
        """Generate simple sine wave test audio"""
        sample_rate = 16000
        samples = int(sample_rate * duration_secs)
        # Generate sine wave at 300Hz ( Mandarin fundamental frequency range)
        audio = [int(12000 * math.sin(2 * math.pi * 300 * t / sample_rate)) for t in range(samples)]
        return struct.pack('<' + 'h' * samples, *audio)
        """Generate authenticated WebSocket URL"""
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
        
        params = {
            'authorization': authorization,
            'date': date,
            'host': self.host
        }
        return f"wss://{self.host}{self.path}?{urlencode(params)}"
    
    def evaluate(self, audio_path: str, reference_text: str, category: str = 'read_sentence') -> dict:
        """
        Synchronous evaluation - entry point
        """
        # Read audio file
        try:
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
        except Exception as e:
            logger.error(f"Could not read audio file: {e}")
            return {'success': False, 'error': f'Cannot read audio file: {str(e)}'}
        
        # Run async evaluation
        return self._run_evaluation(audio_data, reference_text, category)
    
    def evaluate_raw(self, audio_data: bytes, reference_text: str, category: str = 'read_sentence') -> dict:
        """
        Evaluate raw audio bytes directly
        """
        return self._run_evaluation(audio_data, reference_text, category)
    
    def _run_evaluation(self, audio_data: bytes, reference_text: str, category: str) -> dict:
        """Run async evaluation"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self._evaluate_async(audio_data, reference_text, category)
            )
        finally:
            loop.close()
        
        return result
    
    async def _evaluate_async(self, audio_data: bytes, reference_text: str, category: str) -> dict:
        """
        Async evaluation with WebSocket
        """
        logger.info(f"=== Starting iFlytek evaluation ===")
        logger.info(f"Audio size: {len(audio_data)} bytes")
        logger.info(f"Text: {reference_text}")
        
        if not reference_text:
            return {'success': False, 'error': 'Reference text is required'}
        
        if len(audio_data) < 1000:
            return {'success': False, 'error': 'Audio file too small or empty'}
        
        try:
            ws_url = self._get_auth_url()
            logger.info(f"Connecting to iFlytek ISE API...")
            
            async with websockets.connect(ws_url, ssl=ssl._create_unverified_context()) as ws:
                logger.info("WebSocket connected!")
                
                # Step 1: Send params
                params = {
                    'common': {'app_id': self.app_id},
                    'business': {
                        'sub': 'ise',
                        'ent': 'cn_vip',
                        'category': category,
                        'rstcd': 'utf8',
                        'tte': 'utf-8',
                        'cmd': 'ssb',
                        'text': reference_text
                    },
                    'data': {'status': 0}
                }
                
                logger.info("Sending params...")
                await ws.send(json.dumps(params))
                
                # Step 2: Wait for ack
                try:
                    ack = await asyncio.wait_for(ws.recv(), timeout=10)
                    logger.info(f"Ack: {ack[:200]}")
                    ack_json = json.loads(ack)
                    
                    if ack_json.get('code') != 0:
                        error_msg = ack_json.get('message', 'Unknown error')
                        return {'success': False, 'error': f'iFlytek error: {error_msg}'}
                except asyncio.TimeoutError:
                    return {'success': False, 'error': 'Timeout waiting for iFlytek acknowledgment'}
                
                await asyncio.sleep(0.2)
                
                # Step 3: Send audio in chunks
                logger.info("Sending audio...")
                
                # Send all audio at once
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
                
                # First send with status=1 (intermediate)
                msg1 = {
                    'business': {'cmd': 'auw', 'aus': 1},
                    'data': {
                        'status': 1,
                        'data': audio_b64
                    }
                }
                await ws.send(json.dumps(msg1))
                logger.info(f"Sent audio part 1 ({len(audio_data)} bytes)")
                
                # Then send empty message with status=2 (end)
                await asyncio.sleep(0.5)
                
                msg2 = {
                    'business': {'cmd': 'auw', 'aus': 2},
                    'data': {
                        'status': 2,
                        'data': ''
                    }
                }
                await ws.send(json.dumps(msg2))
                logger.info("Sent audio end")
                
                # Step 4: Wait for result
                logger.info("Waiting for result...")
                
                for attempt in range(30):
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=5)
                        response_json = json.loads(response)
                        
                        status = response_json.get('data', {}).get('status')
                        logger.info(f"Response {attempt+1}: status={status}")
                        
                        if status == 2:
                            # Final result received!
                            xml_b64 = response_json.get('data', {}).get('data')
                            if not xml_b64:
                                return {'success': False, 'error': 'No data in iFlytek response'}
                            
                            # Decode XML
                            xml = None
                            for enc in ['utf-8', 'gb2312', 'gbk', 'gb18030']:
                                try:
                                    xml = base64.b64decode(xml_b64).decode(enc)
                                    break
                                except:
                                    continue
                            
                            if not xml:
                                return {'success': False, 'error': 'Cannot decode iFlytek response'}
                            
                            logger.info(f"XML result received: {len(xml)} chars")
                            
                            # Parse XML for scores
                            result = self._parse_xml_result(xml)
                            return result
                            
                    except asyncio.TimeoutError:
                        logger.warning(f"Timeout on attempt {attempt+1}")
                        continue
                
                return {'success': False, 'error': 'Timeout waiting for iFlytek result'}
                
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}
    
    def _parse_xml_result(self, xml: str) -> dict:
        """Parse iFlytek XML response"""
        logger.info("Parsing XML result...")
        
        # Check if rejected
        is_rejected = re.search(r'is_rejected="([^"]+)"', xml)
        if is_rejected and is_rejected.group(1) == 'true':
            except_info = re.search(r'except_info="([^"]+)"', xml)
            error_code = except_info.group(1) if except_info else "28689"
            
            # Map error codes to user-friendly messages
            error_messages = {
                '28689': 'Audio quality too low. Please speak clearly and try again.',
                '28690': 'No speech detected. Please speak louder.',
                '28691': 'Audio too short. Please speak longer.',
            }
            error_msg = error_messages.get(error_code, f'Audio rejected (code: {error_code}). Please try again.')
            
            return {'success': False, 'error': error_msg}
        
        # Extract scores
        total_match = re.search(r'total_score="([0-9.]+)"', xml)
        pron_match = re.search(r'pronunciation_score="([0-9.]+)"', xml)
        fluency_match = re.search(r'fluency_score="([0-9.]+)"', xml)
        tone_match = re.search(r'tone_score="([0-9.]+)"', xml)
        
        if not total_match:
            return {'success': False, 'error': 'Cannot parse scores from iFlytek response'}
        
        total_score = float(total_match.group(1))
        pron_score = float(pron_match.group(1)) if pron_match else total_score
        fluency_score = float(fluency_match.group(1)) if fluency_match else total_score
        tone_score = float(tone_match.group(1)) if tone_match else total_score
        
        logger.info(f"*** SUCCESS! Scores: total={total_score}, pron={pron_score}, fluency={fluency_score}, tone={tone_score} ***")
        
        return {
            'success': True,
            'scores': {
                'overall': total_score,
                'pronunciation': pron_score,
                'fluency': fluency_score,
                'tone': tone_score,
                'level': self._get_level(total_score),
                'grade': self._get_grade(total_score),
                'pass': total_score >= 60
            },
            'engine': 'iflytek-ise'
        }
    
    def _get_level(self, score: float) -> str:
        """Convert score to PSC level"""
        if score >= 97: return 'Level 1'
        elif score >= 92: return 'Level 1'
        elif score >= 87: return 'Level 2'
        elif score >= 80: return 'Level 2'
        elif score >= 70: return 'Level 3'
        elif score >= 60: return 'Level 3'
        else: return 'Below Level 3'
    
    def _get_grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 90: return 'A+'
        elif score >= 85: return 'A'
        elif score >= 80: return 'A-'
        elif score >= 75: return 'B+'
        elif score >= 70: return 'B'
        elif score >= 65: return 'B-'
        elif score >= 60: return 'C'
        else: return 'D'


def evaluate_with_iflytek_ise(audio_path: str, reference_text: str, category: str = 'read_sentence') -> dict:
    """Entry point for Flask app"""
    evaluator = IflytekISEEvaluator()
    return evaluator.evaluate(audio_path, reference_text, category)


if __name__ == '__main__':
    # Test
    import sys
    if len(sys.argv) > 1:
        result = evaluate_with_iflytek_ise(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '春天')
        print(json.dumps(result, indent=2, ensure_ascii=False))
