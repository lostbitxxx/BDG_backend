# BoDongGua - PSC Aligned Audio Analysis System

## 1. PSC Test Structure (Official)
Reference: https://cle.hkust.edu.hk/tests/psc/psc

| Part | Type | Weight | Status |
|------|------|--------|--------|
| **1. 朗读 (Reading Aloud)** | Read passage aloud | 30% | ✅ Implemented |
| **2. 判断题** | Tone/phonetic judgment | 25% | ⚠️ Needs work |
| **3. 听力 (Listening)** | Audio comprehension | 25% | ⚠️ Needs work |
| **4. 说话 (Speaking)** | Topic speaking | 20% | ⚠️ Needs work |

## 2. Current Frontend Status

### MockTest.tsx
- ✅ Section 4 (Reading Aloud) - Main focus
- ✅ PSC scoring calculation
- ✅ Grade/Level mapping
- ✅ Audio recording

### Questions.ts  
- ✅ Section 1: Single characters (100 chars)
- ✅ Section 2: Choice questions
- ✅ Section 4: Reading passages

## 3. Backend Structure

### Current Endpoints:
- `/api/audio/analyze` - Main analysis (iFlytek)
- Audio upload → S3 → iFlytek → Response

### Issues:
- iFlytek WebSocket closing unexpectedly
- Need alternative approach

## 4. Solution: Dual Engine Approach

### Primary: iFlytek ISE (for Reading Aloud)
- Scores: pronunciation, fluency, tone, overall
- Works for Section 4 (朗读)

### Fallback: Local Audio Analysis
- Use Web Speech API or similar for basic scoring
- Or simple audio metrics (duration, volume, etc.)

## 5. Implementation Plan

### Phase 1: Fix iFlytek Integration
- [ ] Debug why WebSocket closes
- [ ] Try different audio format
- [ ] Check iFlytek console for errors

### Phase 2: Backend API
- [ ] `/analyze` endpoint with proper error handling
- [ ] Audio preprocessing (convert to correct format)
- [ ] Return PSC-aligned scores

### Phase 3: Frontend Alignment
- [ ] Display PSC levels correctly
- [ ] Show individual scores (pronunciation, fluency, tone)
- [ ] Error handling for users

## 6. API Response Format (PSC Aligned)

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
  "test_type": "PSC Reading Aloud (朗读)"
}
```

## 7. Next Steps

1. First: Test iFlytek with simple audio
2. Second: If iFlytek fails, use fallback
3. Third: Ensure frontend displays correctly
4. Fourth: Test end-to-end

---

*Plan created: 2026-03-02*
