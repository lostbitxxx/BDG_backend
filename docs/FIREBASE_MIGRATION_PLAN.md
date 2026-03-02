# Database Migration & Auth System Improvement Plan

**From:** MongoDB  
**To:** Firebase  
**Version:** 1.0  
**Date:** March 2, 2026

---

## Executive Summary

This document outlines the complete plan to migrate from MongoDB to Firebase, including database and authentication system improvements.

---

## 1. Why Firebase?

### Comparison with MongoDB

| Criteria | MongoDB | Firebase |
|----------|---------|----------|
| Setup | Complex | Easy (5 min) |
| Auth | Manual | Built-in |
| Free Tier | 512MB | 1GB (Auth: Unlimited) |
| Maintenance | Yes | No (Google managed) |
| Database | NoSQL | NoSQL (Firestore) |
| Real-time | Extra setup | Built-in |

### Firebase Advantages
- **Built-in Authentication** - No need to implement JWT, sessions, password reset
- **Google Cloud** - Reliable, scalable infrastructure
- **Free Tier** - Generous limits for small apps
- **Easy Setup** - Can be done in 5 minutes
- **Real-time** - Built-in real-time listeners
- **Security** - Firebase Auth + Firestore Security Rules

---

## 2. Current Problems

### 2.1 MongoDB Issues
- Complex setup for developers
- Authentication errors common
- Free tier pauses after inactivity
- Requires MongoDB Atlas account
- Connection string format issues

### 2.2 Auth System Issues
- JWT stored in localStorage (security risk)
- No token refresh mechanism
- No proper session management
- Password reset not implemented
- No email verification
- No OAuth support
- Manual user management

---

## 3. Architecture Comparison

### Current Architecture (MongoDB)
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│                  http://localhost:3000                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend (Node.js)                           │
│                  localhost:3001                              │
│  - JWT handling                                            │
│  - MongoDB connection                                      │
│  - Manual auth logic                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   MongoDB Atlas                              │
│  - User collections                                        │
│  - Complex setup                                           │
└─────────────────────────────────────────────────────────────┘
```

### New Architecture (Firebase)
```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│                  http://localhost:3000                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend (Node.js)                           │
│                  localhost:3001                              │
│  - Firebase Admin SDK (optional)                           │
│  - Verify tokens only                                      │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌───────────────────┴───────────────────┐
            ▼                                       ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│     Firebase Auth        │     │    Firebase Firestore     │
│  - Email/Password       │     │  - User profiles         │
│  - Google OAuth         │     │  - App data              │
│  - GitHub OAuth         │     │  - Real-time sync        │
│  - Token management     │     │  - Offline support       │
└───────────────────────────┘     └───────────────────────────┘
```

---

## 4. Migration Phases

### Phase 1: Firebase Setup (1 hour)

**Task 1.1: Create Firebase Project**
1. Go to console.firebase.google.com
2. Create new project "BoDongGua"
3. Enable Authentication
4. Enable Firestore Database

**Task 1.2: Configure Authentication**
1. Sign-in Method: Email/Password
2. Enable Email/Password
3. Enable Google (optional)
4. Enable GitHub (optional)

**Task 1.3: Configure Firestore**
1. Create database (test mode for dev)
2. Set security rules
3. Note configuration

---

### Phase 2: Backend Changes (2 hours)

**Task 2.1: Install Firebase Admin**
```bash
npm install firebase-admin
```

**Task 2.2: Create Firebase Config**
```typescript
// src/config/firebase.ts
import admin from 'firebase-admin';

const serviceAccount = JSON.parse(
  process.env.FIREBASE_SERVICE_ACCOUNT || '{}'
);

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount)
  });
}

export const auth = admin.auth();
export const db = admin.firestore();
```

**Task 2.3: Update Auth Routes**
```typescript
// New auth flow
POST /api/auth/signup
  → Firebase Auth: createUserWithEmailAndPassword
  → Firestore: create user profile
  → Return: { user, token }

POST /api/auth/signin
  → Firebase Auth: signInWithEmailAndPassword
  → Return: { user, token }

POST /api/auth/signout
  → Firebase Auth: signOut
  → Return: { success }

GET /api/auth/verify
  → Firebase Admin: verifyIdToken
  → Return: { user }
```

**Task 2.4: Remove MongoDB**
- Delete MongoDB connection code
- Remove MONGODB_URI from .env

---

### Phase 3: Frontend Changes (3 hours)

**Task 3.1: Install Firebase Client**
```bash
npm install firebase
```

**Task 3.2: Create Firebase Config**
```typescript
// src/lib/firebase.ts
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  // ...
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
```

**Task 3.3: Update Auth Context**
```typescript
// New Auth Context using Firebase Auth
- Sign up with email/password
- Sign in with email/password
- Sign in with Google (optional)
- Sign out
- Password reset
- Email verification
- Auto-refresh token handling
```

**Task 3.4: Update Pages**
- SignIn.tsx - Use Firebase Auth
- SignUp.tsx - Use Firebase Auth
- Profile page - Use Firestore

---

### Phase 4: Data Migration (1 hour)

**Task 4.1: Export MongoDB Data**
```javascript
// Export users from MongoDB
db.users.find().forEach(doc => {
  printjson(doc);
});
```

**Task 4.2: Import to Firebase**
```typescript
// Import users to Firebase Auth
// Note: Cannot import passwords directly
// Users need to reset password
```

**Task 4.3: Migrate Other Data**
- Export from MongoDB
- Import to Firestore

---

### Phase 5: Testing (2 hours)

**Task 5.1: Test Auth Flow**
- Sign up
- Sign in
- Sign out
- Password reset
- Email verification (optional)

**Task 5.2: Test Data Flow**
- CRUD operations
- Real-time updates
- Offline support

**Task 5.3: Security Testing**
- Firestore rules
- Auth validation

---

## 5. Auth System Improvements

### New Features

| Feature | Status | Description |
|---------|--------|-------------|
| Email/Password | ✅ | Basic login |
| Google OAuth | ✅ (Optional) | One-click login |
| GitHub OAuth | ✅ (Optional) | One-click login |
| Password Reset | ✅ | Email-based reset |
| Email Verification | ✅ | Verify email before login |
| Token Refresh | ✅ | Auto-refresh handled by Firebase |
| Session Management | ✅ | Multiple device logout |
| Rate Limiting | ✅ | Built-in Firebase protection |

### Security Comparison

| Aspect | Current | New |
|--------|---------|-----|
| Token Storage | localStorage | httpOnly (via Firebase) |
| Token Refresh | Manual | Auto (Firebase SDK) |
| Password Storage | Hash manually | Firebase manages |
| Session | Single device | Multi-device |
| Brute Force | None | Built-in protection |

---

## 6. Firebase Configuration

### Environment Variables

**Backend (.env)**
```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@xxx.iam.gserviceaccount.com
```

**Frontend (.env)**
```
REACT_APP_FIREBASE_API_KEY=xxx
REACT_APP_FIREBASE_AUTH_DOMAIN=xxx.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=xxx
REACT_APP_FIREBASE_STORAGE_BUCKET=xxx.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=xxx
REACT_APP_FIREBASE_APP_ID=xxx
```

---

## 7. File Changes

### Backend

| File | Action |
|------|--------|
| `src/config/firebase.ts` | Create |
| `src/config/database.ts` | Delete |
| `src/models/User.ts` | Delete |
| `src/routes/auth.ts` | Rewrite |
| `src/middleware/auth.ts` | Simplify |
| `.env.example` | Update |

### Frontend

| File | Action |
|------|--------|
| `src/lib/firebase.ts` | Create |
| `src/context/AuthContext.tsx` | Rewrite |
| `src/pages/SignIn.tsx` | Rewrite |
| `src/pages/SignUp.tsx` | Rewrite |
| `.env.example` | Update |

---

## 8. Timeline

| Phase | Task | Duration |
|-------|------|-----------|
| 1 | Firebase Setup | 1 hour |
| 2 | Backend Changes | 2 hours |
| 3 | Frontend Changes | 3 hours |
| 4 | Data Migration | 1 hour |
| 5 | Testing | 2 hours |

**Total: 9 hours**

---

## 9. Cost Comparison

### MongoDB Atlas
- Free Tier: $0/month
- Shared tier: ~$10/month

### Firebase
- Authentication: Free (unlimited)
- Firestore: 1GB free
- Total: $0/month (for typical usage)

---

## 10. Rollback Plan

If migration fails:
1. Keep MongoDB Atlas for 30 days
2. Revert backend changes
3. Update .env to use MongoDB again

---

## 11. Questions Before Starting

1. Should we keep existing user data?
   - Options: Migrate / Start fresh / Manual migration

2. Which OAuth providers?
   - Google: Easy to implement
   - GitHub: Requires GitHub OAuth app

3. Email verification required?
   - Yes: Add verification step
   - No: Skip for faster launch

4. Timeline?
   - ASAP / Flexible

---

## Summary

Migrating to Firebase provides:
- **Simpler setup** - 5 minutes vs hours
- **Built-in auth** - No JWT management needed
- **Better security** - Google-level security
- **Cost savings** - Generous free tier
- **Less maintenance** - Google managed

The entire migration can be completed in **9 hours**.

---

**Document Ready for Approval**
