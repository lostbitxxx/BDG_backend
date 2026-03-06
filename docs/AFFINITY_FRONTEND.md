# Affinity level – frontend requirements

## Backend behaviour

- **AI chat** (POST `/api/chat` or Socket chat): backend does **not** change affinity. If affinity goes up when you chat, the frontend is calling another endpoint (e.g. `/api/auth/affinity/increment`). Remove that call from the chat flow.
- **Mock test / each question**: affinity increases only when **both** are true:
  1. The request to **POST `/api/audio/analyze`** includes the user’s auth token.
  2. The analysis succeeds (`success: true` in the response).

## What to change in the frontend

### 1. Stop affinity increasing on chat

- Do **not** call **POST `/api/auth/affinity/increment`** when the user sends a chat message or when the AI replies.
- Remove any call to `POST /api/auth/affinity/increment` that is tied to the chat screen or chat events.

### 2. Make affinity increase after each mock test question

When calling **POST `/api/audio/analyze`** (e.g. after uploading audio for a question), send the same auth header you use for other protected APIs:

- **Header:** `Authorization: Bearer <user's Firebase/id token>`
- Use the same token you use for `/api/auth/verify` or after login.

Example (fetch):

```js
const token = await getAuthToken(); // your app’s way to get the current user’s token

const res = await fetch(`${API_BASE}/api/audio/analyze`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  },
  body: JSON.stringify({
    audioUrl: s3Url,
    expectedText: questionText,
    section: 4,
  }),
});
const data = await res.json();

// If logged in and analysis succeeded, the backend may return the new affinity level:
if (data.affinityLevel !== undefined) {
  // Update local state / UI with data.affinityLevel (1–5)
}
```

After this, each successful analyze request from a logged-in user will increase affinity (and the backend will log `[Affinity] incremented for user ...`). If the token is not sent, the backend will log `[Affinity] skipped (no auth token sent with /api/audio/analyze)`.
