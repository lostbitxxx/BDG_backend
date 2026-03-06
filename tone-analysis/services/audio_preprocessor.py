"""
Audio Preprocessing Service
Converts audio to iFlytek required format: PCM 16kHz mono
"""

import os
import tempfile
import subprocess
import logging
import shutil

logger = logging.getLogger(__name__)


class AudioPreprocessor:
    """Audio preprocessing for iFlytek ISE"""
    
    TARGET_SAMPLE_RATE = 16000
    TARGET_CHANNELS = 1
    TARGET_FORMAT = "wav"
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix='bodgongua_')
        self.downloaded_file = None
        self.converted_file = None
    
    def process(self, audio_url: str) -> str:
        """
        Main processing pipeline:
        1. Download from S3
        2. Convert to PCM 16kHz mono
        3. Return path to processed file
        """
        # Step 1: Download
        logger.info(f"Downloading audio from: {audio_url}")
        downloaded = self._download_audio(audio_url)
        if not downloaded:
            logger.error("Failed to download audio")
            return None
        
        self.downloaded_file = downloaded
        
        # Step 2: Convert to PCM 16kHz mono
        logger.info("Converting to PCM 16kHz mono...")
        converted = self._convert_audio(downloaded)
        if not converted:
            logger.error("Failed to convert audio")
            return None
        
        self.converted_file = converted
        
        # Step 3: Validate
        if not self._validate_audio(converted):
            logger.error("Converted audio validation failed")
            return None
        
        logger.info(f"Processed audio: {converted}")
        return converted
    
    def _download_audio(self, url: str) -> str:
        """Download audio from URL (S3 or other)"""
        import boto3
        import requests
        
        # Check if S3 URL
        if 's3.ap-southeast-2.amazonaws.com' in url:
            # Extract bucket and key
            # URL format: https://bodonggua-audio.s3.ap-southeast-2.amazonaws.com/audio/e95bfeeb-f196-46e0-87ae-93ee1d093459.webm
            parts = url.replace('https://', '').split('/')
            bucket = parts[0].split('.')[0]
            # Key is everything after the bucket: audio/xxx.webm
            key = '/'.join(parts[1:])
            
            logger.info(f"S3 download: bucket={bucket}, key={key}")
            
            try:
                s3 = boto3.client('s3')
                temp_file = os.path.join(self.temp_dir, 'input_audio')
                
                s3.download_file(bucket, key, temp_file)
                logger.info(f"Downloaded to: {temp_file}")
                return temp_file
            except Exception as e:
                logger.error(f"S3 download error: {e}")
                return None
        
        # Generic download
        try:
            temp_file = os.path.join(self.temp_dir, 'input_audio')
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                return temp_file
        except Exception as e:
            logger.error(f"Download error: {e}")
            return None
    
    def _convert_audio(self, input_file: str) -> str:
        """Convert audio to PCM 16kHz mono using ffmpeg"""
        output_file = os.path.join(self.temp_dir, 'processed.wav')
        
        try:
            # Prefer explicit FFMPEG_PATH (easier on Windows), fallback to PATH
            ffmpeg_path = os.environ.get('FFMPEG_PATH') or shutil.which('ffmpeg')
            if not ffmpeg_path:
                logger.error("ffmpeg not found. Set FFMPEG_PATH in tone-analysis/.env to the full path of ffmpeg.exe or add ffmpeg to PATH.")
                return None
            
            # Convert
            cmd = [
                ffmpeg_path,
                '-i', input_file,
                '-ar', str(self.TARGET_SAMPLE_RATE),
                '-ac', str(self.TARGET_CHANNELS),
                '-acodec', 'pcm_s16le',
                '-y',  # Overwrite
                output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and os.path.exists(output_file):
                logger.info(f"Converted successfully: {output_file}")
                return output_file
            
            logger.error(f"ffmpeg error (code {result.returncode}): {result.stderr}")
            return None
                
        except subprocess.TimeoutExpired:
            logger.error("ffmpeg timeout")
            return None
        except Exception as e:
            logger.error(f"Conversion error: {e}")
            return None
    
    def _validate_audio(self, audio_file: str) -> bool:
        """Validate audio file"""
        if not os.path.exists(audio_file):
            return False
        
        file_size = os.path.getsize(audio_file)
        
        # Minimum: 1000 bytes (~0.03 seconds at 16kHz)
        if file_size < 1000:
            logger.error(f"Audio too small: {file_size} bytes")
            return False
        
        # Maximum: 50MB
        if file_size > 50 * 1024 * 1024:
            logger.error(f"Audio too large: {file_size} bytes")
            return False
        
        # Check if valid audio
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                 audio_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                duration = float(result.stdout.strip())
                logger.info(f"Audio duration: {duration:.2f}s")
                
                # Must be at least 1 second
                if duration < 1.0:
                    logger.warning(f"Audio too short: {duration}s")
                    # Still return true, let iFlytek handle it
                
                # Must be less than 60 seconds
                if duration > 60:
                    logger.warning(f"Audio too long: {duration}s")
                    return False
                    
        except Exception as e:
            logger.warning(f"Could not get duration: {e}")
        
        return True
    
    def get_duration(self, audio_file: str) -> float:
        """Get audio duration"""
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 
                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                 audio_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return None
    
    def cleanup(self):
        """Clean up temp files"""
        import shutil
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up: {self.temp_dir}")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
