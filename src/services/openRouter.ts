import axios from 'axios';
import 'dotenv/config';

// OpenRouter API configuration
const getOpenRouterKey = () => process.env.OPENROUTER_API_KEY || '';
const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1';

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  success: boolean;
  message?: string;
  error?: string;
}

// Using stepfun/step-3.5-flash:free model
const DEFAULT_MODEL = 'stepfun/step-3.5-flash:free';

export async function sendToAI(messages: ChatMessage[]): Promise<ChatResponse> {
  // Try OpenRouter first
  const apiKey = getOpenRouterKey();
  if (apiKey) {
    try {
      return await sendToOpenRouter(messages, apiKey);
    } catch (error) {
      console.error('OpenRouter API error:', error);
    }
  }

  // Fallback to mock response
  console.log('Using mock response');
  return getMockResponse(messages);
}

async function sendToOpenRouter(messages: ChatMessage[], apiKey: string): Promise<ChatResponse> {
  try {
    const response = await axios.post(
      `${OPENROUTER_BASE_URL}/chat/completions`,
      {
        model: DEFAULT_MODEL,
        messages: messages,
        max_tokens: 4000,
        temperature: 0.7,
      },
      {
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'http://localhost:3001',
          'X-Title': 'BDG Mandarin Practice',
        },
        timeout: 120000, // 2 minute timeout
      }
    );

    console.log('OpenRouter response:', JSON.stringify(response.data).slice(0, 500));

    const choices = response.data?.choices;
    let aiMessage = choices?.[0]?.message?.content ||
                    choices?.[0]?.delta?.content ||
                    response.data?.text;

    // If still no content, try to get from the first choice's message object
    if (!aiMessage && choices?.[0]?.message) {
      const msg = choices[0].message;
      aiMessage = msg.content || msg.text || (typeof msg === 'string' ? msg : null);
    }

    // Log what we found
    console.log('Extracted AI message:', aiMessage?.slice(0, 200) || 'NULL');

    if (aiMessage) {
      return { success: true, message: aiMessage };
    }

    // Check for error in response
    if (response.data?.error) {
      console.log('OpenRouter error:', response.data.error);
      return { success: false, error: response.data.error.message || 'OpenRouter error' };
    }

    return { success: false, error: 'No content in response' };
  } catch (error: any) {
    console.log('OpenRouter request error:', error.message);
    if (error.response?.data?.error) {
      return { success: false, error: error.response.data.error.message };
    }
    throw error;
  }
}

function getMockResponse(messages: ChatMessage[]): ChatResponse {
  const lastMessage = messages[messages.length - 1]?.content || '';

  // Simple mock responses
  const mockResponses: Record<string, string> = {
    'chat': '你好！我是你的普通话练习助手。有什么可以帮助你的吗？',
    'question': '好的，我来为你生成一些问题。',
    'default': '收到你的消息了！继续练习吧。'
  };

  let response = mockResponses.default;
  const lowerMsg = lastMessage.toLowerCase();

  if (lowerMsg.includes('问') || lowerMsg.includes('question')) {
    response = mockResponses.question;
  } else if (lowerMsg.includes('你好') || lowerMsg.includes('hi') || lowerMsg.includes('hello')) {
    response = mockResponses.chat;
  }

  return {
    success: true,
    message: response,
  };
}

export default { sendToAI };
