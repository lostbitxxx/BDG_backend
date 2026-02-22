// Centralised validation helpers used across routes

export const isValidEmail = (email: string): boolean =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

export const isValidPassword = (password: string): { ok: boolean; message?: string } => {
  if (password.length < 6) {
    return { ok: false, message: 'Password must be at least 6 characters' };
  }
  if (!/(?=.*[a-z])(?=.*[A-Z])/.test(password)) {
    return { ok: false, message: 'Password must contain uppercase and lowercase letters' };
  }
  return { ok: true };
};

export const isNonEmptyString = (value: unknown): value is string =>
  typeof value === 'string' && value.trim().length > 0;