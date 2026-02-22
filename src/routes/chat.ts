import express, { Request, Response } from 'express';
import { isNonEmptyString } from '../utils/validation';

const router = express.Router();

const AI_RESPONSES: Record<string, string[]> = {
  greeting: [
    'Hello! How can I help you today?',
    "Hi there! What's on your mind?",
    'Hey! What would you like to talk about?'
  ],
  question: [
    "That's an interesting question!",
    "Great question! I'd be happy to help.",
    "I understand what you're asking."
  ],
  thanks: [
    "You're very welcome!",
    'My pleasure!',
    'Happy to help!'
  ],
  default: [
    "That's interesting! Tell me more.",
    'Can you elaborate on that?',
    'How does that make you feel?',
    "That's a thoughtful point."
  ]
};

function pickResponse(message: string): string {
  const lower = message.toLowerCase();
  let key: keyof typeof AI_RESPONSES = 'default';

  if (/\b(hello|hi|hey)\b/.test(lower)) key = 'greeting';
  else if (lower.includes('?')) key = 'question';
  else if (lower.includes('thank')) key = 'thanks';

  const pool = AI_RESPONSES[key];
  return pool[Math.floor(Math.random() * pool.length)];
}

// POST /api/chat
router.post('/chat', (req: Request, res: Response) => {
  const { message } = req.body as { message: unknown };

  if (!isNonEmptyString(message)) {
    return res.status(400).json({ success: false, error: 'Message is required' });
  }
  if (message.length > 1000) {
    return res.status(400).json({ success: false, error: 'Message too long (max 1000 characters)' });
  }

  return res.json({
    success: true,
    response: pickResponse(message),
    timestamp: new Date().toISOString()
  });
});

export default router;
