import express, { Request, Response } from 'express';
import { PutObjectCommand } from '@aws-sdk/client-s3';
import multer from 'multer';
import crypto from 'crypto';
import s3Client, { AWS_BUCKET } from '../config/s3';
import axios from 'axios';
import { optionalAuth } from '../middleware/auth';
import { addAffinityXp, xpForScore } from '../services/affinity';
import { gradeToGPA, scorePercentToGrade } from '../services/scoring/pscScoring';

const router = express.Router();

// Configure multer for memory storage (we'll upload to S3 directly)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB max
  },
});

// Extend Request to include multer file
interface MulterRequest extends Request {
  file?: {
    buffer: Buffer;
    originalname: string;
    mimetype: string;
    size: number;
  };
}

// Environment variables
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:8000';

// POST /api/audio/upload
router.post('/upload', upload.single('audio'), async (req: MulterRequest, res: Response) => {
  try {
    if (!req.file) {
      return res.status(400).json({ success: false, error: 'No audio file provided' });
    }

    // Generate unique filename
    const uniqueId = crypto.randomUUID();
    const extension = req.file.originalname.split('.').pop() || 'webm';
    const key = `audio/${uniqueId}.${extension}`;

    // Upload to S3
    const command = new PutObjectCommand({
      Bucket: AWS_BUCKET,
      Key: key,
      Body: req.file.buffer,
      ContentType: req.file.mimetype,
    });

    await s3Client.send(command);

    // Return the S3 URL
    const s3Url = `https://${AWS_BUCKET}.s3.ap-southeast-2.amazonaws.com/${key}`;

    return res.json({
      success: true,
      url: s3Url,
      key: key,
      size: req.file.size,
      contentType: req.file.mimetype,
    });
  } catch (error) {
    console.error('Upload error:', error);
    return res.status(500).json({ success: false, error: 'Failed to upload audio' });
  }
});

// POST /api/audio/analyze — optional auth: if logged in, affinity increases on success
router.post('/analyze', optionalAuth, async (req: Request, res: Response) => {
  try {
    const { audioUrl, expectedText, section } = req.body;

    if (!audioUrl) {
      return res.status(400).json({ success: false, error: 'audioUrl is required' });
    }

    console.log('=== Audio Analysis Request ===');
    console.log('Audio URL:', audioUrl);
    console.log('Expected text:', expectedText);
    console.log('Python URL:', PYTHON_SERVICE_URL);

    // Call Python service (allow up to 5 min for long recordings / slow iFlytek)
    const pythonResponse = await axios.post(`${PYTHON_SERVICE_URL}/analyze`, {
      audio_url: audioUrl,
      expected_text: expectedText || '',
      section: section || 4,
    }, {
      timeout: 300000, // 5 minute timeout
    });

    const data = pythonResponse.data;
    const isSuccess = data && (data.success !== false);

    // GPA for individual mock test: convert overall score (0–100) to grade and GPA
    const overallScoreForGpa = data?.scores?.overall ?? data?.scores?.pronunciation;
    if (typeof overallScoreForGpa === 'number' && !Number.isNaN(overallScoreForGpa)) {
      const grade = scorePercentToGrade(overallScoreForGpa);
      const gpa = gradeToGPA(grade);
      (data as Record<string, unknown>).grade = grade;
      (data as Record<string, unknown>).gpa = Math.round(gpa * 100) / 100;
    }

    // Debug: log auth and scores so we can see why XP might not be awarded
    const hasAuth = Boolean(req.headers.authorization);
    const uid = req.user?.uid;
    const scoresShape = data?.scores ? JSON.stringify(data.scores).slice(0, 120) : 'none';
    const email = req.user?.email ?? 'none';
    console.log(
      `[Affinity] analyze done. success=${isSuccess} hasAuthHeader=${hasAuth} uid=${uid ?? 'none'} email=${email} scores=${scoresShape}`
    );

    // Affinity: award XP from pronunciation score; level up when thresholds are reached
    if (isSuccess && uid) {
      const overallScore: number | undefined =
        data?.scores?.overall ?? data?.scores?.pronunciation;

      if (typeof overallScore === 'number' && !Number.isNaN(overallScore)) {
        const xpAwarded = xpForScore(overallScore);
        const state = await addAffinityXp(uid, xpAwarded);
        if (state) {
          (data as Record<string, unknown>).affinityXp = state.xp;
          (data as Record<string, unknown>).affinityLevel = state.level;
          (data as Record<string, unknown>).affinityStage = state.stage;
          (data as Record<string, unknown>).affinityXpAwarded = xpAwarded;
          (data as Record<string, unknown>).affinityXpToNext = state.xpToNext;
          (data as Record<string, unknown>).affinityXpCurrentLevel = state.xpCurrentLevel;
          (data as Record<string, unknown>).affinityXpNeededForLevel = state.xpNeededForLevel;
          console.log(
            `[Affinity] score=${overallScore} +${xpAwarded} XP -> user ${uid} (${email}) total=${state.xp} level=${state.level} (${state.stage})`
          );
        } else {
          console.log('[Affinity] addAffinityXp returned null (Firestore error?)');
        }
      } else {
        console.log(
          `[Affinity] no valid score. overallScore=${String(overallScore)} (type=${typeof data?.scores?.overall})`
        );
      }
    } else if (isSuccess && !uid) {
      console.log(
        '[Affinity] skipped: no uid. Send Authorization: Bearer <Firebase ID token> (use user.getIdToken(), not custom token)'
      );
    }

    if (!isSuccess && data && typeof data === 'object') {
      (data as Record<string, unknown>).code = 'audio_cannot_be_processed';
    }

    console.log('Python response:', JSON.stringify(data).substring(0, 200));
    return res.json(data);
  } catch (error: any) {
    console.error('=== Analysis Error ===');
    console.error('Error message:', error.message);
    console.error('Error code:', error.code);
    console.error('Response data:', error.response?.data);
    
    const analysisFailedCode = 'audio_cannot_be_processed';

    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({
        success: false,
        code: analysisFailedCode,
        error: 'Analysis service is not running. Please start the Python service.',
      });
    }

    const isTimeout =
      error.code === 'ECONNABORTED' ||
      (error.response?.data?.error && String(error.response.data.error).toLowerCase().includes('timeout'));
    if (isTimeout) {
      return res.status(504).json({
        success: false,
        code: analysisFailedCode,
        error: 'Analysis took too long. Try a shorter recording or try again.',
        dev_info: error.response?.data?.dev_info || null,
      });
    }

    return res.status(500).json({
      success: false,
      code: analysisFailedCode,
      error: error.response?.data?.error || error.message || 'Analysis failed',
      dev_info: error.response?.data?.dev_info || null,
    });
  }
});

// GET /api/audio/analysis-status/:jobId
router.get('/analysis-status/:jobId', async (req: Request, res: Response) => {
  try {
    const { jobId } = req.params;
    
    // For now, just return processing status
    // In production, this would check Redis/DB for job status
    return res.json({
      success: true,
      jobId,
      status: 'completed', // Simplified for now
    });
  } catch (error) {
    console.error('Status check error:', error);
    return res.status(500).json({ success: false, error: 'Failed to check status' });
  }
});

// Health check for audio service
router.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', service: 'audio-upload', bucket: AWS_BUCKET });
});

export default router;
