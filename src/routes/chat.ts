import express, { Request, Response } from 'express';
import { isNonEmptyString } from '../utils/validation';
import { sendToAI } from '../services/openRouter';
import { generateSystemPrompt } from '../services/chatPrompt';
import { textToSpeech } from '../services/iflytekTts';

const router = express.Router();

// Strip emojis from text
function stripEmojis(text: string): string {
  return text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '');
}

// POST /api/chat
router.post('/chat', async (req: Request, res: Response) => {
  const { message, character = 'bunny' } = req.body as { 
    message: unknown; 
    character?: string;
  };

  if (!isNonEmptyString(message)) {
    return res.status(400).json({ success: false, error: 'Message is required' });
  }
  if (message.length > 1000) {
    return res.status(400).json({ success: false, error: 'Message too long (max 1000 characters)' });
  }

  try {
    // Build messages with character-specific system prompt
    const messages = [
      { role: 'system' as const, content: generateSystemPrompt(character) },
      { role: 'user' as const, content: message }
    ];

    // Send to OpenRouter AI
    const aiResult = await sendToAI(messages);

    if (!aiResult.success) {
      return res.status(500).json({ success: false, error: aiResult.error });
    }

    // Strip emojis from response
    const cleanResponse = stripEmojis(aiResult.message || '');

    // Generate TTS audio
    const ttsResult = await textToSpeech(cleanResponse, character);

    // Return audio as base64
    return res.json({
      success: true,
      response: cleanResponse,
      audioBase64: ttsResult.audioBase64,
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('Chat error:', error.message);
    return res.status(500).json({ success: false, error: 'Chat failed' });
  }
});

export default router;
