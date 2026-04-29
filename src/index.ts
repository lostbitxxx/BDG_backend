import express, { Request, Response, NextFunction } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { createServer } from 'http';
import { Server } from 'socket.io';
import chatRouter from './routes/chat';
import authRouter from './routes/auth';
import audioRouter from './routes/audio';
import questionsRouter from './routes/questions';
import testRouter from './routes/test';
import { setupSocketIO } from './services/socketHandler';

dotenv.config();

const app = express();
const httpServer = createServer(app);

const corsOptions = {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
};

// Socket.IO setup
const io = new Server(httpServer, {
  cors: corsOptions
});

const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors(corsOptions)); 

// Body parser - skip for multipart to let multer handle it
app.use((req, res, next) => {
  const ct = req.headers['content-type'] || '';
  if (ct.includes('multipart/form-data')) {
    next();
  } else {
    express.json({ limit: '50mb' })(req, res, next);
  }
});

// Setup Socket.IO
setupSocketIO(httpServer);

// Routes
app.use('/api/auth', authRouter);
app.use('/api/audio', audioRouter);
app.use('/api/questions', questionsRouter);
app.use('/api/test', testRouter);
app.use('/api', chatRouter);

// Health check
app.get('/health', (_req: Request, res: Response) => {
  res.json({ 
    status: 'ok', 
    service: 'bdg-backend',
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
httpServer.listen(PORT, () => {
  console.log(`🚀 Server: http://localhost:${PORT}`);
  console.log(`📊 Health: http://localhost:${PORT}/health`);
  console.log(`💬 Chat: http://localhost:${PORT}/api/chat`);
  console.log(`🔐 Auth: http://localhost:${PORT}/api/auth`);
  console.log(`🎤 Audio: http://localhost:${PORT}/api/audio`);
});

export default app;
