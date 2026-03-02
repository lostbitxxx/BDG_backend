# BoDongGua Audio Analysis System - Complete Restructuring Plan

## Executive Summary

**Current State:**
- iFlytek API integration working but audio quality rejections
- Confusing port management (multiple ports in use)
- No fallback system (as requested)
- Need PSC test alignment

**Goal:**
- Clean, production-ready audio analysis system
- iFlytek ISE as primary engine
- Optional librosa enhancement (not required)
- Full PSC alignment

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                         │
│                      http://localhost:3000                      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend (Node.js)                          │
│                      http://localhost:3001                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │  /api/audio/   │  │   /api/chat/    │  │ /api/auth/   │ │
│  │   analyze      │  │                  │  │              │ │
│  └─────────────────┘  └──────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Python Service (Flask)                        │
│                   http://localhost:8001                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   /analyze endpoint                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                │                                │
│                                ▼                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               Audio Preprocessor                          │   │
│  │  - Download from S3                                       │   │
│  │  - Convert to PCM 16kHz mono                             │   │
│  │  - Validate quality                                       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                │                                │
│                                ▼                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Primary: iFlytek ISE API                     │   │
│  │  - WebSocket connection                                   │   │
│  │  - Chinese pronunciation scoring                          │   │
│  │  - Returns: pronunciation, fluency, tone, overall        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                │                                │
│                                ▼                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Optional: Librosa Enhancement                    │   │
│  │  - Local pitch/tone analysis                             │   │
│  │  - Used only if iFlytek succeeds (enhancement only)      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## PSC Test Alignment

### PSC (Putonghua Shuiping Ceshi) Structure

| Part | Content | Weight | Our Feature |
|------|---------|--------|--------------|
| **1. 朗读 (Reading)** | Read passage aloud | 30% | ✅ Primary focus |
| **2. 判断题** | Tone/phonetic判断 | 25% | Future enhancement |
| **3. 听力 (Listening)** | Audio comprehension | 25% | Future enhancement |
| **4. 说话 (Speaking)** | Topic speaking | 20% | Future enhancement |

### Current Focus: Part 1 (朗读 - Reading Aloud)

**iFlytek Returns:**
- `pronunciation_score` - 发音准确度 (30% weight in PSC)
- `fluency_score` - 流畅度
- `tone_score` - 声调准确度
- `total_score` - 总分 (converted to PSC level)

**PSC Levels:**
| Score | Level | Grade |
|-------|-------|-------|
| 97-100 | Level 1 (一级) | A+ |
| 92-96 | Level 1 (一级) | A |
| 87-91 | Level 2 (二级) | A- |
| 80-86 | Level 2 (二级) | B+ |
| 70-79 | Level 3 (三级) | B |
| 60-69 | Level 3 (三级) | C |
| <60 | Below Level 3 | D |

---

## File Structure

```
BDG/
├── BDG_backend/
│   ├── src/
│   │   ├── routes/
│   │   │   └── audio.ts          # Audio endpoints
│   │   └── index.ts              # Backend entry
│   ├── .env                      # All configs here
│   └── package.json
│
├── tone-analysis/                # NEW: Python service (固定端口!)
│   ├── app.py                   # Flask entry (port 8001)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audio_preprocessor.py
│   │   ├── iflytek_ise.py       # Primary engine
│   │   └── librosa_enhancer.py   # Optional enhancement
│   └── requirements.txt
│
└── BDG_frontend/
    └── src/
        └── components/
            ├── MockTest.tsx      # Main test UI
            └── AudioRecorder.tsx
```

---

## Implementation Steps

### Step 1: Fix Port Confusion
**Action:** Use fixed port **8001** for Python service
- Update .env: `PYTHON_SERVICE_URL=http://localhost:8001`
- Always use this port (no more changing ports!)

### Step 2: Rebuild iFlytek Integration
**File:** `tone-analysis/services/iflytek_ise.py`

Key fixes:
- [x] Proper WebSocket handling
- [x] Correct audio format (PCM 16kHz mono)
- [x] Better error messages
- [x] XML parsing for scores
- [x] Rejection handling with user-friendly messages

### Step 3: Add Audio Preprocessing
**File:** `tone-analysis/services/audio_preprocessor.py`

Needs:
- [ ] Convert any format to PCM 16kHz mono (using ffmpeg)
- [ ] Audio quality validation before sending
- [ ] Return error if conversion fails

### Step 4: Optional Librosa Enhancement
**File:** `tone-analysis/services/librosa_enhancer.py`

Purpose:
- Local pitch analysis
- Tone correctness verification
- Only runs AFTER iFlytek succeeds
- Adds to response, doesn't replace

### Step 5: Frontend Alignment
**File:** `BDG_frontend/src/components/MockTest.tsx`

Needs:
- [ ] Show PSC level and grade
- [ ] Display individual scores (pronunciation, fluency, tone)
- [ ] Show helpful error messages when iFlytek fails
- [ ] Add tips for better recording

---

## Configuration

### .env Settings
```bash
# Python Tone Analysis Service (固定!)
PYTHON_SERVICE_URL=http://localhost:8001

# iFlytek Credentials
IFLYTEK_APP_ID=ga8e4cf3
IFLYTEK_API_KEY=8d002d242597976963ba7e41c8f0da73
IFLYTEK_API_SECRET=531014bba3020449ca222f0053028652

# AWS S3 (for audio storage)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=bodonggua-audio
```

### Startup Commands
```bash
# Terminal 1: Python service (always port 8001!)
cd ~/Documents/Learning_Resources/Competition/BDG/tone-analysis
PORT=8001 python3 app.py

# Terminal 2: Backend
cd ~/Documents/Learning_Resources/Competition/BDG/BDG_backend
npm run dev

# Terminal 3: Frontend
cd ~/Documents/Learning_Resources/Competition/BDG/BDG_frontend
npm start
```

---

## API Response Format

### Success Response
```json
{
  "success": true,
  "expected": "春天",
  "scores": {
    "overall": 85.5,
    "pronunciation": 88.0,
    "fluency": 82.0,
    "tone": 86.0,
    "level": "Level 2",
    "grade": "B+",
    "pass": true
  },
  "feedback": "良好！继续保持，多练习会更棒！",
  "processing_time": 3.2,
  "engine": "iflytek-ise",
  "test_type": "PSC Reading Aloud"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Audio quality too low. Please speak clearly and try again.",
  "tips": [
    "Speak louder and clearer",
    "Reduce background noise",
    "Hold microphone closer"
  ]
}
```

---

## Audio Quality Requirements

For iFlytek to accept audio:

1. **Format:** PCM 16kHz, 16-bit, mono
2. **Duration:** 1-60 seconds
3. **Volume:** Loud enough (not too quiet)
4. **Noise:** Minimal background noise
5. **Speech:** Single speaker, clear pronunciation

### Preprocessing Pipeline
```
S3 Audio (WebM/MP3/WAV)
        │
        ▼
    ffmpeg convert
        │
        ▼
  PCM 16kHz mono
        │
        ▼
  Validate quality
        │
        ▼
   iFlytek API
```

---

## Next Actions

### Immediate (This Session)
1. ✅ Clean iFlytek implementation done
2. ⬜ Fix audio preprocessing (convert to PCM 16kHz)
3. ⬜ Set fixed port 8001
4. ⬜ Test with good quality audio

### Future Enhancements
1. Add librosa as optional enhancement
2. Add PSC Parts 2-4 features
3. Improve frontend UI alignment
4. Add audio quality feedback before sending

---

## Summary

| Component | Status | Notes |
|-----------|--------|-------|
| iFlytek Integration | ✅ Working | Audio quality issue only |
| Fallback System | ❌ Removed | As requested |
| Port Management | ⬜ Need fix | Use 8001 |
| Audio Preprocessing | ⬜ Need fix | Convert to PCM |
| PSC Alignment | ⬜ Partial | Level/grade mapping |
| Frontend UI | ⬜ Review | Align with PSC |
