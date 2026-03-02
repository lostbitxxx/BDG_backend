# Database Migration & Auth System Improvement Plan

**Version:** 1.0  
**Date:** March 2, 2026  
**Status:** Planning

---

## 1. Executive Summary

This plan outlines the migration from MongoDB to a simpler database service and the optimization of the authentication system.

### Goals
1. Replace MongoDB with a more developer-friendly database
2. Implement robust authentication system
3. Reduce onboarding friction for new developers

---

## 2. Current Problems

### 2.1 MongoDB Issues
- Complex setup for developers
- Authentication errors common
- Free tier pauses after inactivity
- Requires MongoDB Atlas account
- Connection string format errors

### 2.2 Auth System Issues
- JWT stored in localStorage (security risk)
- No token refresh mechanism
- No proper session management
- Password reset not implemented
- No email verification
- No OAuth support

---

## 3. Recommended Solution

### 3.1 Database: Supabase (Recommended)

| Criteria | Assessment |
|----------|------------|
| Free Tier | 500MB storage, generous limits |
| Setup Time | 15 minutes |
| Auth | Built-in JWT authentication |
| Database | PostgreSQL (full SQL) |
| Security | Row Level Security (RLS) |

**Alternative Options:**
- Firebase (Google-only, no SQL)
- PostgreSQL on Railway/Render (more setup required)

### 3.2 Auth Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Current Flow (Insecure)                     │
├─────────────────────────────────────────────────────────────────┤
│  User → Login → Backend → MongoDB → JWT → localStorage        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Improved Flow (Secure)                       │
├─────────────────────────────────────────────────────────────────┤
│  User → Login → Supabase Auth → Session                       │
│                        ↓                                       │
│              Access Token (15 min)                             │
│              Refresh Token (7 days)                            │
│                        ↓                                       │
│              Stored in httpOnly Cookie                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Phases

### Phase 1: Database Setup (Week 1)

**Task 4.1.1: Create Supabase Project**
- Sign up at supabase.com
- Create new project
- Note: URL, anon key, service role key

**Task 4.1.2: Database Schema**
```sql
-- Users managed by Supabase Auth

-- Profiles table
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own profile"
  ON profiles FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON profiles FOR UPDATE
  USING (auth.uid() = id);
```

**Task 4.1.3: Environment Variables**
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=xxx
SUPABASE_SERVICE_ROLE_KEY=xxx
```

---

### Phase 2: Backend Changes (Week 1-2)

**Task 4.2.1: Install Dependencies**
```bash
npm install @supabase/supabase-js
```

**Task 4.2.2: Create Supabase Client**
```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.SUPABASE_URL!;
const supabaseKey = process.env.SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseKey);
```

**Task 4.2.3: Update Auth Routes**
- Remove MongoDB user model
- Add Supabase auth integration
- Implement token refresh
- Add rate limiting

**Task 4.2.4: Remove MongoDB**
- Delete MongoDB connection code
- Update .env remove MONGODB_URI

---

### Phase 3: Frontend Changes (Week 2)

**Task 4.3.1: Update Auth Context**
```typescript
// Replace localStorage with cookies
// Implement token refresh logic
// Add session management
```

**Task 4.3.2: Update Login/Signup Pages**
- Use Supabase auth methods
- Add "Remember Me" checkbox
- Add password strength indicator

**Task 4.3.3: Add Password Reset**
- Forgot password page
- Reset email flow

---

### Phase 4: Testing & Deployment (Week 2)

**Task 4.4.1: Testing**
- Unit tests for auth
- Integration tests
- Security testing

**Task 4.4.2: Documentation**
- Update .env.example
- Update setup instructions

---

## 5. Auth System Features

### 5.1 Required Features
| Feature | Priority | Description |
|---------|----------|-------------|
| Sign Up | Required | Email/password registration |
| Sign In | Required | Email/password login |
| Sign Out | Required | Clear session |
| Protected Routes | Required | Middleware for auth |
| Token Refresh | Required | Auto-refresh tokens |

### 5.2 Enhanced Features
| Feature | Priority | Description |
|---------|----------|-------------|
| Remember Me | Optional | Extended session (30 days) |
| Password Reset | Optional | Email-based reset |
| Email Verify | Optional | Verify email before login |
| OAuth | Optional | Google/GitHub login |

---

## 6. Security Improvements

### Current Issues
- JWT in localStorage (XSS vulnerable)
- No token rotation
- No session timeout
- No brute force protection

### Proposed Solutions
| Issue | Solution |
|-------|----------|
| XSS | httpOnly cookies |
| Token theft | Short-lived access tokens |
| Sessions | Server-side session management |
| Brute force | Rate limiting + captcha |

---

## 7. File Changes Summary

### Backend Files
| File | Action |
|------|--------|
| `src/lib/supabase.ts` | Create |
| `src/routes/auth.ts` | Modify |
| `src/models/User.ts` | Delete |
| `.env.example` | Update |

### Frontend Files
| File | Action |
|------|--------|
| `src/context/AuthContext.tsx` | Modify |
| `src/pages/SignIn.tsx` | Modify |
| `src/pages/SignUp.tsx` | Modify |
| `.env.example` | Update |

---

## 8. Timeline

| Phase | Tasks | Duration |
|-------|-------|----------|
| 1 | Supabase setup + schema | 2 hours |
| 2 | Backend integration | 4 hours |
| 3 | Frontend integration | 4 hours |
| 4 | Testing + documentation | 2 hours |

**Total Estimated Time: 12 hours**

---

## 9. Questions Before Implementation

1. **Database Choice:** Supabase / Firebase / PostgreSQL?
2. **User Data:** Keep existing or start fresh?
3. **OAuth:** Include Google/GitHub login?
4. **Timeline:** Any deadline?

---

## 10. Approval Required

- [ ] Approve database migration plan
- [ ] Approve auth improvements
- [ ] Confirm Supabase as provider
- [ ] Set budget (if any)

---

**End of Planning Document**
