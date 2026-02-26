import axios from 'axios';

// OpenRouter API configuration
const getOpenRouterKey = () => process.env.OPENROUTER_API_KEY || '';
const OPENROUTER_BASE_URL = 'https://openrouter.ai/api/v1';

// Use stepfun/step-3.5-flash:free only
const DEFAULT_MODEL = 'stepfun/step-3.5-flash:free';

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatResponse {
  success: boolean;
  message?: string;
  error?: string;
}

export async function sendToAI(messages: ChatMessage[]): Promise<ChatResponse> {
  // If no API key, return mock response
  if (!getOpenRouterKey()) {
    console.log('OpenRouter API key not set, using mock response');
    return getMockResponse(messages);
  }

  try {
    const response = await axios.post(
      `${OPENROUTER_BASE_URL}/chat/completions`,
      {
        model: DEFAULT_MODEL,
        messages: messages,
        max_tokens: 500,
      },
      {
        headers: {
          'Authorization': `Bearer ${getOpenRouterKey()}`,
          'Content-Type': 'application/json',
          'HTTP-Referer': 'http://localhost:3000',
          'X-Title': 'BoDongGua',
        },
        timeout: 30000,
      }
    );

    const aiMessage = response.data.choices?.[0]?.message?.content;
    
    return {
      success: true,
      message: aiMessage || 'No response from AI',
    };
  } catch (error: any) {
    console.error('OpenRouter API error:', error.message);
    return getMockResponse(messages);
  }
}

// Mock responses for when API key is not available
function getMockResponse(messages: ChatMessage[]): ChatResponse {
  const lastMessage = messages[messages.length - 1]?.content.toLowerCase() || '';
  
  let response = '';
  
  if (lastMessage.includes('你好') || lastMessage.includes('hello') || lastMessage.includes('hi')) {
    response = '你好！我是你的普通话学习助手。有什么我可以帮助你的吗？';
  } else if (lastMessage.includes('谢谢') || lastMessage.includes('thank')) {
    response = '不客气！继续加油练习普通话吧！';
  } else if (lastMessage.includes('再见') || lastMessage.includes('bye')) {
    response = '再见！记得每天练习哦！';
  } else if (lastMessage.includes('怎么') || lastMessage.includes('how')) {
    response = '这个问题问得好！建议你多听多说，模仿标准普通话发音。';
  } else if (lastMessage.includes('好') || lastMessage.includes('good')) {
    response = '很高兴你觉得好！我们继续练习吧！';
  } else if (lastMessage.includes('读') || lastMessage.includes('发音')) {
    response = '发音很重要！注意声调的变化：一声高平，二声上升，三声降升，四声下降。多练习哦！';
  } else if (lastMessage.includes('声调') || lastMessage.includes('tone')) {
    response = '普通话有四个声调：\n1. ā（高平）\n2. á（上升）\n3. ǎ（降升）\n4. à（下降）\n练习时要特别注意！';
  } else if (lastMessage.includes('zh') || lastMessage.includes('ch') || lastMessage.includes('sh')) {
    response = '卷舌音 zh, ch, sh, r 是 Cantonese speakers 的难点！记得舌头要翘起来碰到上颚。';
  } else {
    response = '很好！继续练习吧。你想练习哪个部分？可以选择声调、发音或者会话练习。';
  }
  
  return {
    success: true,
    message: response,
  };
}

export default { sendToAI };
