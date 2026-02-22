import express, { Request, Response } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { UserModel } from '../models/User';
import { isValidEmail, isValidPassword } from '../utils/validation';
import { authenticateToken } from '../middleware/auth';

const router = express.Router();

// POST /api/auth/register
router.post('/register', async (req: Request, res: Response) => {
  const { email, password, username } = req.body as {
    email: string; password: string; username: string;
  };

  if (!email || !password || !username) {
    return res.status(400).json({ success: false, error: 'All fields are required' });
  }
  if (!isValidEmail(email)) {
    return res.status(400).json({ success: false, error: 'Invalid email format' });
  }
  if (username.trim().length < 3) {
    return res.status(400).json({ success: false, error: 'Username must be at least 3 characters' });
  }
  const pwCheck = isValidPassword(password);
  if (!pwCheck.ok) {
    return res.status(400).json({ success: false, error: pwCheck.message });
  }

  try {
    const existing = await UserModel.findUserByEmail(email);
    if (existing) {
      return res.status(409).json({ success: false, error: 'User already exists' });
    }

    const hashed = await bcrypt.hash(password, 12);
    const newUser = await UserModel.createUser({
      email: email.toLowerCase(),
      password: hashed,
      username: username.trim(),
      isEmailVerified: false
    });

    const token = jwt.sign(
      { userId: newUser._id, email: newUser.email },
      process.env.JWT_SECRET as string,
      { expiresIn: '7d' }
    );

    const { password: _, ...safe } = newUser;
    return res.status(201).json({
      success: true,
      message: 'Account created successfully',
      user: safe,
      token
    });
  } catch (err) {
    console.error('Register error:', err);
    return res.status(500).json({ success: false, error: 'Registration failed' });
  }
});

// POST /api/auth/login
router.post('/login', async (req: Request, res: Response) => {
  const { email, password } = req.body as { email: string; password: string };

  if (!email || !password) {
    return res.status(400).json({ success: false, error: 'Email and password required' });
  }

  try {
    const user = await UserModel.findUserByEmail(email);
    if (!user || !(await bcrypt.compare(password, user.password))) {
      return res.status(401).json({ success: false, error: 'Invalid credentials' });
    }

    await UserModel.updateLastLogin(user.email);

    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET as string,
      { expiresIn: '7d' }
    );

    const { password: _, ...safe } = user;
    return res.json({ success: true, user: safe, token });
  } catch (err) {
    console.error('Login error:', err);
    return res.status(500).json({ success: false, error: 'Login failed' });
  }
});

// GET /api/auth/me
router.get('/me', authenticateToken, async (req: Request, res: Response) => {
  try {
    const user = await UserModel.findUserById(req.user!.userId);
    if (!user) return res.status(404).json({ success: false, error: 'User not found' });
    const { password: _, ...safe } = user;
    return res.json({ success: true, user: safe });
  } catch (err) {
    console.error('Get me error:', err);
    return res.status(500).json({ success: false, error: 'Failed to get user' });
  }
});

export default router;