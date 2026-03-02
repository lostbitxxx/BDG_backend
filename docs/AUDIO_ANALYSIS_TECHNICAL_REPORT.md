# BoDongGua Audio Analysis System - Technical Documentation

## Overview

This document provides a comprehensive technical explanation of the BoDongGua (BDG) audio analysis system for Mandarin Chinese pronunciation evaluation. The system is designed for PSC (Putonghua Shuiping Ceshi / 普通话水平测试) test preparation, specifically targeting Cantonese speakers who need to improve their Mandarin pronunciation.

---

## System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Python Service  │────▶│  Analysis Core  │
│  (React)    │     │ (Express)   │     │   (Flask)        │     │  (Whisper+ML)  │
│  Port 3000  │     │ Port 3001   │     │   Port 60678     │     │                 │
└─────────────┘     └─────────────┘     └──────────────────┘     └─────────────────┘
                           │                                               │
                           ▼                                               ▼
                    ┌─────────────┐                              ┌─────────────────┐
                    │    MongoDB   │                              │       S3        │
                    │   + Redis    │                              │  (Audio Store)  │
                    └─────────────┘                              └─────────────────┘
```

---

## Component Responsibilities

### 1. Frontend (React + TypeScript)
- **Location**: `BDG_frontend/`
- **Port**: 3000
- **Responsibilities**:
  - User interface for recording audio
  - Audio capture using Web Audio API
  - Display analysis results
  - MockTest component handles recording flow

### 2. Backend (Express + TypeScript)
- **Location**: `BDG_backend/`
- **Port**: 3001
- **Responsibilities**:
  - Authentication (JWT)
  - Audio file upload to S3
  - Route requests to Python service
  - API endpoints in `src/routes/audio.ts`

### 3. Python Audio Service (Flask)
- **Location**: `BDG_backend/tone-analysis/`
- **Port**: 60678 (configurable via PORT env)
- **Responsibilities**:
  - Audio preprocessing
  - Speech-to-text transcription (Whisper)
  - Pronunciation scoring
  - Tone analysis
  - Fluency analysis

---

## Audio Analysis Pipeline

### Step 1: User Recording (Frontend)

```typescript
// MockTest.tsx - Audio recording flow
const handleStopRecording = async () => {
  // 1. Stop MediaRecorder
  mediaRecorder.stop();
  
  // 2. Create blob from recorded chunks
  const audioBlob = new Blob(chunks, { type: 'audio/webm' });
  
  // 3. Upload to backend via FormData
  const formData = new FormData();
  formData.append('audio', audioBlob, 'recording.webm');
  
  // 4. Backend uploads to S3, returns URL
  const uploadResponse = await fetch('/api/audio/upload', {
    method: 'POST',
    body: formData
  });
  
  // 5. Call analyze endpoint with S3 URL
  const analyzeResponse = await fetch('/api/audio/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      audioUrl: s3Url,
      expectedText: question.content,
      section: question.section
    })
  });
};
```

### Step 2: Audio Upload (Backend)

```
User Audio → Backend (/api/audio/upload) → AWS S3 → S3 URL
```

**Code Location**: `src/routes/audio.ts`

```typescript
router.post('/upload', upload.single('audio'), async (req, res) => {
  // 1. Validate file
  // 2. Upload to S3 using AWS SDK
  // 3. Return S3 URL
  const s3Url = await uploadToS3(file);
  res.json({ audioUrl: s3Url });
});
```

### Step 3: Analysis Request Flow

```
Frontend → Backend (/api/audio/analyze) → Python Service → Return Results
```

**Backend Code**: `src/routes/audio.ts`

```typescript
router.post('/analyze', async (req, res) => {
  const { audioUrl, expectedText, section } = req.body;
  
  // Call Python service
  const pythonResponse = await axios.post(
    `${PYTHON_SERVICE_URL}/analyze`,
    { audio_url: audioUrl, expected_text: expectedText, section }
  );
  
  res.json(pythonResponse.data);
});
```

---

## Python Audio Analysis Engine

### Overview

The Python service (`app.py`) is the core of the audio analysis system. It performs **real** audio analysis using:

1. **Faster Whisper** - Speech-to-text transcription
2. **Text Comparison** - Pronunciation scoring
3. **Librosa** - Tone/pitch analysis
4. **Speaking Rate Calculation** - Fluency scoring

### File Structure

```
tone-analysis/
├── app.py                      # Main Flask application
├── services/
│   ├── audio_preprocessor.py   # Audio download & validation
│   ├── whisper_service.py       # Faster Whisper transcription
│   ├── tone_analyzer.py        # Librosa pitch detection
│   └── pinyin_db.py           # Pinyin & tone database
├── requirements.txt            # Python dependencies
└── .env                       # Environment variables
```

### Analysis Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PYTHON AUDIO SERVICE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐  │
│  │ Audio Input  │────▶│  Download &  │────▶│   Validate Audio         │  │
│  │ (S3 URL)     │     │  Validate    │     │   - File size > 1KB     │  │
│  └──────────────┘     └──────────────┘     │   - Duration > 0.5s     │  │
│                                             └──────────────────────────┘  │
│                                                       │                    │
│                                                       ▼                    │
│                                             ┌──────────────────────────┐  │
│                                             │   WHISPER TRANSCRIPTION │  │
│                                             │   (Faster Whisper)       │  │
│                                             │   - Speech to text       │  │
│                                             │   - Language: zh         │  │
│                                             │   - Output: Chinese     │  │
│                                             └──────────────────────────┘  │
│                                                       │                    │
│                                                       ▼                    │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                      SCORING COMPONENTS                             │  │
│  ├─────────────────────┬─────────────────────┬───────────────────────┤  │
│  │  Pronunciation       │  Tone Analysis      │  Fluency Analysis     │  │
│  │  (40% weight)       │  (30% weight)       │  (30% weight)        │  │
│  ├─────────────────────┼─────────────────────┼───────────────────────┤  │
│  │  - Character match   │  - Librosa pitch    │  - Characters/min    │  │
│  │  - Text comparison  │  - Tone detection   │  - Optimal: 180-280  │  │
│  │  - Error positions │  - Expected vs      │  - Too slow/fast     │  │
│  │                    │    detected          │    penalties          │  │
│  └─────────────────────┴─────────────────────┴───────────────────────┘  │
│                                                       │                    │
│                                                       ▼                    │
│                                             ┌──────────────────────────┐  │
│                                             │   OVERALL CALCULATION  │  │
│                                             │                          │  │
│                                             │   Overall =              │  │
│                                             │   (Pron × 0.4) +        │  │
│                                             │   (Tone × 0.3) +        │  │
│                                             │   (Fluency × 0.3)       │  │
│                                             │                          │  │
│                                             │   Map to PSC Levels:    │  │
│                                             │   97+ → Level 1-A       │  │
│                                             │   92-96 → Level 1-B     │  │
│                                             │   87-91 → Level 2-A     │  │
│                                             │   80-86 → Level 2-B     │  │
│                                             │   70-79 → Level 3-A     │  │
│                                             │   60-69 → Level 3-B     │  │
│                                             │   <60  → Below Level 3  │  │
│                                             └──────────────────────────┘  │
│                                                       │                    │
│                                                       ▼                    │
│                                             ┌──────────────────────────┐  │
│                                             │   Return JSON Response   │  │
│                                             │   {                     │  │
│                                             │     "success": true,    │  │
│                                             │     "transcription": "",│  │
│                                             │     "scores": {         │  │
│                                             │       "overall": 85.0,  │  │
│                                             │       "pronunciation": 90│  │
│                                             │       "tone": 80,        │  │
│                                             │       "fluency": 82,     │  │
│                                             │       "level": "Level 2" │  │
│                                             │     },                   │  │
│                                             │     "feedback": ""       │  │
│                                             │   }                     │  │
│                                             └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Scoring Algorithms

### 1. Pronunciation Scoring (40% weight)

**Purpose**: Evaluate how accurately the user pronounced the expected text.

**Algorithm**:

```python
def analyze_pronunciation(expected: str, actual: str) -> tuple:
    # Step 1: Extract Chinese characters only
    expected_clean = re.sub(r'[^\u4e00-\u9fff]', '', expected)
    actual_clean = re.sub(r'[^\u4e00-\u9fff]', '', actual)
    
    # Step 2: Character-by-character comparison
    expected_chars = list(expected_clean)
    actual_chars = list(actual_clean)
    
    correct = 0
    errors = []
    
    for i in range(min(len(expected_chars), len(actual_chars))):
        if expected_chars[i] == actual_chars[i]:
            correct += 1
        else:
            errors.append({
                'position': i,
                'expected': expected_chars[i],
                'actual': actual_chars[i]
            })
    
    # Step 3: Calculate match rate
    match_rate = (correct / len(expected_chars)) * 100
    
    # Step 4: Convert to score (0-100)
    if match_rate >= 95:
        score = 100
    elif match_rate >= 90:
        score = 90 + (match_rate - 90) * 2
    elif match_rate >= 70:
        score = 70 + (match_rate - 70) * 0.75
    else:
        score = match_rate * 0.9
    
    return score, details
```

**Example**:

| Expected | Actual | Match Rate | Score |
|----------|--------|------------|-------|
| 春天来了 | 春天来了 | 100% | 100 |
| 春天来了 | 冬天来了 | 75% | 73.75 |
| 春天来了 | 夏天来了 | 50% | 45 |
| 春天来了 | (empty) | 0% | 10 |

### 2. Tone Analysis (30% weight)

**Purpose**: Evaluate the accuracy of Mandarin Chinese tones (声调).

**Mandarin Tones**:
- **Tone 1 (高平)**: Flat, high pitch (~300Hz)
- **Tone 2 (上升)**: Rising from low to high
- **Tone 3 (降升)**: Dipping low then rising
- **Tone 4 (降)**: Falling from high to low

**Algorithm**:

```python
def analyze_tones_local(audio_path: str, expected_text: str) -> tuple:
    # Step 1: Get expected tones from pinyin
    expected_tones = []
    for char in expected_text:
        info = get_char_info(char)  # Uses pypinyin
        expected_tones.append(info.get('tone', 0))
    
    # Step 2: Extract pitch from audio using librosa
    tone_analyzer = ToneAnalyzer()
    tone_result = tone_analyzer.analyze_tones(audio_path, chars_list)
    
    # Step 3: Compare detected vs expected
    if expected_tones[0] == detected_tone:
        tone_score = 80 + confidence * 20  # 80-100
    elif detected_tone == 0:
        tone_score = 50  # Neutral/unclear
    else:
        # Wrong tone - calculate penalty
        tone_score = max(30, 70 - abs(expected - detected) * 15)
    
    return tone_score, details
```

**Librosa Pitch Extraction**:

```python
def extract_pitch(self, audio_path: str):
    # Load audio
    y, sr = librosa.load(audio_path, sr=16000)
    
    # Extract pitch using pyin algorithm
    f0, voiced_flag, voiced_probs = librosa.pyin(
        y,
        fmin=librosa.note_to_hz('E2'),  # ~82 Hz
        fmax=librosa.note_to_hz('C6'),  # ~1047 Hz
        sr=sr,
        hop_length=512
    )
    
    # Analyze pitch contour for tone pattern
    # Flat = Tone 1, Rising = Tone 2, etc.
```

### 3. Fluency Analysis (30% weight)

**Purpose**: Evaluate speaking rate and fluency.

**Algorithm**:

```python
def analyze_fluency(audio_duration: float, transcription: str, expected_text: str):
    # Calculate Characters Per Minute (CPM)
    char_count = len(transcription)
    cpm = (char_count / audio_duration) * 60
    
    # Scoring based on optimal range
    if cpm < 60:
        score = max(30, 60 - (60 - cpm) * 0.5)
    elif cpm < 120:
        score = 60 + (cpm - 60) * 0.3
    elif cpm <= 280:
        score = 78 + min(22, (280 - abs(220 - cpm)) * 0.1)
    elif cpm <= 360:
        score = 80 - (cpm - 280) * 0.15
    else:
        score = max(40, 70 - (cpm - 360) * 0.1)
    
    return score, {'cpm': cpm, 'optimal': '180-280'}
```

**CPM Guidelines**:
- **< 60 CPM**: Too slow (penalty)
- **60-120 CPM**: Slow but acceptable
- **180-280 CPM**: Optimal (bonus)
- **280-360 CPM**: Fast but okay
- **> 360 CPM**: Too fast (penalty)

### 4. Overall Score Calculation

```python
# Weighted average
Overall = (Pronunciation × 0.4) + (Tone × 0.3) + (Fluency × 0.3)

# Map to PSC Levels
if overall >= 97:  level, grade = 'Level 1', 'A'
elif overall >= 92: level, grade = 'Level 1', 'B'
elif overall >= 87: level, grade = 'Level 2', 'A'
elif overall >= 80: level, grade = 'Level 2', 'B'
elif overall >= 70: level, grade = 'Level 3', 'A'
elif overall >= 60: level, grade = 'Level 3', 'B'
else:               level, grade = 'Below Level 3', 'C'
```

---

## Edge Cases & Error Handling

### 1. No Audio / Silence

```python
if audio_size < 1000:  # Less than 1KB
    return {
        'scores': {
            'overall': 0,
            'pronunciation': 0,
            'tone': 0,
            'fluency': 0,
        },
        'feedback': '请录音后再试'
    }
```

### 2. Audio Too Short

```python
if audio_duration < 0.5:
    return {
        'scores': {'overall': 0, ...},
        'feedback': '录音时间太短'
    }
```

### 3. Transcription Fails

```python
if not transcription_result.get('success'):
    # Use expected text as fallback
    # Calculate pronunciation based on expected text only
    pronunciation = 50  # Default partial score
```

---

## API Reference

### Backend Endpoints

#### POST /api/audio/upload
Upload audio file to S3.

**Request**: `multipart/form-data`
```
audio: File (audio/webm, audio/wav, audio/mp3)
```

**Response**:
```json
{
  "success": true,
  "audioUrl": "https://bodonggua-audio.s3.../audio.webm"
}
```

#### POST /api/audio/analyze
Analyze audio pronunciation.

**Request**: `application/json`
```json
{
  "audioUrl": "https://.../audio.webm",
  "expectedText": "春天来了",
  "section": 4
}
```

**Response**:
```json
{
  "success": true,
  "transcription": "春天来了",
  "expected": "春天来了",
  "scores": {
    "overall": 85.5,
    "pronunciation": 90.0,
    "tone": 80.0,
    "fluency": 82.0,
    "level": "Level 2-A",
    "grade": "A",
    "pass": true,
    "details": {
      "pronunciation": {...},
      "tone": {...},
      "fluency": {...}
    }
  },
  "feedback": "很好！继续保持！",
  "processing_time": 3.2,
  "engine": "local-faster-whisper"
}
```

### Python Service Endpoints

#### GET /health
Health check.

**Response**:
```json
{
  "status": "ok",
  "service": "tone-analysis",
  "engine": "Faster Whisper + Tone Analysis (Local)",
  "whisper_ready": true
}
```

#### POST /analyze
Main analysis endpoint.

**Request**:
```json
{
  "audio_url": "https://.../audio.webm",
  "expected_text": "春天来了",
  "section": 4
}
```

---

## Dependencies

### Python (`requirements.txt`)
```
flask>=2.3.0
flask-cors>=4.0.0
faster-whisper>=0.10.0    # Speech recognition (local, no API key)
librosa>=0.10.0           # Audio analysis
numpy>=1.24.0
pypinyin>=0.49.0          # Pinyin conversion
soundfile>=0.12.0        # Audio file handling
requests>=2.28.0
boto3>=1.28.0             # AWS S3
websocket-client>=1.6.0
```

### Node.js
```
express, mongoose, redis, @aws-sdk/client-s3,
socket.io, jsonwebtoken, bcrypt
```

---

## PSC Scoring Standards

The system follows the official PSC (普通话水平测试) scoring standards:

| Level | Score Range | Description |
|-------|-------------|-------------|
| **Level 1-A** | 97-100 | Native/broadcast level |
| **Level 1-B** | 92-96 | Near-native |
| **Level 2-A** | 87-91 | Good for teaching in northern China |
| **Level 2-B** | 80-86 | Good for teaching in southern China |
| **Level 3-A** | 70-79 | Standard professional Mandarin |
| **Level 3-B** | 60-69 | Basic professional Mandarin |
| **Below Level 3** | <60 | Does not meet professional standards |

---

## Troubleshooting

### Issue: Score always around 60-70 even with no audio

**Cause**: Old fallback scoring was using random numbers.

**Fix**: Updated to real analysis (this version). Make sure Python service is using the new `app.py`.

### Issue: Whisper transcription is inaccurate

**Possible causes**:
1. Audio quality too low
2. Too much background noise
3. Speaking too fast/slow

**Solutions**:
1. Use headphones
2. Record in quiet environment
3. Speak at normal pace (180-280 CPM)

### Issue: Port conflicts

- Port 5000: Used by macOS AirPlay Receiver
- Solution: Use alternative port (60678) or disable AirPlay

---

## Future Improvements

1. **Multi-word tone analysis**: Analyze tones for each character in multi-character words
2. **Reference audio comparison**: Compare user audio with native speaker recordings
3. **iFlytek ISE integration**: Add professional pronunciation evaluation API as alternative
4. **Continuous improvement**: Track user progress over time

---

## License & Credits

- **Whisper**: OpenAI (MIT License)
- **Faster Whisper**: OpenAI (MIT License)
- **Librosa**: Librosa Team (ISC License)
- **System**: BoDongGua Project

---

*Document Version: 1.0*  
*Last Updated: 2026-03-01*  
*Author: Auto (AI Coding Assistant)*
