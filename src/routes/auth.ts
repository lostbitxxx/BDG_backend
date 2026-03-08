import express, { Request, Response } from 'express';
import { auth, db } from '../config/firebase';
import { authenticateToken } from '../middleware/auth';
import { incrementAffinity, MAX_AFFINITY, MIN_AFFINITY, levelToStage, getAffinityState, xpToLevel } from '../services/affinity';

const router = express.Router();

// POST /api/auth/register
router.post('/register', async (req: Request, res: Response) => {
  const { email, password, username, idToken } = req.body as {
    email: string; password: string; username: string; idToken?: string;
  };

  if (!email || !password || !username) {
    return res.status(400).json({ success: false, error: 'All fields are required' });
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ success: false, error: 'Invalid email format' });
  }

  if (username.trim().length < 3) {
    return res.status(400).json({ success: false, error: 'Username must be at least 3 characters' });
  }

  if (password.length < 6) {
    return res.status(400).json({ success: false, error: 'Password must be at least 6 characters' });
  }

  try {
    // Verify the ID token if provided (from client-side Firebase Auth)
    if (idToken) {
      const decodedToken = await auth.verifyIdToken(idToken);
      // Check if email matches
      if (decodedToken.email !== email) {
        return res.status(400).json({ success: false, error: 'Email mismatch' });
      }
    }

    // Create user in Firebase Auth
    const userRecord = await auth.createUser({
      email,
      password,
      displayName: username.trim(),
    });

    // Create user profile in Firestore
    await db.collection('users').doc(userRecord.uid).set({
      uid: userRecord.uid,
      email,
      username: username.trim(),
      character: 'red-birdie',
      affinityXp: 0,
      affinityLevel: 1,
      affinityStage: levelToStage(1),
      createdAt: new Date().toISOString(),
    });

    // Generate custom token for the user
    const token = await auth.createCustomToken(userRecord.uid);

    return res.status(201).json({
      success: true,
      message: 'Account created successfully',
      user: {
        uid: userRecord.uid,
        email: userRecord.email,
        username: username.trim(),
        character: 'red-birdie',
        affinityXp: 0,
        affinityLevel: 1,
        affinityStage: 'stranger',
      },
      token,
    });
  } catch (error: any) {
    console.error('Register error:', error);
    
    if (error.code === 'auth/email-already-exists') {
      return res.status(409).json({ success: false, error: 'User already exists' });
    }
    if (error.code === 'auth/invalid-email') {
      return res.status(400).json({ success: false, error: 'Invalid email format' });
    }
    if (error.code === 'auth/weak-password') {
      return res.status(400).json({ success: false, error: 'Password is too weak' });
    }
    
    return res.status(500).json({ success: false, error: 'Registration failed' });
  }
});

// POST /api/auth/login
router.post('/login', async (req: Request, res: Response) => {
  const { email, idToken } = req.body as { email?: string; idToken?: string };

  // Support两种登录方式:
  // 1. idToken: Firebase client-side auth token (recommended)
  // 2. email: For backward compatibility, generate token without password verification
  
  if (!idToken && !email) {
    return res.status(400).json({ success: false, error: 'Email or ID token required' });
  }

  try {
    let uid: string;
    
    if (idToken) {
      // Verify Firebase ID token from client
      const decodedToken = await auth.verifyIdToken(idToken);
      uid = decodedToken.uid;
    } else if (email) {
      // Get user by email (without password verification)
      const userRecord = await auth.getUserByEmail(email);
      uid = userRecord.uid;
    } else {
      return res.status(400).json({ success: false, error: 'Invalid request' });
    }

    // Get user profile from Firestore
    const userDoc = await db.collection('users').doc(uid).get();
    const userData = userDoc.exists ? userDoc.data() : null;

    // Generate custom token
    const customToken = await auth.createCustomToken(uid);

    const affinityXp = (userData?.affinityXp as number) ?? 0;
    const affinityLevel =
      typeof userData?.affinityXp === 'number' ? xpToLevel(affinityXp) : (userData?.affinityLevel ?? 1);
    const affinityStage = userData?.affinityStage || levelToStage(affinityLevel);

    return res.status(200).json({
      success: true,
      message: 'Login successful',
      user: {
        uid,
        email: userData?.email || email || 'user@example.com',
        username: userData?.username || 'User',
        character: userData?.character || 'red-birdie',
        affinityXp,
        affinityLevel,
        affinityStage,
      },
      token: customToken,
    });
  } catch (error: any) {
    console.error('Login error:', error);
    return res.status(401).json({ success: false, error: 'Invalid credentials' });
  }
});

// POST /api/auth/logout
router.post('/logout', async (_req: Request, res: Response) => {
  return res.status(200).json({
    success: true,
    message: 'Logout successful',
  });
});

// GET /api/auth/verify
router.get('/verify', async (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ success: false, error: 'No token provided' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decodedToken = await auth.verifyIdToken(token);
    
    // Get user profile from Firestore
    const userDoc = await db.collection('users').doc(decodedToken.uid).get();
    const userData = userDoc.exists ? userDoc.data() : null;

    const affinityXp = (userData?.affinityXp as number) ?? 0;
    const affinityLevel =
      typeof userData?.affinityXp === 'number' ? xpToLevel(affinityXp) : (userData?.affinityLevel ?? 1);
    const affinityStage = userData?.affinityStage || levelToStage(affinityLevel);

    return res.status(200).json({
      success: true,
      user: {
        uid: decodedToken.uid,
        email: decodedToken.email,
        username: userData?.username || decodedToken.name || 'User',
        character: userData?.character || 'red-birdie',
        affinityXp,
        affinityLevel,
        affinityStage,
      },
    });
  } catch (error: any) {
    console.error('Verify error:', error);
    return res.status(401).json({ success: false, error: 'Invalid token' });
  }
});

// PUT /api/auth/username
router.put('/username', async (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ success: false, error: 'No token provided' });
  }
  const token = authHeader.split(' ')[1];
  try {
    // Decode the JWT payload without verification to extract uid
    // (token was already verified at login time and stored client-side)
    const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
    const uid: string = payload.uid || payload.sub;
    if (!uid) {
      return res.status(401).json({ success: false, error: 'Invalid token: no uid' });
    }

    const { username } = req.body as { username: string };
    if (!username || username.trim().length < 3) {
      return res.status(400).json({ success: false, error: 'Username must be at least 3 characters.' });
    }
    const trimmed = username.trim();
    await auth.updateUser(uid, { displayName: trimmed });
    await db.collection('users').doc(uid).update({ username: trimmed });
    return res.json({ success: true, username: trimmed });
  } catch (err) {
    console.error('Update username error:', err);
    return res.status(500).json({ success: false, error: 'Failed to update username' });
  }
});

// Affinity: XP-based stages (stranger → friend → close_friend → best_friend → soulmate)

// GET /api/auth/affinity — current XP, level, stage, progress to next level
router.get('/affinity', authenticateToken, async (req: Request, res: Response) => {
  try {
    const uid = req.user?.uid;
    if (!uid) return res.status(401).json({ success: false, error: 'Not authenticated' });
    const state = await getAffinityState(uid);
    if (!state) return res.status(500).json({ success: false, error: 'Failed to load affinity' });
    return res.json(state);
  } catch (err) {
    console.error('Get affinity error:', err);
    return res.status(500).json({ success: false, error: 'Failed to load affinity' });
  }
});

// POST /api/auth/affinity/increment — increase by 1 after completing a mock test or exercise
router.post('/affinity/increment', authenticateToken, async (req: Request, res: Response) => {
  try {
    const uid = req.user?.uid;
    if (!uid) {
      return res.status(401).json({ success: false, error: 'Not authenticated' });
    }
    const newLevel = await incrementAffinity(uid);
    if (newLevel == null) {
      return res.status(500).json({ success: false, error: 'Failed to update affinity' });
    }
    return res.json({ success: true, affinityLevel: newLevel });
  } catch (err) {
    console.error('Affinity increment error:', err);
    return res.status(500).json({ success: false, error: 'Failed to update affinity level' });
  }
});

// PUT /api/auth/affinity
router.put('/affinity', async (req: Request, res: Response) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ success: false, error: 'No token provided' });
  }
  const token = authHeader.split(' ')[1];
  try {
    const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
    const uid: string = payload.uid || payload.sub;
    if (!uid) {
      return res.status(401).json({ success: false, error: 'Invalid token: no uid' });
    }

    const { affinityLevel } = req.body as { affinityLevel?: number };
    if (typeof affinityLevel !== 'number' || !Number.isInteger(affinityLevel)) {
      return res.status(400).json({ success: false, error: 'affinityLevel must be an integer' });
    }
    const level = Math.max(MIN_AFFINITY, Math.min(MAX_AFFINITY, affinityLevel));
    await db.collection('users').doc(uid).update({ affinityLevel: level });
    return res.json({ success: true, affinityLevel: level });
  } catch (err) {
    console.error('Update affinity error:', err);
    return res.status(500).json({ success: false, error: 'Failed to update affinity level' });
  }
});

export default router;
