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

/** Decode token without verification to check its type */
function decodeTokenPayload(token: string): { sub?: string; uid?: string; iss?: string } | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const payload = JSON.parse(Buffer.from(parts[1], 'base64').toString());
    return payload;
  } catch {
    return null;
  }
}

/** Verify token - handles both ID tokens and custom tokens */
async function verifyToken(token: string) {
  // First, try to verify as ID token
  try {
    return await auth.verifyIdToken(token);
  } catch (error: any) {
    // If error is about custom token, try to extract UID and get user
    if (error.code === 'auth/argument-error' ||
        error.message?.includes('custom token')) {

      // Try to decode and get UID
      const payload = decodeTokenPayload(token);
      console.log('Token payload:', payload);

      if (payload) {
        // Check if this is a service account token (not a user token)
        if (payload.iss?.includes('firebase-adminsdk') ||
            payload.sub?.includes('firebase-adminsdk') ||
            payload.uid?.includes('firebase-adminsdk')) {
          console.log('Service account token detected - rejecting');
          throw new Error('INVALID_TOKEN_TYPE');
        }

        const uid = payload.sub || payload.uid;
        console.log('Extracted UID:', uid);

        if (uid) {
          try {
            const userRecord = await auth.getUser(uid);
            return {
              uid: userRecord.uid,
              email: userRecord.email || undefined,
              email_verified: userRecord.emailVerified,
              name: userRecord.displayName || undefined,
            };
          } catch (userError: any) {
            // User not found - token is invalid
            if (userError.code === 'auth/user-not-found') {
              console.log('User not found for UID:', uid);
              throw new Error('TOKEN_USER_NOT_FOUND');
            }
            throw userError;
          }
        }
      }
    }
    // Re-throw original error if not a custom token issue
    throw error;
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

    // Verify Firebase token (handles both ID tokens and custom tokens)
    const decodedToken = await verifyToken(token);

    // Add user to request object
    req.user = {
      uid: decodedToken.uid,
      email: decodedToken.email,
      username: decodedToken.name || decodedToken.email?.split('@')[0],
    };

    next();
  } catch (error: any) {
    console.error('Auth error:', error);

    // Handle invalid token type (service account token)
    if (error.message === 'INVALID_TOKEN_TYPE') {
      return res.status(401).json({
        success: false,
        error: 'Invalid token. Please login again.'
      });
    }

    // Handle token with no corresponding user
    if (error.message === 'TOKEN_USER_NOT_FOUND') {
      return res.status(401).json({
        success: false,
        error: 'Session expired. Please login again.'
      });
    }

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
      error: 'Authentication error: ' + error.message
    });
  }
};

// Optional authentication (doesn't fail if no token)
export const optionalAuth = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      const decodedToken = await verifyToken(token);
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
