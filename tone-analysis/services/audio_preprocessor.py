"""
Audio Preprocessing Service
Handles audio format conversion, normalization, and validation
"""

import os
import tempfile
import requests
import subprocess
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class AudioPreprocessor:
    """Audio preprocessing pipeline for Whisper and analysis"""
    
    # Target audio format for Whisper
    TARGET_SAMPLE_RATE = 16000
    TARGET_CHANNELS = 1
    TARGET_FORMAT = "wav"
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def validate_audio(self, audio_path: str) -> Tuple[bool, str]:
        """
        Validate audio file
        Returns: (is_valid, error_message)
        """
        if not os.path.exists(audio_path):
            return False, "Audio file not found"
        
        # Check file size (max 50MB)
        file_size = os.path.getsize(audio_path)
        if file_size > 50 * 1024 * 1024:
            return False, "Audio file too large (max 50MB)"
        
        # Check file extension
        allowed_extensions = ['.wav', '.mp3', '.webm', '.m4a', '.flac', '.ogg']
        ext = os.path.splitext(audio_path)[1].lower()
        if ext not in allowed_extensions:
            return False, f"Unsupported audio format: {ext}"
        
        return True, ""
    
    def get_duration(self, audio_path: str) -> Optional[float]:
        """Get audio duration in seconds using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error getting duration: {e}")
        return None
    
    def download_from_url(self, url: str) -> Optional[str]:
        """Download audio from S3 URL to local file"""
        import boto3
        from botocore.config import Config
        
        try:
            # Check if it's an S3 URL
            if 's3.' in url or '.s3.' in url:
                # Parse S3 URL: https://bucket.s3.region.amazonaws.com/key
                # or: https://bucket.s3.region.amazonaws.com/key?params
                from urllib.parse import urlparse
                
                parsed = urlparse(url)
                host = parsed.netloc
                
                # Extract bucket and region from host
                # Format: bucket.s3.region.amazonaws.com
                parts = host.split('.')
                if 's3' in parts:
                    bucket_idx = parts.index('s3')
                    bucket = '.'.join(parts[:bucket_idx])  # Full bucket name
                    region = parts[bucket_idx + 1] if bucket_idx + 1 < len(parts) else 'ap-southeast-2'
                else:
                    bucket = parts[0]
                    region = 'ap-southeast-2'
                
                key = parsed.path.lstrip('/')
                
                logger.info(f"S3 download: bucket={bucket}, region={region}, key={key}")
                
                # Get AWS credentials from environment
                aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID', '')
                aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
                
                if aws_access_key and aws_secret:
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret,
                        region_name=region
                    )
                else:
                    # Use default credentials
                    s3_client = boto3.client('s3', region_name=region)
                
                # Download file
                ext = os.path.splitext(key)[1] or '.webm'
                temp_file = os.path.join(self.temp_dir, f"audio{ext}")
                
                s3_client.download_file(bucket, key, temp_file)
                logger.info(f"Downloaded to: {temp_file}")
                return temp_file
            else:
                # Regular URL download
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    ext = os.path.splitext(url.split('?')[0])[1] or '.webm'
                    temp_file = os.path.join(self.temp_dir, f"audio{ext}")
                    
                    with open(temp_file, 'wb') as f:
                        f.write(response.content)
                    return temp_file
                
                return temp_file
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
        return None
    
    def convert_to_wav(self, input_path: str) -> Optional[str]:
        """
        Convert audio to WAV format optimized for Whisper
        Returns: path to converted file
        """
        output_path = os.path.join(self.temp_dir, "converted.wav")
        
        try:
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-i', input_path,
                '-ar', str(self.TARGET_SAMPLE_RATE),  # Sample rate
                '-ac', str(self.TARGET_CHANNELS),      # Mono
                '-acodec', 'pcm_s16le',                # 16-bit PCM
                '-t', '60',                            # Max 60 seconds
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
        
        return None
    
    def normalize_volume(self, input_path: str, target_db: float = -20.0) -> Optional[str]:
        """Normalize audio volume to target dB"""
        output_path = os.path.join(self.temp_dir, "normalized.wav")
        
        try:
            cmd = [
                'ffmpeg',
                '-y',
                '-i', input_path,
                '-af', f'volume={target_db}dB',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return output_path
                
        except Exception as e:
            logger.error(f"Error normalizing volume: {e}")
        
        return None
    
    def trim_silence(self, input_path: str, threshold_db: float = -40.0) -> Optional[str]:
        """Trim silence from beginning and end"""
        output_path = os.path.join(self.temp_dir, "trimmed.wav")
        
        try:
            # silenceremove at beginning and end
            cmd = [
                'ffmpeg',
                '-y',
                '-i', input_path,
                '-af', f'silenceremove=start_periods=1:start_duration=0.5:start_threshold={threshold_db}dB:detection=peak,silenceremove=stop_periods=-1:stop_duration=0.5:stop_threshold={threshold_db}dB:detection=peak',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return output_path
                
        except Exception as e:
            logger.error(f"Error trimming silence: {e}")
        
        return None
    
    def process(self, audio_url: str) -> Optional[str]:
        """
        Full preprocessing pipeline - simplified
        Just download the file, don't convert (Faster Whisper handles formats)
        """
        import uuid
        
        logger.info(f"Processing audio from: {audio_url}")
        
        # Use a fixed temp directory to avoid cleanup issues
        self.temp_dir = "/tmp/bodgongua_audio"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Step 1: Download
        local_path = self.download_from_url(audio_url)
        if not local_path:
            logger.error("Failed to download audio")
            return None
        
        # Step 2: Validate
        is_valid, error = self.validate_audio(local_path)
        if not is_valid:
            logger.error(f"Audio validation failed: {error}")
            return None
        
        # Step 3: Check duration
        duration = self.get_duration(local_path)
        if duration and duration < 1.0:
            logger.error("Audio too short (less than 1 second)")
            return None
        
        # Skip conversion - use original file (Faster Whisper handles webm/mp3/wav)
        logger.info(f"Audio file ready: {local_path}")
        return local_path
    
    def cleanup(self):
        """Clean up temp files"""
        import shutil
        try:
            shutil.rmtree(self.temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")


def preprocess_audio(audio_url: str) -> Optional[str]:
    """Convenience function for preprocessing"""
    preprocessor = AudioPreprocessor()
    try:
        return preprocessor.process(audio_url)
    finally:
        preprocessor.cleanup()
