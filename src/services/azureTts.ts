import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import s3Client from '../config/s3';
import { PutObjectCommand } from '@aws-sdk/client-s3';

// Azure Speech configuration
const getAzureKey = () => process.env.AZURE_SPEECH_KEY || '';
const getAzureRegion = () => process.env.AZURE_SPEECH_REGION || 'southeastasia';

// Voice names for Azure
const VOICES: Record<string, string> = {
  'bunny': 'zh-CN-XiaoxiaoNeural',      // Female - friendly
  'cat': 'zh-CN-YunxiNeural',            // Male - witty  
  'owl': 'zh-CN-YunyangNeural',          // Male - wise
  'female': 'zh-CN-XiaoxiaoNeural',
  'male': 'zh-CN-YunxiNeural',
};

interface TTSResponse {
  success: boolean;
  audioUrl?: string;
  error?: string;
}

export async function textToSpeech(text: string, character: string = 'bunny'): Promise<TTSResponse> {
  try {
    const apiKey = getAzureKey();
    const region = getAzureRegion();
    
    if (!apiKey) {
      console.log('Azure Speech key not set, skipping TTS');
      return { success: true, audioUrl: undefined };
    }

    const voice = VOICES[character] || VOICES['bunny'];
    console.log(`Azure TTS: using voice ${voice}`);

    const response = await axios({
      method: 'POST',
      url: `https://${region}.tts.speech.microsoft.com/cognitiveservices/v1`,
      headers: {
        'Ocp-Apim-Subscription-Key': apiKey,
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'audio-16khz-128kbitrate-mp3',
      },
      data: `
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='zh-CN'>
          <voice name='${voice}'>
            ${text}
          </voice>
        </speak>
      `,
      responseType: 'arraybuffer',
      timeout: 30000,
    });

    // Upload audio to S3
    const audioKey = `tts/${uuidv4()}.mp3`;
    const bucketName = process.env.AWS_BUCKET_NAME || 'bodonggua-audio';
    
    await s3Client.send(new PutObjectCommand({
      Bucket: bucketName,
      Key: audioKey,
      Body: Buffer.from(response.data),
      ContentType: 'audio/mpeg',
    }));

    const audioUrl = `https://${bucketName}.s3.${process.env.AWS_REGION || 'ap-southeast-2'}.amazonaws.com/${audioKey}`;
    
    console.log('Azure TTS audio saved:', audioUrl);
    
    return {
      success: true,
      audioUrl: audioUrl,
    };
  } catch (error: any) {
    console.error('Azure TTS error:', error.message);
    return {
      success: true,
      audioUrl: undefined,
    };
  }
}

export default { textToSpeech };
