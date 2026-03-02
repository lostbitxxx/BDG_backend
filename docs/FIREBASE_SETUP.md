# Firebase Migration Complete

## Changes Made

### Backend
1. **Firebase Admin SDK** - Added `src/config/firebase.ts`
2. **Auth Routes** - Updated `src/routes/auth.ts` to use Firebase Auth
3. **Middleware** - Updated `src/middleware/auth.ts` to verify Firebase tokens
4. **Environment** - Updated `.env.example` with Firebase config

### Frontend
1. **Firebase Client** - Added `src/lib/firebase.ts`

---

## Setup Required

### Step 1: Create Firebase Project
1. Go to https://console.firebase.google.com
2. Create new project "BoDongGua"
3. Enable Authentication:
   - Sign-in Method: Email/Password
   - Enable "Email/Password"
4. Enable Firestore:
   - Create database (start in Test Mode)

### Step 2: Get Firebase Config

**From Firebase Console → Project Settings → General:**

```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@your-project.iam.gserviceaccount.com
```

**Download Service Account Key:**
1. Project Settings → Service Accounts
2. Generate new private key
3. Copy the JSON content

### Step 3: Configure Backend .env

```
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYourPrivateKey\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk@xxx.iam.gserviceaccount.com
```

### Step 4: Configure Frontend .env

```
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=123456789
REACT_APP_FIREBASE_APP_ID=1:123456789:web:abcdef
```

---

## Starting the App

### Backend
```bash
cd BDG_backend
npm install firebase-admin
npm run dev
```

### Frontend
```bash
cd BDG_frontend
npm install firebase
npm start
```

---

## Testing

1. Register a new user
2. Login with email/password
3. Verify user appears in Firebase Console → Authentication
4. Verify profile created in Firebase Console → Firestore

---

## Notes

- User data is stored in Firestore `users` collection
- Password is managed by Firebase Auth (not stored in our database)
- All authentication is handled by Firebase
