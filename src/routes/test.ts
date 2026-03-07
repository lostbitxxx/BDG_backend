/**
 * PSC Test Routes
 * Handles test sessions, question generation, and scoring
 */

import express, { Request, Response } from 'express';
import crypto from 'crypto';
import {
  generateSection1Questions,
  generateSection2Questions,
  generateSection3Questions,
  generateSection4Questions,
  generateSection5Questions,
  generateFullTest,
  generatePartialTest
} from '../services/questionGenerator';
import {
  calculateFullPSCScore,
  calculateSection1Score,
  calculateSection2Score,
  calculateSection3Score,
  calculateSection4Score,
  calculateSection5Score,
  TestResponse,
  Section3Answers,
  Section5Analysis
} from '../services/scoring/pscScoring';
import { SECTION_CONFIG } from '../data/psc';

const router = express.Router();

// In-memory storage for test sessions (use Redis in production)
interface TestSession {
  id: string;
  type: 'full' | 'partial';
  partialSection?: 1 | 2 | 3 | 4 | 5;
  questions: Record<1 | 2 | 3 | 4 | 5, any[]>;
  responses: Record<1 | 2 | 3 | 4 | 5, any>;
  durations: Record<1 | 2 | 3 | 4 | 5, number>;
  startTime: Date;
  status: 'pending' | 'in_progress' | 'completed';
  completedSections: number[];
}

const sessions: Map<string, TestSession> = new Map();

const SECTION_IDS = [1, 2, 3, 4, 5] as const;

// GET /api/test/sections - List sections for full practice (1–5)
router.get('/sections', (_req: Request, res: Response) => {
  const sections = SECTION_IDS.map((section) => {
    const config = SECTION_CONFIG[section];
    return {
      section,
      name: config.name,
      nameEn: config.nameEn,
      timeLimit: config.timeLimit,
    };
  });
  res.json({ success: true, sections, total: 5 });
});

// POST /api/test/start - Start a new test session
router.post('/start', async (req: Request, res: Response) => {
  try {
    const { type, section } = req.body;

    if (!type || !['full', 'partial'].includes(type)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid test type. Must be "full" or "partial"'
      });
    }

    const sessionId = crypto.randomUUID();
    const questions = type === 'full'
      ? generateFullTest(Date.now())
      : { [section]: generatePartialTest(section, Date.now()) };

    const session: TestSession = {
      id: sessionId,
      type,
      partialSection: type === 'partial' ? section : undefined,
      questions: questions as TestSession['questions'],
      responses: {} as TestSession['responses'],
      durations: {} as TestSession['durations'],
      startTime: new Date(),
      status: 'in_progress',
      completedSections: []
    };

    sessions.set(sessionId, session);

    // Return questions based on test type
    const returnQuestions = type === 'full'
      ? questions
      : questions[section as 1 | 2 | 3 | 4 | 5];

    res.json({
      success: true,
      sessionId,
      type,
      section: type === 'partial' ? section : undefined,
      questions: returnQuestions,
      timeLimits: SECTION_CONFIG
    });
  } catch (error) {
    console.error('Error starting test:', error);
    res.status(500).json({ success: false, error: 'Failed to start test' });
  }
});

// GET /api/test/:sessionId - Get test session status
router.get('/:sessionId', (req: Request, res: Response) => {
  try {
    const { sessionId } = req.params;
    const session = sessions.get(sessionId);

    if (!session) {
      return res.status(404).json({ success: false, error: 'Session not found' });
    }

    res.json({
      success: true,
      session: {
        id: session.id,
        type: session.type,
        partialSection: session.partialSection,
        status: session.status,
        startTime: session.startTime,
        completedSections: session.completedSections
      }
    });
  } catch (error) {
    console.error('Error getting session:', error);
    res.status(500).json({ success: false, error: 'Failed to get session' });
  }
});

// POST /api/test/:sessionId/submit/:section - Submit a section
router.post('/:sessionId/submit/:section', (req: Request, res: Response) => {
  try {
    const { sessionId, section } = req.params;
    const { response, duration } = req.body;

    const session = sessions.get(sessionId);
    if (!session) {
      return res.status(404).json({ success: false, error: 'Session not found' });
    }

    const sectionNum = parseInt(section) as 1 | 2 | 3 | 4 | 5;
    if (isNaN(sectionNum) || sectionNum < 1 || sectionNum > 5) {
      return res.status(400).json({ success: false, error: 'Invalid section' });
    }

    // Store response and duration
    session.responses[sectionNum] = response;
    session.durations[sectionNum] = duration;
    session.completedSections.push(sectionNum);

    // Calculate score for this section
    let score;
    switch (sectionNum) {
      case 1:
        score = calculateSection1Score(response as TestResponse, duration);
        break;
      case 2:
        score = calculateSection2Score(response as TestResponse, duration);
        break;
      case 3:
        score = calculateSection3Score(response as Section3Answers, duration);
        break;
      case 4:
        score = calculateSection4Score(response as TestResponse, duration);
        break;
      case 5:
        score = calculateSection5Score(response as Section5Analysis, duration);
        break;
    }

    res.json({
      success: true,
      section: sectionNum,
      score,
      completedSections: session.completedSections
    });
  } catch (error) {
    console.error('Error submitting section:', error);
    res.status(500).json({ success: false, error: 'Failed to submit section' });
  }
});

// POST /api/test/:sessionId/complete - Complete test and get final score
router.post('/:sessionId/complete', (req: Request, res: Response) => {
  try {
    const { sessionId } = req.params;

    const session = sessions.get(sessionId);
    if (!session) {
      return res.status(404).json({ success: false, error: 'Session not found' });
    }

    // Build responses and durations
    const responses: any = {};
    const durations: any = {};

    for (const section of session.completedSections) {
      responses[section] = session.responses[section];
      durations[section] = session.durations[section];
    }

    // Calculate full score
    const result = calculateFullPSCScore(responses, durations);

    session.status = 'completed';

    res.json({
      success: true,
      result,
      completedSections: session.completedSections
    });
  } catch (error) {
    console.error('Error completing test:', error);
    res.status(500).json({ success: false, error: 'Failed to complete test' });
  }
});

// GET /api/test/:sessionId/result - Get final result
router.get('/:sessionId/result', (req: Request, res: Response) => {
  try {
    const { sessionId } = req.params;

    const session = sessions.get(sessionId);
    if (!session) {
      return res.status(404).json({ success: false, error: 'Session not found' });
    }

    if (session.status !== 'completed') {
      return res.status(400).json({
        success: false,
        error: 'Test not completed yet'
      });
    }

    // Calculate final result
    const responses: any = {};
    const durations: any = {};

    for (const section of session.completedSections) {
      responses[section] = session.responses[section];
      durations[section] = session.durations[section];
    }

    const result = calculateFullPSCScore(responses, durations);

    res.json({
      success: true,
      result
    });
  } catch (error) {
    console.error('Error getting result:', error);
    res.status(500).json({ success: false, error: 'Failed to get result' });
  }
});

// GET /api/test/questions/:section - Get questions for a specific section (no session)
router.get('/questions/:section', (req: Request, res: Response) => {
  try {
    const { section } = req.params;
    const { count } = req.query;
    const sectionNum = parseInt(section) as 1 | 2 | 3 | 4 | 5;

    if (isNaN(sectionNum) || sectionNum < 1 || sectionNum > 5) {
      return res.status(400).json({ success: false, error: 'Invalid section' });
    }

    const questions = generatePartialTest(sectionNum, Date.now());

    res.json({
      success: true,
      section: sectionNum,
      questions,
      timeLimit: SECTION_CONFIG[sectionNum].timeLimit
    });
  } catch (error) {
    console.error('Error getting questions:', error);
    res.status(500).json({ success: false, error: 'Failed to get questions' });
  }
});

export default router;
