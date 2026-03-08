import WebSocket from 'ws';
import crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';

// iFlytek TTS configuration
const getAppId = () => process.env.IFLYTEK_APP_ID || '';
const getApiKey = () => process.env.IFLYTEK_API_KEY || '';
const getApiSecret = () => process.env.IFLYTEK_API_SECRET || '';

const IFLYTEK_WS_URL = 'wss://tts-api-sg.xf-yun.com/v2/tts';

// Voice parameters for different characters
const VOICES: Record<string, { vcn: string; speed: number; pitch: number }> = {
  'red-birdie': { vcn: 'x_xiaoyan', speed: 50, pitch: 50 },
  'foggy-birdie': { vcn: 'x_xiaolin', speed: 55, pitch: 55 },
  'final-birdie': { vcn: 'x_xiaoyang_story', speed: 45, pitch: 45 },
};

function getAuthUrl(): string {
  const now = new Date();
  const date = now.toUTCString();
  const host = 'tts-api-sg.xf-yun.com';
  const path = '/v2/tts';
  
  const signatureOrigin = `host: ${host}\ndate: ${date}\nGET ${path} HTTP/1.1`;
  const hmac = crypto.createHmac('sha256', getApiSecret());
  hmac.update(signatureOrigin);
  const signatureSha = hmac.digest('base64');
  
  const authorizationOrigin = `api_key="${getApiKey()}", algorithm="hmac-sha256", headers="host date request-line", signature="${signatureSha}"`;
  const authorization = Buffer.from(authorizationOrigin).toString('base64');
  
  return `${IFLYTEK_WS_URL}?authorization=${authorization}&date=${encodeURIComponent(date)}&host=${host}`;
}

interface TTSResponse {
  success: boolean;
  audioBase64?: string;
  error?: string;
}

export async function textToSpeech(text: string, character: string = 'red-birdie'): Promise<TTSResponse> {
  return new Promise(async (resolve) => {
    try {
      const appId = getAppId();
      const apiKey = getApiKey();
      
      if (!appId || !apiKey) {
        console.log('iFlytek credentials not set, skipping TTS');
        resolve({ success: true });
        return;
      }

      const voice = VOICES[character] || VOICES['red-birdie'];
      console.log(`iFlytek TTS: using voice ${voice.vcn} for ${character}`);

      const requestId = uuidv4().replace(/-/g, '');
      const authUrl = getAuthUrl();

      const ws = new WebSocket(authUrl);
      let audioData: Buffer[] = [];
      let isComplete = false;

      const cleanup = () => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.close();
        }
      };

      ws.on('open', () => {
        console.log('WebSocket connected');
        const message = {
          common: { app_id: appId },
          business: {
            aue: 'lame',
            vcn: voice.vcn,
            speed: voice.speed,
            pitch: voice.pitch,
            volume: 50,
            tte: 'UTF8',
          },
          data: {
            status: 2,
            text: Buffer.from(text).toString('base64'),
          }
        };
        ws.send(JSON.stringify(message));
      });

      ws.on('message', (data: Buffer) => {
        try {
          const response = JSON.parse(data.toString());
          if (response.code !== 0) {
            console.log('iFlytek error:', response.message);
            cleanup();
            resolve({ success: true });
            return;
          }
          if (response.data && response.data.audio) {
            audioData.push(Buffer.from(response.data.audio, 'base64'));
          }
          if (response.data && response.data.status === 2) {
            isComplete = true;
            cleanup();
          }
        } catch (e) {
          // Binary audio data
          audioData.push(data);
        }
      });

      ws.on('close', () => {
        console.log('WebSocket closed, audio chunks:', audioData.length);
        if (audioData.length > 0) {
          const combinedAudio = Buffer.concat(audioData);
          const base64 = combinedAudio.toString('base64');
          resolve({ success: true, audioBase64: base64 });
        } else {
          resolve({ success: true });
        }
      });

      ws.on('error', (err) => {
        console.error('WebSocket error:', err.message);
        resolve({ success: true });
      });

      setTimeout(() => {
        if (!isComplete) {
          console.log('TTS timeout');
          cleanup();
          resolve({ success: true });
        }
      }, 15000);

    } catch (error: any) {
      console.error('iFlytek TTS error:', error.message);
      resolve({ success: true });
    }
  });
}

export default { textToSpeech };
