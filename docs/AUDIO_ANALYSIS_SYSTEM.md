# 🎤 BoDongGua Audio Analysis System

## Overview

This document explains the pronunciation analysis system for BoDongGua, designed to evaluate Putonghua (Mandarin Chinese) pronunciation for PSC (Putonghua Shuiping Ceshi) test preparation.

---

## Why This System?

### The Problem
- SpeechSuper (paid API) is expensive
- Generic speech recognition doesn't work well for Chinese
- Need PSC-specific analysis (tones, retroflex, nasals)

### Our Solution
Build our own system using open-source tools:
- **Whisper** - Speech-to-text (open source)
- **Librosa** - Audio signal processing for tone analysis
- **Custom scoring** - PSC-specific metrics

---

## System Architecture

```
User Recording
      ↓
AWS S3 (Storage)
      ↓
Python Microservice (Flask)
      ↓
┌─────┴─────┐
│ Analysis   │
│ Pipeline   │
├────────────┤
│ 1. Preprocess │
│ 2. Whisper    │
│ 3. Tone Detect │
│ 4. Score      │
└─────┬─────┘
      ↓
MongoDB (Results)
      ↓
Frontend Display
```

---

## Analysis Pipeline

### Step 1: Audio Preprocessing

**Purpose:** Ensure consistent audio quality for analysis

**Operations:**
1. Convert to WAV format (16kHz, mono)
2. Volume normalization (-20dB)
3. Trim silence
4. Validate duration (1-60 seconds)

```python
# Input: Any audio format (webm, mp3, wav, m4a)
# Output: Clean WAV file, 16kHz, mono
```

### Step 2: Whisper Transcription

**Purpose:** Convert speech to text

**Models:**
| Model | Speed | Accuracy | RAM |
|-------|-------|----------|-----|
| tiny | 10x | Good | 1GB |
| base | 7x | Very Good | 1GB |
| small | 4x | Excellent | 2GB |

**Recommendation:** Use `base` for development, `small` for production

```python
# Input: Audio file
# Output: Transcribed text
# Example: "春天来了" → "chun tian lai le"
```

### Step 3: Tone Analysis (Librosa)

**Purpose:** Detect Mandarin tones from audio pitch

**Mandarin Tones:**
| Tone | Description | F0 Pattern |
|------|-------------|-------------|
| 1 | High flat | ˉ (flat, ~300Hz) |
| 2 | Rising | ˊ (low to high) |
| 3 | Dipping | ˇ (low→high→low) |
| 4 | Falling | ˋ (high to low) |
| 0 | Neutral | ˙ (short, low) |

**How it works:**
1. Extract pitch contour using librosa
2. Map pitch pattern to tones
3. Compare with expected tones

```python
# Input: Audio file
# Output: Detected tones for each character
# Example: "妈麻马骂" → [1, 2, 3, 4]
```

### Step 4: Pinyin Comparison

**Purpose:** Detect phoneme errors

**Error Types:**
1. **Retroflex initials**: zh, ch, sh, r (hard for Cantonese speakers)
2. **Nasal finals**: an, en, in, un, ün, ang, eng, ing, ong
3. **Vowel differentiation**: i vs ü, ei vs ui, etc.

```python
# Input: Expected text + Whisper result
# Output: Error list with positions
# Example: Expected "知道" → Heard "基地"
# Error: retroflex "zh" → flat "j"
```

### Step 5: Scoring

**Score Calculation:**

```typescript
pronunciation = (transcriptionMatch * 0.3) + 
               (phonemeAccuracy * 0.4) + 
               (toneAccuracy * 0.3);

fluency = (speechRate * 0.5) + (pausePenalty * 0.5);

overall = (pronunciation * 0.7) + (fluency * 0.3);
```

### Step 6: Feedback Generation

**Purpose:** Provide actionable improvement tips

Using Grok/AI to generate:
- What to improve specifically
- Practice suggestions
- Encouragement

---

## Data Structures

### Input

```typescript
interface AnalyzeRequest {
  audioUrl: string;        // S3 URL
  expectedText: string;    // Text user should read
  section: 1 | 2 | 3 | 4; // PSC section
}
```

### Output

```typescript
interface AnalysisResult {
  success: boolean;
  
  // Transcription
  transcription: string;
  transcriptionMatch: number; // 0-100%
  
  // Tone Analysis
  toneAccuracy: number;      // 0-100
  toneErrors: ToneError[];
  
  // Phoneme Analysis  
  phonemeAccuracy: number;  // 0-100
  retroflexErrors: RetroflexError[];
  nasalErrors: NasalError[];
  
  // Scores
  pronunciation: number;    // 0-100
  fluency: number;          // 0-100
  overall: number;          // 0-100
  
  // Feedback
  feedback: string;
  suggestions: string[];
  
  // Metadata
  processingTime: number;
  modelUsed: string;
}

interface ToneError {
  char: string;
  position: number;
  expected: 1 | 2 | 3 | 4 | 0;
  detected: 1 | 2 | 3 | 4 | 0;
}

interface RetroflexError {
  char: string;
  position: number;
  expected: "zh" | "ch" | "sh" | "r";
  detected: "z" | "c" | "s" | "l" | "n";
}
```

---

## Error Handling

### Fallback Strategies

| Scenario | What Happens |
|----------|-------------|
| Audio format invalid | Return error before processing |
| Audio too short (<1s) | Return "Audio too short" |
| Audio too long (>60s) | Process in chunks |
| Whisper fails | Skip transcription, use tone-only scoring |
| Tone analysis fails | Skip tone score, use text matching |
| Network error | Retry 3 times with backoff |
| All fails | Return error, suggest re-recording |

---

## Caching

Results are cached in Redis to avoid reprocessing:

```typescript
cacheKey = md5(audioUrl + expectedText);
cacheTTL = 24 hours;
```

---

## Question Bank Integration

For PSC, we need reference texts:

### Section 1: Single Characters (100 words)
- Focus: Individual character pronunciation
- Each character has known pinyin/tone

### Section 2: Polysyllabic Words (100 words)
- Focus: Word-level pronunciation
- Common difficult words

### Section 3: Passage Reading (400 chars)
- Focus: Fluency and expression
- 60 preset passages

### Section 4: Speaking (3 min)
- Focus: Spontaneous speech
- 30 topic prompts

---

## Usage

### Start the Python Service

```bash
cd tone-analysis
pip install -r requirements.txt
python app.py
# Service runs on http://localhost:5000
```

### Call from Backend

```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "audio_url": "https://s3.../audio.webm",
    "expected_text": "春天来了",
    "section": 4
  }'
```

---

## Dependencies

### Python (tone-analysis/)
```
flask
flask-cors
whisper
librosa
numpy
pypinyin
soundfile
requests
```

### System
- FFmpeg (for audio conversion)

### External Services
- AWS S3 (audio storage)
- Redis (caching)
- MongoDB (results storage)
- Grok API (feedback generation)

---

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|-----------|
| Whisper Model | tiny | small/base |
| Caching | Disabled | Enabled |
| Timeout | 60s | 30s |
| Logs | Verbose | Minimal |

---

## Troubleshooting

### Common Issues

1. **"No module named 'whisper'"**
   - Run: `pip install -r requirements.txt`

2. **"ffmpeg not found"**
   - Run: `brew install ffmpeg`

3. **Whisper takes too long**
   - Use smaller model (tiny/base instead of small)

4. **Tone detection inaccurate**
   - Ensure audio is clear (no background noise)
   - Check that speaker is facing microphone

---

## Future Improvements

1. **Speaker diarization** - Detect multiple speakers
2. **Accent detection** - Identify Cantonese-specific errors
3. **Real-time feedback** - WebSocket for live scoring
4. **Progress tracking** - Historical analysis over time
5. **AI tutor** - Grok-powered conversational practice

---

## Contact

For issues or questions about this system, refer to:
- Backend: `/api/audio/analyze` endpoint
- Frontend: `MockTest.tsx` component
- Python Service: `tone-analysis/app.py`

---

*Last Updated: 2026-02-26*
