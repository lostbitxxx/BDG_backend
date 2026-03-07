# Full Test Results Page (Test GPA & Summary)

After the user completes one full PSC test (all 5 sections), the app should show a **results page** with the test GPA, total score, level, and per-section breakdown.

## Backend API (already implemented)

### 1. Complete the test (call when user finishes section 5)

**POST** `/api/test/:sessionId/complete`

No body required. Returns:

```json
{
  "success": true,
  "completedSections": [1, 2, 3, 4, 5],
  "result": {
    "totalScore": 87.5,
    "level": "二級乙等",
    "grade": "B",
    "pass": true,
    "testGPA": 3.0,
    "sectionGrades": { "1": "A", "2": "B+", "3": "B", "4": "B+", "5": "B" },
    "sectionGPAs": { "1": 4, "2": 3, "3": 3, "4": 3, "5": 3 },
    "sections": {
      "1": { "finalScore": 9.5, "maxScore": 10, ... },
      "2": { "finalScore": 18, "maxScore": 20, ... },
      "3": { "finalScore": 8.5, "maxScore": 10, ... },
      "4": { "finalScore": 26, "maxScore": 30, ... },
      "5": { "finalScore": 26, "maxScore": 30, ... }
    },
    "timeUsed": [120, 90, 100, 180, 150],
    "timeoutOccurred": [false, false, false, false, false]
  }
}
```

### 2. Get result later (e.g. if user navigates back to results)

**GET** `/api/test/:sessionId/result`

Returns the same `result` object. Requires `session.status === 'completed'`.

---

## What the Results Page Should Show

1. **Test GPA** – `result.testGPA` (e.g. 3.0), prominently.
2. **Total score** – `result.totalScore` (e.g. 87.5) and **Level** – `result.level` (e.g. 二級乙等) and **Grade** – `result.grade` (e.g. B).
3. **Pass / Fail** – `result.pass` (true if totalScore ≥ 60).
4. **Per-section breakdown** (optional but useful):
   - Section 1: score, grade, GPA
   - Section 2: score, grade, GPA
   - … same for sections 3, 4, 5.

Section names (for labels) can be fetched from **GET** `/api/test/sections` or hardcoded:

| Section | name (中文)   | nameEn                |
|---------|----------------|------------------------|
| 1       | 讀單音節字     | Read Single Characters |
| 2       | 讀多音節詞語   | Read Polysyllabic Words |
| 3       | 選擇判斷       | Choice & Judgment      |
| 4       | 朗讀短文       | Reading Passage        |
| 5       | 命題說話       | Topic Speaking         |

---

## Frontend Flow

1. When the user clicks **Submit test** / **Complete** after section 5, call **POST** `/api/test/:sessionId/complete`.
2. Use the response `result` (or store it in state/context).
3. **Navigate to a dedicated “Test Results” route** (e.g. `/test-results/:sessionId` or `/practice/full-test/results`) and render the results page using `result.testGPA`, `result.totalScore`, `result.level`, `result.sectionGrades`, etc.
4. Optionally, on that route, call **GET** `/api/test/:sessionId/result` if you only have `sessionId` (e.g. after refresh).

---

## Summary

- **Backend:** Already returns `testGPA`, `sectionGPAs`, `sectionGrades`, `totalScore`, `level`, `grade`, `pass`, and per-section scores in **POST** `/api/test/:sessionId/complete` and **GET** `/api/test/:sessionId/result`.
- **Frontend:** Add a **Full Test Results** page that appears after completing a full set, and display the test GPA and the rest of the summary as above.
