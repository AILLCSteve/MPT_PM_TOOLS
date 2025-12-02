# COMPLETE REWRITE REQUIREMENTS

## Phase 1: Understanding Legacy System (Reference Only)

### UI Components That Must Be Preserved:

#### 1. Navigation & Branding
- MPT navbar with logo (/shared/assets/images/logo.png)
- Title: "CIPP Bid-Spec Analyzer"
- Home link
- Blue gradient color scheme (#5b7fcc)

#### 2. Document Upload Section
- File input (drag-and-drop enabled)
- Supports: PDF, TXT, DOCX, RTF
- Shows: filename, file size
- "Load Test Document" button

#### 3. Question Configuration Section
- 10 question sections (toggleable)
- Each shows: section name, question count, enabled/disabled state
- Active question counter
- Context Guardrails textarea
- "Manage Questions" button
- "Add Custom Section" button
- "Export Questions" button

#### 4. Analysis Controls
- "Start Analysis (Pass 1)" button
- "Run Second Pass" button (conditional)
- "Stop Analysis" button
- "Clear Results" button
- Export dropdown menu (6 formats)

#### 5. Activity Log
- Timestamped entries
- Color-coded by type (info, success, error, warning)
- Auto-scroll to bottom
- "Export Log" button
- "Clear Log" button

#### 6. Progress Tracker
- Percentage bar
- Status text
- Shows/hides dynamically

#### 7. Results Display
- Sections with questions/answers
- Footnotes section
- Statistics dashboard
- Live unitary log display

#### 8. Settings Modal
- API key management (from environment)
- Test API connection button
- Model selection
- Other configuration

#### 9. Debug Panel (Collapsible)
- Shows technical details
- Can be hidden

### Backend Functionality That Must Work:

#### 1. File Upload Flow
**Intended:** User uploads file → Save to temp → Return filepath
**Current Issue:** Unknown (need to test)

#### 2. SSE Progress Stream
**Intended:** Client connects → Receives real-time events during analysis
**Current Issue:** Events not appearing in activity log

#### 3. HOTDOG AI Analysis
**Intended:**
- Layer 0: Extract PDF pages
- Layer 1: Load questions config
- Layer 2: Generate expert personas
- Layer 3: Process windows with multi-expert
- Layer 4: Accumulate answers
- Layer 5: Track token usage
- Layer 6: Compile output

**Current Issue:** Analysis runs but no live feedback

#### 4. Progress Events
**Intended Events:**
1. `connected` - SSE stream connected
2. `document_ingested` - PDF extracted (pages, windows)
3. `config_loaded` - Questions loaded
4. `expert_generated` - Expert persona created
5. `window_processing` - Window analysis starting
6. `experts_dispatched` - Experts analyzing
7. `experts_complete` - Expert analysis done
8. `window_complete` - Window finished (includes unitary log)
9. `progress_milestone` - Periodic updates
10. `done` - Analysis complete
11. `error` - Error occurred

**Current Issue:** Events emitted but not displayed

#### 5. Second Pass Analysis
**Intended:** Analyze unanswered questions with enhanced scrutiny
**Current Issue:** Unknown

#### 6. Export Functionality
**Intended:** 6 export formats (Excel charts, Excel table, CSV, HTML, Markdown, JSON)
**Current Issue:** "Analyzer never started" error

#### 7. Stop Analysis Button
**Intended:** Cancel ongoing analysis
**Current Issue:** Doesn't work

### Architecture Issues Identified:

#### Problem 1: Blocking Worker Thread
- `loop.run_until_complete()` blocks entire worker
- Even with gevent, this prevents SSE from yielding
- Need: True async execution that doesn't block

#### Problem 2: Event Delivery Chain
- Orchestrator emits → Callback queues → SSE yields → Frontend receives
- Somewhere in this chain, events are lost
- Need: Verify each step actually works

#### Problem 3: Logger Display Logic
**Working Examples:**
```javascript
Logger.success(`✅ File uploaded: ${pdfPath}`);  // WORKS
Logger.info('✅ Progress stream connected');     // WORKS
```

**Not Working:**
```javascript
// SSE events - should trigger but don't display
Logger.info(`📄 Extracted ${data.total_pages} pages`);
```

Need: Understand why manual Logger calls work but SSE-triggered ones don't

---

## Phase 2: Rewrite Plan

### Step 1: Create Clean Backend (app_new.py)
- Simple Flask app
- No accumulated patches
- Clear SSE implementation that actually works
- Proper async handling for HOTDOG

### Step 2: Test SSE Independently
- Simple test endpoint that emits events every second
- Verify frontend receives them
- Verify Logger displays them
- **Don't move forward until this works**

### Step 3: Integrate HOTDOG Properly
- Run in background without blocking
- Emit progress events that actually reach frontend
- Verify each event appears in activity log
- **Don't move forward until this works**

### Step 4: Rebuild Frontend (cipp_analyzer_clean.html)
- Start from scratch
- Copy ONLY working UI components
- Rewrite ALL JavaScript logic cleanly
- Test each button/function individually

### Step 5: Implement All Features
- Upload
- Analysis
- Stop button
- Second pass
- Export (all 6 formats)
- Settings
- Question management

### Step 6: Integration Testing
- Test complete workflow end-to-end
- Verify all buttons work
- Verify all displays update
- Fix any issues

---

## Phase 3: Key Design Decisions

### For SSE to Work:
**Option A: Background Task Queue (Celery/RQ)**
- Analysis runs in separate worker process
- Progress updates posted to Redis
- SSE stream reads from Redis
- **Pro:** True separation, proven pattern
- **Con:** Requires Redis

**Option B: Threading with Queue**
- Analysis runs in separate thread
- Progress updates posted to queue
- SSE stream reads from queue
- **Pro:** Simple, no external dependencies
- **Con:** Python GIL limitations

**Option C: Gevent Greenlets (Done Right)**
- Analysis runs in greenlet
- SSE runs in greenlet
- Cooperative multitasking
- **Pro:** Single process, works with current setup
- **Con:** Need to do it correctly (not just patch)

### For Logger to Work:
**Pattern from working code:**
```javascript
// Upload handler - line 5689
Logger.success(`✅ File uploaded: ${pdfPath}`);

// SSE connection - line 5711
Logger.info('✅ Progress stream connected');
```

**Must replicate exactly in SSE event handlers**

---

## Next Steps:

1. Create `app_new.py` from scratch
2. Create simple test SSE endpoint
3. Verify it works in browser
4. Then add HOTDOG integration
5. Then rebuild frontend
6. Test everything

**DO NOT PROCEED TO NEXT STEP UNTIL CURRENT STEP WORKS**
