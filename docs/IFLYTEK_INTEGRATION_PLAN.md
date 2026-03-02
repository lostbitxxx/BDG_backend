# BoDongGua Audio Analysis - Integration Plan
## iFlytek API + Whisper + Librosa Hybrid System

---

## Current Problem

The current system was rebuilt to use ONLY local Whisper + Librosa, **bypassing iFlytek entirely**.

The **original design intent** was:
- **iFlytek ISE API** → Primary scoring engine (professional Mandarin evaluation)
- **Faster Whisper** → Transcription only (to show what user said)
- **Librosa** → Enhanced tone analysis (supplement iFlytek)

---

## Why iFlytek Matters

### iFlytek ISE (Pronunciation Evaluation) Capabilities:

| Feature | iFlytek ISE | Local Whisper+Librosa |
|---------|--------------|----------------------|
| **Phoneme-level scoring** | ✅ Yes | ❌ No |
| **Detailed pronunciation feedback** | ✅ Yes | ❌ Basic |
| **Prosody analysis** | ✅ Yes | ❌ Limited |
| **Professional Mandarin evaluation** | ✅ Yes | ❌ Not professional |
| **Cost** | API calls | Free (but less accurate) |

### iFlytek Returns (when working):
```xml
<total_score value="85.5"/>
<pronunciation_score value="88.0"/>
<fluency_score value="82.0"/>
<tone_score value="80.0"/>
<phoneme_detail>
  <phone char="春" pinyin="chun" score="90" status="correct"/>
  <phone char="天" pinyin="tian" score="85" status="correct"/>
</phoneme_detail>
```

---

## Proposed Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HYBRID AUDIO ANALYSIS SYSTEM                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        PHASE 1: Input                                │  │
│  │  Audio (S3 URL) → Download & Validate                              │  │
│  │  - Check: file size > 1KB, duration > 0.5s                        │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│                                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     PHASE 2: Parallel Processing                    │  │
│  │                                                                      │  │
│  │   ┌──────────────────────┐    ┌──────────────────────┐            │  │
│  │   │   iFlytek ISE API    │    │  Faster Whisper      │            │  │
│  │   │   (Primary Scorer)   │    │  (Transcription)     │            │  │
│  │   │                      │    │                      │            │  │
│  │   │  - Overall score     │    │  - What user said    │            │  │
│  │   │  - Pronunciation    │    │  - Confidence        │            │  │
│  │   │  - Tone             │    │  - Language detect  │            │  │
│  │   │  - Fluency          │    │                      │            │  │
│  │   │  - Phoneme details  │    │                      │            │  │
│  │   └──────────────────────┘    └──────────────────────┘            │  │
│  │                                    │                                │  │
│  │                                    ▼                                │  │
│  │   ┌──────────────────────────────────────────────────────────────┐  │  │
│  │   │            Librosa Tone Analyzer (Enhancement)               │  │  │
│  │   │                                                              │  │  │
│  │   │  - Pitch contour extraction                                 │  │  │
│  │   │  - Tone pattern validation                                  │  │  │
│  │   │  - Speaker-independent analysis                             │  │  │
│  │   └──────────────────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│                                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     PHASE 3: Score Fusion                          │  │
│  │                                                                      │  │
│  │   ┌─────────────────────────────────────────────────────────────┐   │  │
│  │   │              HYBRID SCORING ALGORITHM                      │   │  │
│  │   │                                                              │   │  │
│  │   │  IF iFlytek succeeded:                                      │   │  │
│  │   │    - Use iFlytek scores (80% weight)                       │   │  │
│  │   │    - Enhance with Whisper transcription for feedback        │   │  │
│  │   │    - Use Librosa for tone validation                       │   │  │
│  │   │                                                              │   │  │
│  │   │  IF iFlytek failed:                                         │   │  │
│  │   │    - Use Whisper + Text comparison (40%)                   │   │  │
│  │   │    - Use Librosa tone analysis (30%)                        │   │  │
│  │   │    - Use Fluency analysis (30%)                             │   │  │
│  │   │                                                              │   │  │
│  │   └─────────────────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                       │
│                                    ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     PHASE 4: Output                                │  │
│  │                                                                      │  │
│  │   {                                                               │  │
│  │     "success": true,                                              │  │
│  │     "transcription": "...",     // From Whisper                  │  │
│  │     "expected": "...",                                             │  │
│  │     "scores": {                                                   │  │
│  │       "overall": 85.0,       // iFlytek primary                  │  │
│  │       "pronunciation": 88.0,  // iFlytek or Whisper-match        │  │
│  │       "tone": 82.0,          // iFlytek + Librosa validation     │  │
│  │       "fluency": 80.0,       // iFlytek or CPM-based            │  │
│  │       "level": "Level 2",                                           │  │
│  │       "source": "iflytek"    // or "local-fallback"             │  │
│  │     },                                                             │  │
│  │     "feedback": "..."         // Detailed feedback               │  │
│  │   }                                                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Fix iFlytek Integration (Priority 1)

#### 1.1 Verify iFlytek Credentials
Check if credentials work:
```python
# Test credentials
IFLYTEK_APP_ID = "ga8e4cf3"
IFLYTEK_API_KEY = "8d002d242597976963ba7e41c8f0da73"
IFLYTEK_API_SECRET = "531014bba3020449ca222f0053028652"
```

#### 1.2 Debug iFlytek Connection
- Add detailed logging to WebSocket connection
- Check API endpoint (Singapore vs China)
- Verify authentication signature format

#### 1.3 Handle API Failures Gracefully
```python
def call_iflytek(audio_path, text):
    try:
        result = evaluator.evaluate(audio_path, text)
        if result.get('success'):
            return result
    except Exception as e:
        logger.error(f"iFlytek failed: {e}")
    
    # Return flag that iFlytek failed
    return {'success': False, 'fallback': True}
```

### Phase 2: Hybrid Scoring System (Priority 2)

#### 2.1 Score Fusion Logic
```python
def calculate_hybrid_scores(iflytek_result, whisper_result, librosa_result):
    if iflytek_result.get('success'):
        # Use iFlytek as primary
        scores = iflytek_result['scores']
        scores['source'] = 'iflytek'
        
        # Enhance with Whisper transcription
        scores['transcription_match'] = compare_texts(
            expected_text,
            whisper_result.get('text', '')
        )
        
        # Validate with Librosa
        if librosa_result.get('success'):
            scores['tone_validation'] = librosa_result
        
    else:
        # Fallback to local scoring
        scores = calculate_local_scores(whisper_result, librosa_result)
        scores['source'] = 'local-fallback'
    
    return scores
```

#### 2.2 Detailed Feedback Generation
```python
def generate_feedback(scores, iflytek_details, whisper_text):
    feedback_parts = []
    
    # Overall assessment
    if scores['overall'] >= 90:
        feedback_parts.append("🌟 Excellent pronunciation!")
    elif scores['overall'] >= 80:
        feedback_parts.append("✅ Great job!")
    
    # iFlytek-specific feedback
    if scores['source'] == 'iflytek':
        # Use iFlytek phoneme details
        for phone in iflytek_details.get('phonemes', []):
            if phone['status'] != 'correct':
                feedback_parts.append(f"Pronounce '{phone['char']}' ({phone['pinyin']}) more carefully")
    else:
        # Use Whisper comparison
        for error in whisper_text.get('errors', []):
            feedback_parts.append(f"Note: '{error['expected']}' at position {error['position']}")
    
    return " ".join(feedback_parts)
```

### Phase 3: Enhanced Tone Analysis (Priority 3)

#### 3.1 Multi-level Tone Analysis
```python
def enhanced_tone_analysis(audio_path, expected_text):
    # Level 1: Get expected tones from pinyin
    expected_tones = [get_char_info(c)['tone'] for c in expected_text]
    
    # Level 2: Get iFlytek tone scores (if available)
    iflytek_tones = iflytek_result.get('tone_scores', [])
    
    # Level 3: Librosa pitch validation
    librosa_tones = librosa_detect_tones(audio_path)
    
    # Combine: Weight iFlytek > Librosa > Expected
    final_tones = []
    for i, char in enumerate(expected_text):
        if iflytek_tones:
            tone_score = iflytek_tones[i]
        elif librosa_tones:
            tone_score = librosa_tones[i] * 0.7 + expected_tones[i] * 0.3
        else:
            tone_score = expected_tones[i]
        
        final_tones.append({'char': char, 'tone': tone_score})
    
    return final_tones
```

### Phase 4: Transcription Enhancement (Priority 4)

#### 4.1 Whisper + iFlytek Transcription
```python
def get_best_transcription(audio_path):
    # iFlytek ASR (if available)
    iflytek_asr = call_iflytek_asr(audio_path)
    
    # Whisper transcription
    whisper_trans = whisper.transcribe(audio_path)
    
    # Use Whisper as primary, validate with iFlytek
    if iflytek_asr.get('success'):
        # Cross-validate
        if similarity(whisper_trans, iflytek_asr) > 0.8:
            return whisper_trans  # Both agree
        else:
            # Return both for user to verify
            return {'whisper': whisper_trans, 'iflytek': iflytek_asr}
    
    return whisper_trans  # Fallback to Whisper
```

---

## File Structure After Implementation

```
tone-analysis/
├── app.py                      # Main Flask app (updated)
├── services/
│   ├── audio_preprocessor.py   # Audio download & validation
│   ├── whisper_service.py       # Faster Whisper (transcription)
│   ├── tone_analyzer.py        # Librosa (tone enhancement)
│   ├── pinyin_db.py           # Pinyin & tone database
│   │
│   ├── iflytek_ise.py          # iFlytek ISE (PRIMARY scorer) ✅
│   ├── iflytek_asr.py          # iFlytek ASR (transcription)
│   └── hybrid_scorer.py        # NEW: Score fusion engine
│
├── requirements.txt            # Dependencies
└── .env                       # Config (includes iFlytek keys)
```

---

## Scoring Weight Distribution

### When iFlytek Works (Primary):
| Component | Weight | Source |
|-----------|--------|--------|
| Overall Score | 100% | iFlytek |
| Pronunciation | 100% | iFlytek |
| Tone | 100% | iFlytek + Librosa validation |
| Fluency | 100% | iFlytek |

### When iFlytek Fails (Fallback):
| Component | Weight | Source |
|-----------|--------|--------|
| Pronunciation | 40% | Whisper text comparison |
| Tone | 30% | Librosa pitch detection |
| Fluency | 30% | CPM calculation |

---

## API Keys Configuration

### Current .env (needs verification):
```
IFLYTEK_APP_ID=ga8e4cf3
IFLYTEK_API_KEY=8d002d242597976963ba7e41c8f0da73
IFLYTEK_API_SECRET=531014bba3020449ca222f0053028652
```

### To Test iFlytek:
```bash
# Test API connectivity
curl -X POST "https://ise-api-sg.xf-yun.com/v2/ise" \
  -H "Authorization: ..." \
  -d '{"common": {...}, "business": {...}}'
```

---

## Implementation Tasks

### Task 1: Debug iFlytek Connection
- [ ] Add detailed logging to WebSocket connection
- [ ] Test authentication signature
- [ ] Verify API endpoint
- [ ] Handle timeout errors

### Task 2: Create Hybrid Scorer
- [ ] Create `hybrid_scorer.py`
- [ ] Implement score fusion logic
- [ ] Add fallback detection

### Task 3: Update Main App
- [ ] Update `app.py` to use hybrid system
- [ ] Add parallel processing for iFlytek + Whisper
- [ ] Implement detailed feedback generation

### Task 4: Testing
- [ ] Test with iFlytek credentials
- [ ] Test fallback when iFlytek fails
- [ ] Verify scores are reasonable

---

## Expected Results

### With Working iFlytek:
```json
{
  "success": true,
  "transcription": "春天来了",
  "expected": "春天来了",
  "scores": {
    "overall": 85.5,
    "pronunciation": 88.0,
    "tone": 82.0,
    "fluency": 80.0,
    "level": "Level 2-A",
    "grade": "A",
    "pass": true,
    "source": "iflytek",
    "phoneme_details": [
      {"char": "春", "pinyin": "chun1", "score": 90},
      {"char": "天", "pinyin": "tian1", "score": 88},
      {"char": "来", "pinyin": "lai2", "score": 82},
      {"char": "了", "pinyin": "le0", "score": 80}
    ]
  },
  "feedback": "Good pronunciation! Note: '了' (le) should be lighter."
}
```

### With iFlytek Failed (Fallback):
```json
{
  "success": true,
  "transcription": "春天来了",
  "expected": "春天来了",
  "scores": {
    "overall": 78.5,
    "pronunciation": 85.0,
    "tone": 70.0,
    "fluency": 75.0,
    "level": "Level 3-A",
    "source": "local-fallback"
  },
  "feedback": "Good effort! Some characters could be pronounced more clearly."
}
```

---

## Questions to Resolve

1. **Are the iFlytek credentials active?**
   - Need to verify API keys work

2. **Which iFlytek server to use?**
   - Singapore: `ise-api-sg.xf-yun.com`
   - China: `ise-api.xf-yun.com`

3. **What category to use?**
   - `read_syllable` (Section 1)
   - `read_word` (Section 2)  
   - `read_sentence` (Section 3, 4)

---

*Plan Version: 1.0*  
*Last Updated: 2026-03-01*  
*Author: Auto*
