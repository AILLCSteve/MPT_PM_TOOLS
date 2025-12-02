# COMPLETE REBUILD SPECIFICATION

## VERIFIED: SSE Works in Isolation ✅
Test showed SSE events flow correctly when backend sends them.
Problem is NOT SSE itself, it's how we're integrating it.

---

## PART 1: BACKEND ARCHITECTURE (app_clean.py)

### Design Decision: Use Threading (Not Gevent)
**Why:** Simpler, proven, no monkey patching needed
**How:**
1. Main Flask thread handles requests
2. Analysis runs in separate Python thread
3. Thread posts progress to Queue
4. SSE endpoint reads from Queue

### Backend Structure:

```python
import threading
import queue
from flask import Flask, Response, stream_with_context
import json

# Global progress queues (session_id -> Queue)
progress_queues = {}

# SSE Endpoint (SIMPLE - like test that worked)
@app.route('/api/progress/<session_id>')
def progress_stream(session_id):
    def generate():
        q = progress_queues.get(session_id)
        if not q:
            q = queue.Queue()
            progress_queues[session_id] = q

        # Send connection event
        yield f"data: {json.dumps({'event': 'connected'})}\n\n"

        while True:
            try:
                event_type, data = q.get(timeout=15)

                if event_type == 'done':
                    yield f"data: {json.dumps({'event': 'done'})}\n\n"
                    break

                yield f"data: {json.dumps({'event': event_type, **data})}\n\n"

            except queue.Empty:
                yield ": keepalive\n\n"

    return Response(stream_with_context(generate()),
                    mimetype='text/event-stream')

# Analysis Endpoint (NON-BLOCKING)
@app.route('/api/analyze', methods=['POST'])
def analyze():
    session_id = request.json['session_id']
    pdf_path = request.json['pdf_path']

    # Create progress queue
    q = queue.Queue()
    progress_queues[session_id] = q

    # Define progress callback
    def progress_callback(event_type, data):
        q.put((event_type, data))

    # Run analysis in background thread
    def run_analysis():
        orchestrator = HotdogOrchestrator(progress_callback=progress_callback)
        result = orchestrator.analyze_document(pdf_path)
        q.put(('done', {}))
        return result

    # Start thread
    thread = threading.Thread(target=run_analysis)
    thread.daemon = True
    thread.start()

    # Return immediately (don't wait for analysis)
    return jsonify({'success': True, 'session_id': session_id})
```

### Key Points:
1. SSE endpoint is SIMPLE (like working test)
2. Analysis runs in thread (doesn't block)
3. Progress callback just does `q.put()`
4. Frontend receives events in real-time

---

## PART 2: FRONTEND ARCHITECTURE (cipp_analyzer_clean.html)

### UI Components (ALL PRESERVED):

#### 1. MPT Navbar
```html
<nav class="mpt-navbar">
    <div class="logo-container">
        <img src="/shared/assets/images/logo.png">
        <span>CIPP Bid-Spec Analyzer</span>
    </div>
    <a href="/">← Home</a>
</nav>
```

#### 2. Document Upload Section
```html
<div class="section">
    <h3>📄 Document Upload</h3>
    <div class="file-upload" id="fileUpload">
        <input type="file" id="fileInput" accept=".pdf,.txt,.docx,.rtf">
        <p>Click to select file or drag and drop</p>
    </div>
    <div id="fileInfo">
        <p>Selected: <span id="fileName"></span></p>
        <p>Size: <span id="fileSize"></span></p>
    </div>
    <button class="btn btn-test" onclick="loadTestDocument()">📋 Load Test</button>
</div>
```

#### 3. Question Configuration
```html
<div class="section">
    <h3>❓ Question Configuration</h3>
    <div id="questionSections"></div>
    <p>Active: <span id="activeQuestionCount">0</span> questions</p>

    <textarea id="contextGuardrails" placeholder="Context guardrails..."></textarea>

    <button onclick="showQuestionManager()">📝 Manage Questions</button>
    <button onclick="addQuestionSection()">➕ Add Custom Section</button>
    <button onclick="exportQuestions()">📤 Export Questions</button>
    <button onclick="showSettings()">⚙️ Settings</button>
</div>
```

#### 4. Analysis Controls
```html
<div class="section">
    <h3>🎯 Analysis Controls</h3>

    <button id="analyzeBtn" onclick="startAnalysis()">🚀 Start Analysis</button>
    <button id="secondPassBtn" onclick="runSecondPass()">🔍 Second Pass</button>
    <button id="stopBtn" onclick="stopAnalysis()">⏹️ Stop</button>
    <button onclick="clearResults()">🗑️ Clear</button>

    <div class="btn-group">
        <button id="exportBtn" onclick="showExportMenu()">📊 Export ▼</button>
        <div id="exportMenu">
            <button onclick="exportExcelDashboard()">📊 Excel Dashboard</button>
            <button onclick="exportResults('excel-simple')">✨ Excel Table</button>
            <button onclick="exportResults('csv')">📄 CSV</button>
            <button onclick="exportResults('html')">🌐 HTML</button>
            <button onclick="exportResults('markdown')">📝 Markdown</button>
            <button onclick="exportResults('json')">📋 JSON</button>
        </div>
    </div>
</div>
```

#### 5. Activity Log
```html
<div id="logContainer">
    <h4>Activity Log</h4>
    <div id="logContent"></div>
    <button onclick="exportLog()">💾 Export</button>
    <button onclick="clearLog()">🗑️ Clear</button>
</div>
```

#### 6. Progress Tracker
```html
<div id="progressContainer">
    <div id="progressFill"></div>
    <span id="progressText"></span>
</div>
```

#### 7. Results Display
```html
<div id="resultsSection">
    <h3>Results</h3>
    <div id="resultsContent"></div>
    <div id="statisticsContent"></div>
</div>
```

#### 8. Settings Modal
```html
<div id="settingsModal" class="modal">
    <div class="modal-content">
        <button class="close-btn" onclick="hideSettings()">×</button>
        <h2>Settings</h2>

        <label>API Key Status</label>
        <input id="apiKeyDisplay" readonly>
        <button onclick="testApiConnection()">🔗 Test Connection</button>

        <button onclick="saveSettings()">💾 Save</button>
        <button onclick="hideSettings()">❌ Close</button>
    </div>
</div>
```

### JavaScript Structure (CLEAN):

```javascript
// Simple Logger (EXACTLY like working code)
class Logger {
    static log(message, type = 'info') {
        const time = new Date().toLocaleTimeString();
        const logContainer = document.getElementById('logContent');
        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;
        entry.textContent = `[${time}] ${message}`;
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    static info(msg) { this.log(msg, 'info'); }
    static success(msg) { this.log(msg, 'success'); }
    static error(msg) { this.log(msg, 'error'); }
    static warning(msg) { this.log(msg, 'warning'); }
}

// Progress Tracker
class ProgressTracker {
    static show() {
        document.getElementById('progressContainer').style.display = 'block';
    }
    static hide() {
        document.getElementById('progressContainer').style.display = 'none';
    }
    static update(percent, text) {
        document.getElementById('progressFill').style.width = `${percent}%`;
        document.getElementById('progressText').textContent = text;
    }
}

// Analysis Flow (SIMPLE)
async function startAnalysis() {
    const file = document.getElementById('fileInput').files[0];
    if (!file) {
        Logger.error('No file selected');
        return;
    }

    Logger.info('Starting analysis...');

    // 1. Upload file
    const formData = new FormData();
    formData.append('file', file);
    const uploadResp = await fetch('/api/upload', {
        method: 'POST',
        body: formData
    });
    const uploadData = await uploadResp.json();

    Logger.success(`File uploaded: ${uploadData.filepath}`);

    // 2. Connect to SSE BEFORE starting analysis
    const sessionId = 'session_' + Date.now();
    const eventSource = new EventSource(`/api/progress/${sessionId}`);

    eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);

        // Route events to Logger (SIMPLE)
        if (data.event === 'connected') {
            Logger.success('Progress stream connected');
        }
        else if (data.event === 'document_ingested') {
            Logger.info(`Extracted ${data.total_pages} pages`);
        }
        else if (data.event === 'window_processing') {
            Logger.info(`Processing window ${data.window_num}/${data.total_windows}`);
        }
        else if (data.event === 'window_complete') {
            Logger.success(`Window ${data.window_num} complete`);
        }
        else if (data.event === 'done') {
            Logger.success('Analysis complete!');
            eventSource.close();
        }
    };

    // 3. Start analysis (returns immediately)
    const analyzeResp = await fetch('/api/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            session_id: sessionId,
            pdf_path: uploadData.filepath,
            context_guardrails: document.getElementById('contextGuardrails').value
        })
    });

    const analyzeData = await analyzeResp.json();
    Logger.info('Analysis started in background');
}
```

---

## PART 3: BUILD SEQUENCE

### Stage 1: Minimal Working SSE ✅ DONE
- Created test_sse_simple.html
- Created app_test_sse.py
- Verified SSE works

### Stage 2: Backend with Threading (NEXT)
- Create app_clean.py
- Implement /api/upload
- Implement /api/progress/<id>
- Implement /api/analyze with threading
- Test SSE events appear

### Stage 3: Integrate HOTDOG
- Modify orchestrator to NOT block
- Use progress_callback correctly
- Verify all events emit

### Stage 4: Frontend Complete UI
- Create cipp_analyzer_clean.html
- All UI components
- All buttons
- All functionality

### Stage 5: Stop Button
- Implement thread cancellation
- Test stop works

### Stage 6: Second Pass
- Implement second pass endpoint
- Test works

### Stage 7: Export
- Implement all 6 export formats
- Test each one

### Stage 8: Settings & Modals
- Question manager
- Settings modal
- All modals work

---

## CRITICAL LEARNING

**What worked in test:**
```python
# Backend sends
yield f"data: {json.dumps({'event': 'test', 'message': 'Test 1'})}\n\n"

# Frontend receives and displays
Logger.info('Test 1');  // THIS WORKED!
```

**What to replicate:**
- Exact same SSE format
- Exact same Logger calls
- Don't overcomplicate!

---

## NEXT STEP

Build app_clean.py with threading-based architecture.
Test it works.
Then build frontend.
Then integrate HOTDOG.

**DO NOT MOVE TO NEXT STAGE UNTIL CURRENT STAGE WORKS**
