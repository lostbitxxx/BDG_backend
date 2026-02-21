import express from 'express';

const router = express.Router();

// Interface for chat request
interface ChatRequest {
  message: string;
}

// Interface for chat response
interface ChatResponse {
  success: boolean;
  response?: string;
  timestamp: string;
  error?: string;
}

// Interface for Ollama API response
interface OllamaResponse {
  message: {
    content: string;
  };
}

// Interface for Hugging Face API response
interface HuggingFaceResponse {
  generated_text: string;
}

// Function to call Ollama (Local AI - Free)
async function callOllamaAPI(message: string): Promise<string> {
  try {
    const response = await fetch('http://localhost:11434/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'llama3.2:1b', // Small, fast model
        messages: [
          {
            role: 'system',
            content: 'You are a helpful and friendly AI assistant. Keep responses concise and engaging.'
          },
          {
            role: 'user',
            content: message
          }
        ],
        stream: false
      }),
    });

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.status}`);
    }

    const data: OllamaResponse = await response.json();
    return data.message.content;
  } catch (error) {
    console.error('Ollama API error:', error);
    throw new Error('Ollama service unavailable. Make sure Ollama is running locally.');
  }
}

// Function to call Hugging Face (Free with API key)
async function callHuggingFaceAPI(message: string): Promise<string> {
  const apiKey = process.env.HUGGINGFACE_API_KEY;
  
  if (!apiKey) {
    throw new Error('HUGGINGFACE_API_KEY not configured');
  }

  try {
    const response = await fetch('https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        inputs: message,
        parameters: {
          max_new_tokens: 100,
          temperature: 0.7
        }
      }),
    });

    if (!response.ok) {
      throw new Error(`Hugging Face API error: ${response.status}`);
    }

    const data: HuggingFaceResponse[] = await response.json();
    return data[0]?.generated_text?.replace(message, '').trim() || 'I understand what you\'re asking!';
  } catch (error) {
    console.error('Hugging Face API error:', error);
    throw new Error('Hugging Face service unavailable');
  }
}

// Function to get AI response with fallback options
async function getAIResponse(message: string): Promise<string> {
  const aiProvider = process.env.AI_PROVIDER || 'ollama';
  
  try {
    switch (aiProvider.toLowerCase()) {
      case 'ollama':
        return await callOllamaAPI(message);
      case 'huggingface':
        return await callHuggingFaceAPI(message);
      default:
        // Fallback to simple responses if no AI service available
        const fallbackResponses = [
          "That's interesting! Tell me more about your thoughts.",
          "I find that really intriguing. Can you elaborate?",
          "How does that make you feel?",
          "I'm here to listen and discuss whatever interests you.",
          "That's a thoughtful point. What led you to think about that?"
        ];
        return fallbackResponses[Math.floor(Math.random() * fallbackResponses.length)]!;
    }
  } catch (error) {
    console.error('AI service error, using fallback:', error);
    // Fallback response if AI services fail
    return "I'm having trouble connecting to my AI service right now, but I'm still here to chat! What would you like to talk about?";
  }
}

// POST /api/chat
router.post('/chat', async (req: express.Request<{}, ChatResponse, ChatRequest>, res) => {
  try {
    const { message } = req.body;
    
    // Validation
    if (!message || typeof message !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'Message is required and must be a string',
        timestamp: new Date().toISOString()
      });
    }

    if (message.trim().length === 0) {
      return res.status(400).json({
        success: false,
        error: 'Message cannot be empty',
        timestamp: new Date().toISOString()
      });
    }

    if (message.length > 1000) {
      return res.status(400).json({
        success: false,
        error: 'Message is too long (max 1000 characters)',
        timestamp: new Date().toISOString()
      });
    }
    
    // Get AI response
    const aiResponse = await getAIResponse(message.trim());
    
    // Log the interaction
    console.log(`Chat interaction - User: "${message.trim()}" | AI: "${aiResponse.substring(0, 100)}..."`);
    
    res.json({
      success: true,
      response: aiResponse,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Chat endpoint error:', error);
    
    const errorMessage = error instanceof Error ? error.message : 'Internal server error';
    
    res.status(500).json({
      success: false,
      error: errorMessage,
      timestamp: new Date().toISOString()
    });
  }
});

export default router;
