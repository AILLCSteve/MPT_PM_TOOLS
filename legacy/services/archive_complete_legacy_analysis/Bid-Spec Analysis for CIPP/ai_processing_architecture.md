# Multi-Layer AI Processing Architecture for CIPP Analyzer

## Architecture Overview

The AI processing system uses **4 specialized layers**, each with a focused responsibility, to ensure exhaustive and accurate document analysis per promptbase.md requirements.

```
┌─────────────────────────────────────────────────────────────────┐
│                     PDF DOCUMENT (INPUT)                         │
│                    Extracted with page numbers                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: Page-by-Page Extractor                                │
│  Role: Split document into pages with preserved page numbers    │
│  Input: Combined text with <PDF pg #> markers                   │
│  Output: Array of {pageNum, text} objects                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: Question Answering Specialist (3-page windows)        │
│  Role: Analyze 3-page window against ALL 105 questions          │
│  Prompt: Expert CIPP contractor perspective                     │
│  Input: 3 pages of text + 105 questions                         │
│  Output: Findings for each question (answers, citations, pages) │
│  Specialization: Finding answers, identifying citations         │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: Answer Accumulator                                    │
│  Role: APPEND findings to existing answers (never overwrite)    │
│  Data Structure: doc_review_glocom (105-question master list)   │
│  Logic: For each question:                                      │
│    - If answer exists → APPEND new findings                     │
│    - If no answer yet → Create initial answer                   │
│    - Track ALL page numbers where answer found                  │
│  Output: Updated doc_review_glocom                              │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: Unitary Log Compiler/Organizer                        │
│  Role: Display & manage the complete 105-question table         │
│  Responsibilities:                                               │
│    - Display every 3 pages (full table rebuild)                 │
│    - Display every 30 pages (checkpoint progress)               │
│    - Display every 50 pages (pause for user)                    │
│    - Format final unitary log                                   │
│    - Manage footnotes list                                      │
│  Output: Formatted table display in UI                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Layer 1: Page-by-Page Extractor
**Status**: ✅ Already Implemented (PDF Service)

Server returns:
```javascript
{
  pages: [
    { page: 1, text: "..." },
    { page: 2, text: "..." },
    // ...
  ],
  combined_text: "<PDF pg 1>\n...\n<PDF pg 2>\n..."
}
```

### Layer 2: Question Answering Specialist
**Prompt Engineering**:
```
You are an expert CIPP (Cured-In-Place Pipe) contractor analyzing bid specifications.

For the following 3-page window, answer ALL 105 questions from a contractor's perspective.

CRITICAL RULES:
1. Answer from pages 1-3 only (current window)
2. Quote text verbatim with <PDF pg #> markers
3. If no answer found in THIS window, respond "Not found in pages 1-3"
4. Include inline citations (section titles, clause numbers)
5. Bold critical terms in answers
6. If standards/laws referenced, note them for web search

FORMAT: Return JSON with exact structure specified.
```

**Specialization**: This layer ONLY finds answers. It doesn't know about accumulation.

### Layer 3: Answer Accumulator
**JavaScript Logic**:
```javascript
class AnswerAccumulator {
    constructor() {
        this.doc_review_glocom = this.initializeAllQuestions(); // All 105 questions
        this.doc_footnotes = [];
    }

    initializeAllQuestions() {
        // Create array with all 105 questions, answers initially "Not yet found"
        return ALL_105_QUESTIONS.map((q, i) => ({
            section_header: q.section,
            number: i + 1,
            question: q.text,
            answer: "Not yet found",
            pdf_pages: [],
            inline_citations: [],
            footnotes: []
        }));
    }

    accumulateFindings(questionNumber, newFindings) {
        const question = this.doc_review_glocom[questionNumber - 1];

        if (newFindings.answer !== "Not found in pages X-Y") {
            if (question.answer === "Not yet found") {
                // First answer found
                question.answer = newFindings.answer;
            } else {
                // APPEND to existing answer
                question.answer += "\n\n" + newFindings.answer;
            }

            // Accumulate page numbers
            question.pdf_pages.push(...newFindings.pages);
            question.inline_citations.push(...newFindings.citations);
        }
    }
}
```

**Key Feature**: NEVER overwrites. ALWAYS appends.

### Layer 4: Unitary Log Compiler/Organizer
**Responsibilities**:

1. **Every 3 Pages**: Display full 105-row table
2. **Every 30 Pages**: Checkpoint display with progress
3. **Every 50 Pages**: Pause and ask user
4. **Final**: Complete formatted unitary log

**Display Format** (per promptbase.md):
```
| Section Header | # | Question | Answer | PDF Page | Inline Citation | Footnote |
|----------------|---|----------|--------|----------|-----------------|----------|
| Project Info   | 1 | What... | Answer | 1, 5, 12 | Section 2.1    | ^1       |
```

---

## Processing Flow

### Initialization
1. Load PDF → Extract pages (Layer 1)
2. Initialize doc_review_glocom with all 105 questions (Layer 3)
3. Initialize Unitary Log Compiler (Layer 4)

### Main Loop (3-page windows)
```javascript
for (let pageIndex = 0; pageIndex < totalPages; pageIndex += 3) {
    // Get 3-page window
    const windowPages = pages.slice(pageIndex, pageIndex + 3);
    const windowText = windowPages.map(p => p.text).join("\n\n");

    // Layer 2: Analyze this window
    const findings = await questionAnsweringSpecialist.analyze(
        windowText,
        ALL_105_QUESTIONS,
        windowPages.map(p => p.page)
    );

    // Layer 3: Accumulate findings
    for (const finding of findings) {
        answerAccumulator.accumulateFindings(
            finding.questionNumber,
            finding
        );
    }

    // Layer 4: Display (every 3 pages)
    unitaryLogCompiler.displayCurrentState(
        answerAccumulator.doc_review_glocom,
        answerAccumulator.doc_footnotes
    );

    // Layer 4: Checkpoint every 30 pages
    if ((pageIndex + 3) % 30 === 0) {
        unitaryLogCompiler.displayCheckpoint(pageIndex + 3);
    }

    // Layer 4: Pause every 50 pages
    if ((pageIndex + 3) % 50 === 0) {
        await unitaryLogCompiler.pauseForUser();
    }
}
```

---

## Advantages of Layered Architecture

### 1. Separation of Concerns
- Each layer has ONE job
- Easy to test and debug
- Clear responsibilities

### 2. Better AI Outputs
- Layer 2 focuses ONLY on finding answers (specialized prompt)
- Layer 4 focuses ONLY on formatting (specialized prompt)
- Specialized prompts = better results

### 3. Maintainability
- Can improve one layer without affecting others
- Can swap AI models for specific layers
- Can add new layers (e.g., citation validator)

### 4. Guarantees Exhaustive Scanning
- Layer 2 processes EVERY 3-page window
- Layer 3 ensures ALL 105 questions tracked
- Layer 4 ensures ALL 105 questions displayed

### 5. Answer Accumulation
- Layer 3 explicitly handles APPEND logic
- No risk of overwriting earlier answers
- All page numbers preserved

---

## Error Handling

### Layer 2 Failures
- Retry with exponential backoff
- Log which window failed
- Continue to next window
- User can review partial results

### Layer 3 Failures
- Never lose accumulated data
- Checkpoint state to localStorage every 30 pages
- Can resume from last checkpoint

### Layer 4 Failures
- Display can be regenerated from doc_review_glocom
- No data loss

---

## Future Enhancements

### Additional Layers
- **Layer 2.5: Citation Validator** - Verify citations exist in document
- **Layer 3.5: Duplicate Detector** - Identify redundant answers
- **Layer 4.5: Footnote Researcher** - Auto-search standards/laws on web

### Performance Optimization
- Parallel processing of multiple 3-page windows
- Caching of AI responses
- Progressive rendering of table

---

## Alignment with promptbase.md

✅ **3-page windowing**: Layer 2 processes in 3-page chunks
✅ **ALL 105 questions**: Layer 3 maintains complete list
✅ **Accumulation**: Layer 3 explicitly APPENDs
✅ **Page number preservation**: Layer 1 provides, Layer 3 tracks
✅ **Display every 3 pages**: Layer 4 handles
✅ **Display every 30 pages**: Layer 4 checkpoint
✅ **Pause every 50 pages**: Layer 4 user interaction
✅ **Unitary log**: Layer 4 final compilation
✅ **Exhaustive scanning**: Loop processes ALL pages for ALL questions

---

**Architecture Version**: 1.0
**Last Updated**: 2025-11-01
**Status**: Ready for Implementation
