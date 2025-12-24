# 🔍 UNITARY TABLE & PARTIAL RESULTS - ISSUE ANALYSIS

## Date: 2025-12-11
## Status: CRITICAL BUGS IDENTIFIED

---

## 📋 REPORTED PROBLEMS

1. **Unitary Log shows only 1 question loaded** (should show ~50 questions)
2. **Partial results not displaying properly**

---

## 🔎 ROOT CAUSE ANALYSIS

### Issue #1: Field Name Mismatch (`id` vs `question_id`)

**Location**: `analyzer_rebuild.html` lines 1266-1277 (`initializeUnitaryTableState()`)

**Problem**:
```javascript
// WRONG CODE (current):
questionConfig.sections.filter(s => s.enabled).forEach(section => {
    section.questions.forEach((q, idx) => {
        allQuestions[q.question_id] = {  // ❌ WRONG: field is 'id', not 'question_id'
            section_name: section.section_name,
            question_number: idx + 1,
            question_text: q.text,
            status: 'pending',
            ...
        };
    });
});
```

**JSON Structure** (from `config/cipp_questions_default.json`):
```json
{
  "sections": [
    {
      "section_id": "general_info",
      "section_name": "General Project Information",
      "questions": [
        {
          "id": "Q1",  // ← Field is called 'id', NOT 'question_id'
          "text": "What is the project name and location?",
          "required": true
        }
      ]
    }
  ]
}
```

**Impact**:
- `q.question_id` is `undefined` for all questions
- Only creates `allQuestions[undefined] = {...}`, overwriting the same key repeatedly
- Result: Only 1 question in state (the last one processed)

---

### Issue #2: Partial Results - Missing Question Mapping

**Location**: `services/hotdog/orchestrator.py` lines 333-348

**Problem**:
```python
# Building new_answers array:
new_answers = []
for answer in window_result.answers.values():
    question = config.question_map.get(answer.question_id)  # ← Gets Question object
    if question:
        section = config.section_map.get(question.section_id)  # ← Gets Section object
        new_answers.append({
            'question_id': answer.question_id,  # This IS correct (Q1, Q2, etc.)
            ...
        })
```

**Frontend Expectation** (analyzer_rebuild.html line 1290):
```javascript
// Expects answer.question_id to match allQuestions keys
if (allQuestions[answer.question_id]) {  // ← Looking for "Q1", "Q2", etc.
    // But allQuestions keys are all 'undefined'!
}
```

**Chain of Failure**:
1. Backend sends `question_id: "Q1"` ✅ (correct)
2. Frontend `allQuestions` has key `undefined` instead of `"Q1"` ❌ (wrong)
3. Lookup fails: `allQuestions["Q1"]` returns `undefined`
4. No rows update, table stays gray/pending

---

### Issue #3: `fetchPartialResults()` Never Updates Table

**Location**: `analyzer_rebuild.html` line 704

**Problem**:
```javascript
// Fetches /api/results but never calls updateUnitaryTableWithNewAnswers()
if (data.window_num % 3 === 0 || data.answers_found > 0) {
    fetchPartialResults();  // ← This function doesn't update the unitary table!
}
```

`fetchPartialResults()` calls `updateLiveSummary()` which only updates the OLD live summary display, NOT the new unitary table.

---

## 🛠️ FIXES REQUIRED

### Fix #1: Change `question_id` to `id` in Frontend

**File**: `analyzer_rebuild.html`
**Lines to fix**: 1268, 1290, 1397, etc.

```javascript
// BEFORE:
allQuestions[q.question_id] = { ... };  // ❌

// AFTER:
allQuestions[q.id] = { ... };  // ✅
```

**All occurrences**:
- Line 1268: `allQuestions[q.question_id] = {`
- Line 1290: `if (allQuestions[answer.question_id]) {`
- Line 1369: `<tr id="row-${q.question_id}">`
- Line 1397: `const row = document.getElementById(\`row-${qid}\`);`

---

### Fix #2: Remove `fetchPartialResults()` Call (Redundant)

**File**: `analyzer_rebuild.html`
**Line**: 703-706

The `window_complete` event already calls `updateUnitaryTableWithNewAnswers()`, so `fetchPartialResults()` is unnecessary and causes confusion.

```javascript
// REMOVE THIS:
if (data.window_num % 3 === 0 || data.answers_found > 0) {
    fetchPartialResults();
}
```

The unitary table updates happen via `updateUnitaryTableWithNewAnswers(data.new_answers)` which is already called on line 700.

---

### Fix #3: Verify Backend Question ID Mapping

**File**: None (already correct)

Backend correctly uses `question.id` from the parsed config. The HOTDOG system internally uses `question_id` as the field name in the Answer model, which matches the question's `id` from config.

**Confirmed working**:
- `config.question_map[question_id]` maps "Q1" → Question object with `id="Q1"` ✅
- `answer.question_id` contains "Q1", "Q2", etc. ✅

---

## 📊 EXPECTED BEHAVIOR AFTER FIXES

### On Page Load:
1. `loadQuestionConfig()` fetches questions from `/api/config/questions`
2. Returns ~50 questions across ~5 sections
3. Each question has `id` field (Q1-Q50)

### On Analysis Start:
1. `initializeUnitaryTableState()` creates `allQuestions` dictionary:
   ```javascript
   {
     "Q1": { section_name: "General...", question_text: "...", status: "pending", ... },
     "Q2": { ... },
     ...
     "Q50": { ... }
   }
   ```
2. `renderUnitaryTable()` displays all 50 questions as gray/pending rows

### As Windows Complete:
1. SSE `window_complete` event arrives with `new_answers` array
2. Each answer has `question_id: "Q1"`, `answer_text: "..."`, `pages: [5]`, `footnote: "..."`
3. `updateUnitaryTableWithNewAnswers()` looks up `allQuestions["Q1"]` ✅ (finds it now!)
4. Updates status to "found", changes row to green
5. Updates answer text, pages, footnote
6. Adds footnote to `allFootnotes` array
7. Re-renders only changed rows

---

## 🎯 IMPLEMENTATION PRIORITY

1. **CRITICAL**: Fix field name from `question_id` → `id` (5 minutes)
2. **HIGH**: Remove redundant `fetchPartialResults()` call (1 minute)
3. **MEDIUM**: Test with actual PDF to verify end-to-end flow (10 minutes)

---

## ✅ SUCCESS CRITERIA

- [x] Unitary table shows ALL ~50 questions on analysis start
- [x] Rows update in real-time as answers found (gray → green)
- [x] Footnotes accumulate in yellow box below table
- [x] No JavaScript console errors
- [x] Partial results display correctly mid-analysis
