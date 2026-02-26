import express, { Request, Response } from 'express';
import { PutObjectCommand } from '@aws-sdk/client-s3';
import multer from 'multer';
import crypto from 'crypto';
import s3Client, { AWS_BUCKET } from '../config/s3';
import axios from 'axios';

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
const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:9401';

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

// POST /api/audio/analyze
router.post('/analyze', async (req: Request, res: Response) => {
  try {
    const { audioUrl, expectedText, section } = req.body;

    if (!audioUrl) {
      return res.status(400).json({ success: false, error: 'audioUrl is required' });
    }

    console.log('Analyzing audio:', audioUrl);
    console.log('Expected text:', expectedText);

    // Call Python service
    const pythonResponse = await axios.post(`${PYTHON_SERVICE_URL}/analyze`, {
      audio_url: audioUrl,
      expected_text: expectedText || '',
      section: section || 4,
    }, {
      timeout: 120000, // 2 minute timeout
    });

    return res.json(pythonResponse.data);
  } catch (error: any) {
    console.error('Analysis error:', error.message);
    
    if (error.code === 'ECONNREFUSED') {
      return res.status(503).json({ 
        success: false, 
        error: 'Analysis service is not running. Please start the Python service.' 
      });
    }
    
    return res.status(500).json({ 
      success: false, 
      error: error.response?.data?.error || error.message || 'Analysis failed' 
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
