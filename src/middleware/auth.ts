import type { Request, Response, NextFunction } from 'express';
import { auth } from '../config/firebase';

// Extend Request interface to include user
declare global {
  namespace Express {
    interface Request {
      user?: {
        uid: string;
        email?: string;
        username?: string;
      };
    }
  }
}

export const authenticateToken = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'Access token required'
      });
    }

    // Verify Firebase token
    const decodedToken = await auth.verifyIdToken(token);
    
    // Add user to request object
    req.user = {
      uid: decodedToken.uid,
      email: decodedToken.email,
      username: decodedToken.name || decodedToken.email?.split('@')[0],
    };

    next();
  } catch (error: any) {
    console.error('Auth error:', error);
    
    if (error.code === 'auth/id-token-expired') {
      return res.status(401).json({
        success: false,
        error: 'Token expired'
      });
    }
    
    if (error.code === 'auth/invalid-id-token') {
      return res.status(403).json({
        success: false,
        error: 'Invalid token'
      });
    }

    return res.status(500).json({
      success: false,
      error: 'Authentication error'
    });
  }
};

// Optional authentication (doesn't fail if no token)
export const optionalAuth = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      const decodedToken = await auth.verifyIdToken(token);
      req.user = {
        uid: decodedToken.uid,
        email: decodedToken.email,
        username: decodedToken.name || decodedToken.email?.split('@')[0],
      };
    }

    next();
  } catch {
    // Continue without authentication
    next();
  }
};
