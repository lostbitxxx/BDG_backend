# BoDongGua Development Plan - Complete Project

## Current Status
- ✅ Frontend (React) running on port 3000
- ✅ Backend (Express) running on port 3001
- ✅ MongoDB connected
- ✅ Redis connected
- ✅ AWS S3 for audio storage
- ✅ Python Audio Analysis Service (needs fix - Whisper API issue)
- ✅ Audio Recording in MockTest page
- ❌ Analysis still failing (Whisper module issue)

---

## Remaining Work to Complete

### Phase 3: Fix Audio Analysis System (Priority 1)

#### Issue: Whisper Module Error
**Problem:**module 'whisper `' has no attribute 'load'`

**Solution:**

 Options1. **Option A: Use faster-whisper (Recommended)**
   - Install: `pip install faster-whisper`
   - More efficient, works better
   - Requires code change in whisper_service.py

2. **Option B: Use HuggingFace Transformers**
   - Install: `pip install transformers torch`
   - Uses different model architecture

3. **Option C: Use API-based Whisper**
   - Use OpenAI Whisper API (paid, but reliable)
   - Better accuracy

**What you need to do manually:**
- Choose which option you prefer
- Tell me to proceed

---

### Phase 4: Mock Test System

#### 4.1 Question Bank
Create database of PSC test questions:

```
Questions:
- 100 single-character words (Section 1)
- 100 polysyllabic words (Section 2)  
- 60 reading passages (Section 4)
- 30 speaking topics (Section 5)
```

#### 4.2 Test Flow
1. User selects test type
2. Present questions sequentially
3. Record and analyze each answer
4. Calculate section scores
5. Generate overall score

**What you need to do manually:**
- Provide test questions/content OR
- Approve using sample questions for now

---

### Phase 5: Tailored Practice System

#### 5.1 Error Tracking
- Store user's mistakes in MongoDB
- Track by category: tones, retroflex, nasals, vocabulary

#### 5.2 Practice Generation
- Generate exercises based on errors
- Save to "Practice Gallery"

**Implementation:**
- New MongoDB schema for practice history
- New API endpoints for practice management

---

### Phase 6: Chat/AI Companion System

#### 6.1 Current State
- Basic chat UI exists
- Mock responses only
- No real AI integration

#### 6.2 Implementation Needed
1. **Integrate Grok API** (xAI)
   - Sign up at https://x.ai
   - Get API key
   - Replace mock responses with real AI

2. **Integrate TTS** (ElevenLabs or Azure)
   - For character voice responses
   - Make companion "speak"

3. **Socket.io** (optional, for real-time)
   - For live chat experience

**What you need to do manually:**
- Sign up for xAI Grok API
- Get API key
- OR choose alternative (OpenAI, Anthropic)

---

### Phase 7: Gamification

#### 7.1 CGA Leaderboard
- Calculate scores based on practice consistency
- Display rankings

#### 7.2 Companion Affinity
- Character evolves based on progress
- Unlock features as user improves

---

### Phase 8: Deployment

#### 8.1 Frontend
- Deploy to Vercel (free)
- Configure custom domain (optional)

#### 8.2 Backend
- Deploy to Vercel or Railway
- Or keep on local/Render

#### 8.3 Python Service
- Deploy to Railway/Render/Heroku
- Or run locally

---

## Cost Estimate

| Service | Free Tier | Monthly Cost |
|---------|-----------|--------------|
| MongoDB Atlas | 512MB | $0 |
| Redis | 30MB | $0 |
| Vercel | 100GB | $0 |
| AWS S3 | 5GB | ~$1 |
| Grok API | Trial available | ~$20/mo |
| ElevenLabs | Free tier | $0-10/mo |

**Total: ~$20-30/month**

---

## Approval Needed

Please review and approve each phase. Tell me:

1. **Phase 3:** Which Whisper solution do you prefer?
   - Option A: faster-whisper (recommended, free)
   - Option B: HuggingFace Transformers (free)
   - Option C: OpenAI API (paid, most accurate)

2. **Phase 4:** Use sample questions for now?

3. **Phase 6:** Which AI provider for chat?
   - xAI Grok
   - OpenAI GPT
   - Anthropic Claude

---

## Files Created So Far

```
BDG/
├── docs/
│   └── AUDIO_ANALYSIS_SYSTEM.md
├── BDG_frontend/
│   └── (React app)
├── BDG_backend/
│   └── (Express app)
└── tone-analysis/
    ├── app.py
    ├── requirements.txt
    └── services/
        ├── pinyin_db.py
        ├── audio_preprocessor.py
        ├── whisper_service.py
        ├── tone_analyzer.py
        └── scorer.py
```
