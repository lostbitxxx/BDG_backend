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

# Max audio duration in seconds (0 = no limit). Default 300 seconds (5 minutes)
MAX_AUDIO_DURATION = int(os.environ.get('MAX_AUDIO_DURATION', 300))


def enhance_audio(audio_path: str) -> str:
    """
    Apply audio enhancement: noise reduction, silence removal, normalization
    Returns path to enhanced audio file
    """
    import noisereduce as nr
    import soundfile as sf
    import numpy as np

    try:
        # Load audio
        audio, sr = sf.read(audio_path)

        # Convert stereo to mono if needed
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        duration = len(audio) / sr
        logger.info(f"Enhancing audio: {duration:.2f}s at {sr}Hz")

        # Calculate RMS BEFORE
        rms_before = np.sqrt(np.mean(audio**2))
        logger.info(f"RMS before: {rms_before:.4f}, max: {np.max(np.abs(audio)):.4f}")

        # Skip if audio is too short
        if len(audio) < sr * 0.5:
            logger.warning("Audio too short for enhancement")
            return audio_path

        # 1. Noise reduction - use beginning as noise profile
        try:
            # Use first 0.5 seconds as noise sample
            noise_sample = audio[:int(sr * 0.5)]
            audio = nr.reduce_noise(y=audio, sr=sr, y_noise=noise_sample, n_std_thresh=0.5, prop_decrease=1.0)
            logger.info("Noise reduction applied")
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")

        # 2. Remove silence at beginning and end
        try:
            # Find non-silent parts (threshold 0.01)
            abs_audio = np.abs(audio)
            threshold = 0.01
            non_silent = abs_audio > threshold

            if np.any(non_silent):
                # Find first and last non-silent samples
                indices = np.where(non_silent)[0]
                start_idx = max(0, indices[0] - int(sr * 0.1))  # Keep 100ms before speech
                end_idx = min(len(audio), indices[-1] + int(sr * 0.1))  # Keep 100ms after speech
                audio = audio[start_idx:end_idx]
                logger.info(f"Trimmed silence: {start_idx} to {end_idx}")
        except Exception as e:
            logger.warning(f"Silence removal failed: {e}")

        # 3. Volume normalization - aggressive boost
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            # Target RMS of 0.5 (iFlytek likes moderate volume)
            target_rms = 0.5
            # Apply gain, capped at 15x
            gain = min(target_rms / rms, 15.0)
            audio = audio * gain
            # Soft clip to prevent harsh clipping
            audio = np.tanh(audio)
            logger.info(f"Applied gain: {gain:.2f}x")

        # 4. Ensure 16kHz sample rate
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr = 16000
            logger.info("Resampled to 16kHz")

        # Calculate RMS AFTER
        rms_after = np.sqrt(np.mean(audio**2))
        max_after = np.max(np.abs(audio))
        duration_after = len(audio) / sr
        logger.info(f"RMS after: {rms_after:.4f}, max: {max_after:.4f}, duration: {duration_after:.2f}s")

        # Save enhanced audio
        sf.write(audio_path, audio, sr)
        logger.info(f"Audio enhanced successfully")

        return audio_path

    except Exception as e:
        logger.error(f"Audio enhancement failed: {e}", exc_info=True)
        return audio_path


def check_audio_quality(audio_path: str) -> dict:
    """
    Check audio quality metrics
    Returns dict with quality metrics and warnings
    """
    import soundfile as sf
    import numpy as np

    try:
        audio, sr = sf.read(audio_path)

        # Convert stereo to mono if needed
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        duration = len(audio) / sr

        # Calculate metrics
        rms = np.sqrt(np.mean(audio**2))
        max_val = np.max(np.abs(audio))

        # Calculate signal-to-noise ratio (simplified)
        # Use quiet parts as noise estimate
        sorted_audio = np.sort(np.abs(audio))
        noise_estimate = np.mean(sorted_audio[:int(len(sorted_audio) * 0.1)])
        if noise_estimate > 0:
            snr = 20 * np.log10(rms / noise_estimate) if noise_estimate > 0 else 0
        else:
            snr = 100  # Very clean audio

        # Check for silence (too quiet)
        is_too_quiet = rms < 0.01
        # Check for clipping (too loud)
        is_clipping = max_val >= 0.99
        # Check for very short audio
        is_too_short = duration < 1.0
        # Check for low SNR
        is_low_snr = snr < 10

        result = {
            'duration': round(duration, 2),
            'rms': round(rms, 4),
            'max': round(max_val, 4),
            'snr': round(snr, 2),
            'warnings': []
        }

        if is_too_quiet:
            result['warnings'].append('Audio is too quiet - speak louder')
        if is_clipping:
            result['warnings'].append('Audio may be clipping - speak at normal volume')
        if is_too_short:
            result['warnings'].append('Audio is very short')
        if is_low_snr:
            result['warnings'].append('High background noise - record in quieter environment')

        logger.info(f"Audio quality check: {result}")
        return result

    except Exception as e:
        logger.warning(f"Audio quality check failed: {e}")
        return {'warnings': [], 'error': str(e)}


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

        # Step 2.5: Enhance audio (noise reduction, normalization)
        logger.info("Enhancing audio quality...")
        try:
            enhanced = enhance_audio(converted)
            if not enhanced:
                logger.warning("Audio enhancement returned None, using original")
            else:
                logger.info(f"Audio enhanced successfully: {enhanced}")
        except Exception as e:
            logger.warning(f"Audio enhancement error: {e}, using original")

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
                
                # Check max duration (0 = no limit)
                if MAX_AUDIO_DURATION > 0 and duration > MAX_AUDIO_DURATION:
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
