import express, { Request, Response } from 'express';
import { isNonEmptyString } from '../utils/validation';
import { sendToAI } from '../services/openRouter';
import { generateSystemPrompt } from '../services/chatPrompt';
import { textToSpeech } from '../services/elevenLabs';
import { getRandomQuestions } from '../data/questions';

const router = express.Router();

// Strip emojis from text
function stripEmojis(text: string): string {
  return text.replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F700}-\u{1F77F}\u{1F780}-\u{1F7FF}\u{1F800}-\u{1F8FF}\u{1F900}-\u{1F9FF}\u{1FA00}-\u{1FA6F}\u{1FA70}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, '');
}

// Map character to ElevenLabs gender
function getGenderForCharacter(character: string): 'male' | 'female' {
  switch (character) {
    case 'owl':
      return 'male';
    default:
      return 'female';
  }
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

    // Determine TTS voice gender based on character
    const gender = getGenderForCharacter(character);

    // Generate TTS audio with ElevenLabs
    const ttsResult = await textToSpeech(cleanResponse, gender);

    // Return audio as base64 (keeps API compatible)
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

// POST /api/tailored-practice - Generate tailored practice questions using AI analysis + question bank
router.post('/tailored-practice', async (req: Request, res: Response) => {
  const { userInput, categories, weaknesses, feedback, historyRecord } = req.body as {
    userInput?: string;
    categories?: string[];
    weaknesses?: string[];
    feedback?: string;
    historyRecord?: {
      feedbackEn: string;
      feedbackZh: string;
      weaknesses: string[];
      strengths: string[];
      overallScore: number;
    };
  };

  try {
    // Step 1: Map category IDs to question bank tags
    const categoryToTags: Record<string, string> = {
      'tone_1': 'tone_1',
      'tone_2': 'tone_2',
      'tone_3': 'tone_3',
      'tone_4': 'tone_4',
      'retroflex': 'retroflex',
      'nasal': 'nasal',
      'u_vs_ü': 'u_vs_ü',
      'zcs_zhchsh': 'retroflex',
      'n_vs_l': 'n_vs_l',
      'f_vs_h': 'f_vs_h',
      'an_vs_ang': 'an_vs_ang',
      'en_vs_eng': 'en_vs_eng',
      'in_vs_ing': 'in_vs_ing',
      'third_tone': 'third_tone',
      'neutral_tone': 'neutral_tone',
      'passive_ba': 'passive_ba',
      'le_structure': 'le_structure',
      'classifier': 'classifier',
    };

    // Map weakness names to tags
    const weaknessToTags: Record<string, string[]> = {
      'Single Characters': ['tone_1', 'tone_2', 'tone_3', 'tone_4', 'retroflex', 'n_vs_l'],
      'Polysyllabic Words': ['tone_1', 'tone_2', 'tone_3', 'tone_4', 'third_tone', 'an_vs_ang'],
      'Vocabulary & Grammar': ['classifier', 'passive_ba', 'le_structure', 'vocabulary'],
      'Reading Passage': ['tone_1', 'tone_2', 'tone_3', 'tone_4', 'neutral_tone', 'reading'],
      'Speaking': ['retroflex', 'nasal', 'n_vs_l', 'f_vs_h', 'pronunciation'],
    };

    let targetTags: string[] = [];

    // If categories provided directly, convert to tags
    if (categories && categories.length > 0) {
      targetTags = categories.map(c => categoryToTags[c]).filter(Boolean);
    }

    // If weaknesses provided, add their tags
    if (weaknesses && weaknesses.length > 0) {
      weaknesses.forEach(w => {
        const tags = weaknessToTags[w];
        if (tags) targetTags.push(...tags);
      });
      targetTags = [...new Set(targetTags)];
    }

    // Step 2: If we have user input or history record, use AI to analyze and determine focus areas
    let userPrompt = '';
    if (historyRecord) {
      userPrompt = `Analyze this PSC test feedback and determine which areas need practice most.
Previous feedback: ${historyRecord.feedbackEn}
Weak areas: ${historyRecord.weaknesses.join(', ')}
Previous score: ${historyRecord.overallScore}%

Respond ONLY with a JSON array of tag names to focus on from this list:
tone_1, tone_2, tone_3, tone_4, retroflex, nasal, n_vs_l, f_vs_h, an_vs_ang, en_vs_eng, in_vs_ing, third_tone, neutral_tone, classifier, passive_ba, le_structure, vocabulary, reading

Example: ["retroflex", "n_vs_l", "third_tone"]`;
    } else if (userInput) {
      userPrompt = `Analyze this user's practice request and determine which areas to focus on.
User request: "${userInput}"

Respond ONLY with a JSON array of tag names from this list:
tone_1, tone_2, tone_3, tone_4, retroflex, nasal, n_vs_l, f_vs_h, an_vs_ang, en_vs_eng, in_vs_ing, third_tone, neutral_tone, classifier, passive_ba, le_structure, vocabulary, reading

Example: ["third_tone", "retroflex"]`;
    }

    // If we have user input or history, get AI analysis to refine tags
    if (userPrompt) {
      const analysisMessages = [
        { role: 'system' as const, content: 'You are a PSC (Putonghua Shuiping Ceshi) expert. Analyze user requests and determine which pronunciation/grammar areas need practice. Respond ONLY with a JSON array of tag names.' },
        { role: 'user' as const, content: userPrompt }
      ];

      try {
        const aiAnalysis = await sendToAI(analysisMessages);
        if (aiAnalysis.success && aiAnalysis.message) {
          // Parse AI's tag suggestions
          const jsonMatch = aiAnalysis.message.match(/\[[\s\S]*\]/);
          if (jsonMatch) {
            const aiTags = JSON.parse(jsonMatch[0]);
            if (Array.isArray(aiTags)) {
              // Merge AI suggestions with existing tags
              targetTags = [...new Set([...targetTags, ...aiTags])];
            }
          }
        }
      } catch (analysisError) {
        console.error('AI analysis error:', analysisError);
        // Continue with existing tags
      }
    }

    // Step 3: Extract questions from question bank based on determined tags
    let selectedQuestions = getRandomQuestions(10, targetTags.length > 0 ? targetTags : undefined);

    // If not enough questions found, get random ones
    if (selectedQuestions.length < 10) {
      selectedQuestions = getRandomQuestions(10);
    }

    // Format questions for frontend
    const formattedQuestions = selectedQuestions.map(q => ({
      content: q.content,
      pinyin: q.pinyin || '',
      type: q.type === 'choice' ? 'vocabulary' : q.type === 'reading' && q.section === 4 ? 'reading' : 'tone',
      difficulty: q.section === 1 ? 'easy' : q.section === 2 ? 'medium' : 'hard',
      hint: q.tags ? q.tags.join(', ') : undefined,
      section: q.section,
      id: q.id
    }));

    return res.json({
      success: true,
      questions: formattedQuestions,
      analyzedTags: targetTags,
      generatedFor: historyRecord ? 'history' : 'custom',
      questionCount: formattedQuestions.length,
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    console.error('Tailored practice error:', error.message);
    return res.status(500).json({ success: false, error: 'Failed to generate practice questions' });
  }
});

export default router;
