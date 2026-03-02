# BoDongGua Audio Analysis System

## Overview

The Audio Analysis System is a Mandarin Chinese pronunciation evaluation system for PSC (Putonghua Shuiping Ceshi) test preparation. It uses iFlytek ISE (Intelligent Speech Evaluation) API for pronunciation scoring.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│                  http://localhost:3000                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Backend (Node.js)                           │
│                  localhost:3001                             │
│  - Routes: /api/audio/analyze                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Service (Flask)                         │
│                  localhost:8000                             │
│  - Engine: iFlytek ISE Only (No Fallback)               │
│  - PSC Aligned: Yes                                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  iFlytek ISE API                           │
│           ise-api-sg.xf-yun.com (Singapore)              │
│           - WebSocket: /v2/ise                            │
└─────────────────────────────────────────────────────────────┘
```

## PSC Alignment

### Test Parts

| Part | Type | Weight | Description |
|------|------|--------|-------------|
| 1 | Reading Single Characters | 10% | Single character pronunciation |
| 2 | Reading Words | 20% | Polysyllabic words |
| 3 | Vocabulary & Grammar | 10% | Multiple choice |
| 4 | Reading Passage | 30% | Read 400-character passage |
| 5 | Speaking | 30% | Topic speaking |

### Current Focus
- **Part 4: Reading Passage (朗读作品)** - Primary feature implemented

## iFlytek Integration

### Credentials
```
IFLYTEK_APP_ID=ga8e4cf3
IFLYTEK_API_KEY=8d002d242597976963ba7e41c8f0da73
IFLYTEK_API_SECRET=531014bba3020449ca222f0053028652
```

### API Details
- **Server**: ise-api-sg.xf-yun.com (Singapore)
- **Protocol**: WebSocket
- **Endpoint**: wss://ise-api-sg.xf-yun.com/v2/ise

### Parameters
```python
{
    "sub": "ise",           # Intelligent Speech Evaluation
    "ent": "cn_vip",        # Chinese VIP
    "category": "read_sentence",  # Sentence reading
    "cmd": "ssb",
    "auf": "audio/L16;rate=16000",
    "aue": "raw",
    "text": reference_text,
    "tte": "utf-8"
}
```

### Audio Requirements
- Format: PCM 16kHz mono
- Duration: 1-60 seconds
- Quality: Clear voice, low background noise

## Error Codes

| Code | User Message |
|------|-------------|
| 28676 | Audio quality is too low. Please speak more clearly and try again. |
| 28677 | Too much background noise. Please record in a quieter environment. |
| 28678 | Audio is too short. Please speak longer (at least 3 seconds). |
| 28679 | No speech detected. Please speak directly into the microphone. |
| 28680 | Audio volume is too low. Please speak louder. |
| 28681 | Audio volume is too loud. Please speak softer. |

## API Response

### Success
```json
{
  "success": true,
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
  "engine": "iflytek-ise",
  "test_type": "PSC Reading Aloud"
}
```

### Error
```json
{
  "success": false,
  "error": "Audio quality is too low. Please speak more clearly and try again.",
  "dev_info": "iFlytek error code: 28676"
}
```

## Services

| Service | Port | Status |
|---------|------|--------|
| Frontend | 3000 | Running |
| Backend | 3001 | Running |
| Python | 8000 | Running |

## Files

### Backend
- `tone-analysis/app.py` - Main Flask API
- `tone-analysis/services/iflytek_fixed.py` - iFlytek WebSocket client
- `tone-analysis/services/audio_preprocessor.py` - Audio download & conversion
- `tone-analysis/services/__init__.py` - Services package

### Frontend
- `src/components/MockTest.tsx` - Main test UI
- `src/data/questions.ts` - PSC question bank

## Environment Variables

```bash
# Backend
MONGODB_URI=...
JWT_SECRET=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...

# Python
IFLYTEK_APP_ID=ga8e4cf3
IFLYTEK_API_KEY=8d002d242597976963ba7e41c8f0da73
IFLYTEK_API_SECRET=531014bba3020449ca222f0053028652
PYTHON_SERVICE_URL=http://localhost:8000
```

## Security

- All credentials stored in `.env` files (not committed to Git)
- `.gitignore` configured to exclude sensitive files
- Test files with credentials excluded from Git
