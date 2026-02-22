import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import chatRouter from './routes/chat';
import authRouter from './routes/auth';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// ─── Middleware ───────────────────────────────────────────────
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use((req: Request, _res: Response, next: NextFunction) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  next();
});

// ─── Routes ──────────────────────────────────────────────────
app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Root route
app.get('/', (_req: Request, res: Response) => {
  res.json({
    name: 'BoDongGua API',
    version: '1.0.0',
    endpoints: {
      health:   'GET  /health',
      chat:     'POST /api/chat',
      register: 'POST /api/auth/register',
      login:    'POST /api/auth/login',
    }
  });
});

app.use('/api', chatRouter);       // POST /api/chat
app.use('/api/auth', authRouter);  // POST /api/auth/register, POST /api/auth/login

// ─── 404 — print attempted path to help debug ────────────────
app.use((req: Request, res: Response) => {
  console.warn(`⚠️  404 — no route matched: ${req.method} ${req.url}`);
  res.status(404).json({ success: false, error: `Route not found: ${req.method} ${req.url}` });
});

app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err.message);
  res.status(500).json({ success: false, error: 'Internal server error' });
});

// ─── Start ───────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🚀 Server:  http://localhost:${PORT}`);
  console.log(`📊 Health:  http://localhost:${PORT}/health`);
  console.log(`💬 Chat:    http://localhost:${PORT}/api/chat`);
  console.log(`🔐 Auth:    http://localhost:${PORT}/api/auth`);
});