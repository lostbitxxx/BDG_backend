import axios from 'axios';
import s3Client from '../config/s3';
import { PutObjectCommand } from '@aws-sdk/client-s3';
import { v4 as uuidv4 } from 'uuid';

// ElevenLabs API configuration
const getElevenLabsKey = () => process.env.ELEVENLABS_API_KEY || '';
const ELEVENLABS_BASE_URL = 'https://api.elevenlabs.io/v1';

// Voice IDs from environment
const getVoiceId = (gender: 'male' | 'female' = 'female') => {
  if (gender === 'male') {
    return process.env.ELEVENLABS_VOICE_MALE || 'DowyQ68vDpgFYdWVGjc3';
  }
  return process.env.ELEVENLABS_VOICE_FEMALE || '9lHjugDhwqoxA5MhX0az';
};

interface TTSResponse {
  success: boolean;
  audioUrl?: string;
  audioBase64?: string;
  error?: string;
}

export async function textToSpeech(text: string, gender: 'male' | 'female' = 'female'): Promise<TTSResponse> {
  try {
    const apiKey = getElevenLabsKey();

    // If no API key, return empty
    if (!apiKey) {
      console.log('ElevenLabs API key not set, skipping TTS');
      return { success: true, audioUrl: undefined };
    }

    const voiceId = getVoiceId(gender);
    console.log('Using ElevenLabs with voice ID:', voiceId, 'API key starts with:', apiKey.substring(0, 8));

    const response = await axios.post(
      `${ELEVENLABS_BASE_URL}/text-to-speech/${voiceId}`,
      {
        text: text,
        model_id: 'eleven_multilingual_v2',
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
        },
      },
      {
        headers: {
          'Accept': 'audio/mpeg',
          'Content-Type': 'application/json',
          'xi-api-key': apiKey,
        },
        responseType: 'arraybuffer',
        timeout: 30000,
      }
    );

    // Prepare audio buffer and base64
    const audioBuffer = Buffer.from(response.data);
    const audioBase64 = audioBuffer.toString('base64');

    // Upload audio to S3
    const audioKey = `tts/${uuidv4()}.mp3`;
    const bucketName = process.env.AWS_BUCKET_NAME || 'bodonggua-audio';
    
    await s3Client.send(new PutObjectCommand({
      Bucket: bucketName,
      Key: audioKey,
      Body: audioBuffer,
      ContentType: 'audio/mpeg',
    }));

    const audioUrl = `https://${bucketName}.s3.${process.env.AWS_REGION || 'ap-southeast-2'}.amazonaws.com/${audioKey}`;
    
    console.log('TTS audio saved:', audioUrl);
    
    return {
      success: true,
      audioUrl,
      audioBase64,
    };
  } catch (error: any) {
    console.error('ElevenLabs API error:', error.message);
    if (error.response) {
      console.error('ElevenLabs response status:', error.response.status);
      console.error('ElevenLabs response data:', error.response.data);
    }
    return {
      success: true, // Don't fail the whole chat
      audioUrl: undefined,
    };
  }
}

export default { textToSpeech };
