# BoDongGua Audio Analysis System - Rebuild Plan

## Overview
Rebuild the audio analysis system from scratch with iFlytek ISE API as the primary (and only required) engine, with optional librosa enhancement.

---

## 1. Current System Removal

### Files to Remove/Clean:
- `BDG_backend/tone-analysis/services/iflytek_ise.py` - Replace entirely
- `BDG_backend/tone-analysis/services/audio_preprocessor.py` - Rebuild
- `BDG_backend/tone-analysis/app.py` - Rebuild

### Keep:
- Frontend components (may need alignment)

---

## 2. PSC Test Alignment

### PSC (Putonghua Shuiping Ceshi) Test Format:
| Part | Type | Weight | Description |
|------|------|--------|-------------|
| 1 | Reading Aloud (朗读) | 30% | Read passage, tests pronunciation & tones |
| 2 | Phonetic Skills (选择判断) | 25% | Multiple choice on tones/phonetics |
| 3 | Listening (听力理解) | 25% | Audio comprehension |
| 4 | Speaking (命题说话) | 20% | Speak on given topic |

### Current UI vs PSC Alignment:
- **MockTest.tsx** - Appears to test reading aloud ✓
- Need to add: phonetics questions, listening practice
- Current scoring: needs PSC-aligned output

---

## 3. New Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Frontend   │────►│   Backend    │────►│   Python      │
│  (React)    │     │  (Node.js)  │     │   (Flask)    │
└─────────────┘     └──────────────┘     └───────────────┘
       │                   │                     │
       │                   │                     │
       ▼                   ▼                     ▼
   Upload UI         Route /api/          iFlytek ISE
   Record Audio      audio/analyze        WebSocket
   Display Results   Validate             Process Audio
                                        Return Scores
```

---

## 4. Implementation Phases

### Phase 1: iFlytek ISE Only (Priority)
- [ ] Clean up and rebuild `iflytek_ise.py`
  - Proper WebSocket handling
  - Correct parameters for Chinese pronunciation
  - Error handling with user-friendly messages
- [ ] Rebuild `app.py`
  - Clean endpoints
  - Proper audio preprocessing
  - No fallback
- [ ] Test with iFlytek API

### Phase 2: Optional Librosa Enhancement
- [ ] Add librosa for local audio analysis
- [ ] Use as enhancement only (not required)
- [ ] Combine with iFlytek results

### Phase 3: PSC UI Alignment
- [ ] Review MockTest component
- [ ] Add PSC-style questions
- [ ] Align scoring with PSC standards

---

## 5. iFlytek ISE Parameters (Chinese Pronunciation)

```python
params = {
    'common': {'app_id': APP_ID},
    'business': {
        'sub': 'ise',        # Intelligent Speech Evaluation
        'ent': 'cn_vip',     # Chinese VIP
        'category': 'read_sentence',  # For reading aloud
        'rstcd': 'utf8',
        'tte': 'utf-8',
        'text': reference_text
    },
    'data': {'status': 0}
}
```

### Audio Requirements:
- Format: PCM 16kHz mono
- Encoding: 16-bit
- Quality: Clear voice, low background noise

---

## 6. Expected iFlytek Response

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xml_result>
    <read_sentence>
        <read_sentence 
            total_score="85.5"
            pronunciation_score="88.0"
            fluency_score="82.0"
            tone_score="86.0"
            is_rejected="false">
        </read_sentence>
    </read_sentence>
</xml_result>
```

---

## 7. Next Steps

1. **Remove old code** - Clean up tone-analysis folder
2. **Rebuild iflytek_ise.py** - New clean implementation
3. **Rebuild app.py** - Flask API with proper structure
4. **Test iFlytek** - Verify API works
5. **Align UI** - Check MockTest vs PSC requirements

---

## Notes
- iFlytek console shows API is being called successfully
- Issue: Audio quality causes rejection (error 28689)
- Solution: Ensure audio is clear before sending
- No fallback - if iFlytek fails, return error to user
