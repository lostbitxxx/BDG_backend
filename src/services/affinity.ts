import { db } from '../config/firebase';

export const MIN_AFFINITY = 1;
export const MAX_AFFINITY = 5;

export type AffinityStage =
  | 'stranger'
  | 'friend'
  | 'close_friend'
  | 'best_friend'
  | 'soulmate';

/** XP required (total) to reach each level. Level 1 = 0, Level 2 = XP_LEVELS[1], etc. */
export const XP_LEVELS: number[] = [0, 100, 300, 600, 1000];

export function levelToStage(level: number): AffinityStage {
  if (level >= 5) return 'soulmate';
  if (level === 4) return 'best_friend';
  if (level === 3) return 'close_friend';
  if (level === 2) return 'friend';
  return 'stranger';
}

/**
 * Compute level (1–5) from total XP.
 */
export function xpToLevel(xp: number): number {
  let level = MIN_AFFINITY;
  for (let i = XP_LEVELS.length - 1; i >= 0; i--) {
    if (xp >= XP_LEVELS[i]) {
      level = i + 1;
      break;
    }
  }
  return Math.min(level, MAX_AFFINITY);
}

/**
 * XP required to reach the next level from current total XP.
 * Returns 0 if already max level.
 */
export function xpToNextLevel(currentXp: number): number | null {
  const level = xpToLevel(currentXp);
  if (level >= MAX_AFFINITY) return null;
  return XP_LEVELS[level] - currentXp;
}

/**
 * Total XP threshold for the next level (for progress bar).
 */
export function xpThresholdForLevel(level: number): number {
  if (level < 1 || level > MAX_AFFINITY) return XP_LEVELS[MAX_AFFINITY - 1];
  return XP_LEVELS[level - 1];
}

/**
 * Award XP for a pronunciation score (0–100). Better score = more XP.
 */
export function xpForScore(score: number): number {
  if (Number.isNaN(score) || score < 0) return 0;
  const clamped = Math.min(100, Math.max(0, score));
  if (clamped < 60) return 5;
  if (clamped < 70) return 10;
  if (clamped < 80) return 15;
  if (clamped < 90) return 25;
  if (clamped < 95) return 35;
  return 50;
}

export interface AffinityState {
  xp: number;
  level: number;
  stage: AffinityStage;
  xpToNext: number | null;
  xpCurrentLevel: number; // XP into current level (for progress bar)
  xpNeededForLevel: number; // XP needed total for current level
}

/**
 * Add XP and level up if thresholds are crossed.
 * Returns new affinity state or null on error.
 */
export async function addAffinityXp(
  uid: string,
  xpAmount: number
): Promise<AffinityState | null> {
  if (!uid || !db.collection || xpAmount <= 0) return null;
  try {
    const ref = db.collection('users').doc(uid);
    const doc = await ref.get();
    const data = doc.exists ? doc.data() || {} : {};
    let currentXp: number = (data.affinityXp as number) ?? 0;
    // Migrate: if user has old affinityLevel but no affinityXp, set XP to that level's floor
    if (currentXp === 0 && typeof data.affinityLevel === 'number' && data.affinityLevel > 1) {
      currentXp = XP_LEVELS[Math.min(data.affinityLevel - 1, XP_LEVELS.length - 1)] ?? 0;
    }
    const newXp = currentXp + xpAmount;
    const newLevel = xpToLevel(newXp);
    const stage = levelToStage(newLevel);

    await ref.set(
      {
        affinityXp: newXp,
        affinityLevel: newLevel,
        affinityStage: stage,
      },
      { merge: true }
    );

    const xpPrevThreshold = newLevel > 1 ? XP_LEVELS[newLevel - 2] : 0;
    const xpCurrentLevel = newXp - xpPrevThreshold;
    const xpToNext = xpToNextLevel(newXp);
    const xpNeededForLevel =
      newLevel >= MAX_AFFINITY ? 0 : XP_LEVELS[newLevel] - XP_LEVELS[newLevel - 1];

    return {
      xp: newXp,
      level: newLevel,
      stage,
      xpToNext: xpToNext ?? 0,
      xpCurrentLevel,
      xpNeededForLevel,
    };
  } catch (err) {
    console.error('addAffinityXp error:', err);
    return null;
  }
}

/**
 * Get current affinity state for a user (for display).
 */
export async function getAffinityState(uid: string): Promise<AffinityState | null> {
  if (!uid || !db.collection) return null;
  try {
    const doc = await db.collection('users').doc(uid).get();
    const data = doc.exists ? doc.data() || {} : {};
    const xp: number = (data.affinityXp as number) ?? 0;
    const level = xpToLevel(xp);
    const stage = levelToStage(level);
    const xpToNext = xpToNextLevel(xp);
    const xpPrevThreshold = level > 1 ? XP_LEVELS[level - 2] : 0;
    const xpCurrentLevel = xp - xpPrevThreshold;
    const xpNeededForLevel =
      level >= MAX_AFFINITY ? 0 : XP_LEVELS[level] - XP_LEVELS[level - 1];

    return {
      xp,
      level,
      stage,
      xpToNext: xpToNext ?? 0,
      xpCurrentLevel,
      xpNeededForLevel,
    };
  } catch (err) {
    console.error('getAffinityState error:', err);
    return null;
  }
}

/**
 * Legacy: increment level by 1 (for POST /api/auth/affinity/increment).
 * Now adds a fixed XP amount so level-up is still threshold-based.
 */
export async function incrementAffinity(uid: string): Promise<number | null> {
  const state = await addAffinityXp(uid, 25);
  return state ? state.level : null;
}
