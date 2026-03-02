import admin from 'firebase-admin';

// Check if Firebase is configured
const isFirebaseConfigured = () => {
  return !!(
    process.env.FIREBASE_PROJECT_ID &&
    process.env.FIREBASE_PRIVATE_KEY &&
    process.env.FIREBASE_CLIENT_EMAIL
  );
};

// Initialize Firebase Admin only if configured
let auth: admin.auth.Auth;
let db: admin.firestore.Firestore;

if (isFirebaseConfigured()) {
  try {
    const serviceAccount = {
      type: 'service_account',
      project_id: process.env.FIREBASE_PROJECT_ID,
      private_key: process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
      client_email: process.env.FIREBASE_CLIENT_EMAIL,
    };

    admin.initializeApp({
      credential: admin.credential.cert(serviceAccount as admin.ServiceAccount),
    });

    auth = admin.auth();
    db = admin.firestore();
    console.log('Firebase Admin initialized');
  } catch (error) {
    console.error('Firebase Admin initialization error:', error);
    auth = {} as admin.auth.Auth;
    db = {} as admin.firestore.Firestore;
  }
} else {
  console.log('Firebase not configured - set FIREBASE_PROJECT_ID, FIREBASE_PRIVATE_KEY, FIREBASE_CLIENT_EMAIL in .env');
  auth = {} as admin.auth.Auth;
  db = {} as admin.firestore.Firestore;
}

export { auth, db };
