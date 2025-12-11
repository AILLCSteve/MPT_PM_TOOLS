# CIPP Analyzer Frontend - Exhaustive Inventory & Technical Blueprint

**Document Version:** 1.0
**Source File:** `legacy/services/bid-spec-analysis-v1/cipp_analyzer_clean.html`
**Total Lines:** 2,257
**Last Analysis:** 2025-12-09
**Purpose:** Complete technical inventory for rebuilding the CIPP Analyzer frontend

---

## Table of Contents

1. [UI Elements Inventory](#1-ui-elements-inventory)
2. [Features & Functionality](#2-features--functionality)
3. [JavaScript Functions Catalog](#3-javascript-functions-catalog)
4. [Styling & Visual Design](#4-styling--visual-design)
5. [Data Flow Architecture](#5-data-flow-architecture)
6. [Configuration System](#6-configuration-system)
7. [External Dependencies](#7-external-dependencies)
8. [State Management](#8-state-management)
9. [API Endpoints](#9-api-endpoints)
10. [Event Handling](#10-event-handling)

---

## 1. UI Elements Inventory

### 1.1 Navigation Bar (MPT Navbar)

**Element:** `.mpt-navbar`
**Location:** Lines 727-733
**Styling:** Lines 549-593

**Components:**
- **Logo Container** (`.logo-container`)
  - Company logo image: `/shared/assets/images/logo.png` (40px height)
  - App title: "CIPP Bid-Spec Analyzer" (1.2rem, white, bold)
- **Home Link** (`.home-link`)
  - Text: "← Home"
  - Target: `/` (root)
  - Style: White border, hover effect with background inversion

**Behavior:**
- Sticky positioning (top: 0, z-index: 1000)
- Gradient background: #1E3A8A → #5B7FCC
- Responsive: Stacks vertically on mobile (<768px)

---

### 1.2 Header Section

**Element:** `.header`
**Location:** Lines 736-739
**Styling:** Lines 64-78

**Components:**
- **H1 Title:** "🏗️ CIPP Bid-Spec Analyzer" (2.5em, white)
- **Subtitle:** "Professional bid specification analysis powered by AI" (1.1em, white)

**Behavior:**
- Center-aligned
- 30px bottom margin

---

### 1.3 Document Upload Section

**Element:** `.section` (File Upload)
**Location:** Lines 742-754
**Styling:** Lines 119-133

**Components:**

#### File Upload Drop Zone
- **ID:** `fileUpload`
- **Type:** Clickable drop zone with drag-and-drop support
- **Accepted Formats:** `.pdf, .txt, .docx, .rtf`
- **Visual:**
  - Dashed border (2px, rgba(221, 221, 221, 0.7))
  - 30px padding
  - White translucent background (0.95 opacity)
  - Hover: Border color changes to #5B7FCC
- **Text:**
  - Primary: "Click to select file" (bold)
  - Secondary: "Supported formats: PDF, TXT, DOCX, RTF"

#### Hidden File Input
- **ID:** `fileInput`
- **Type:** `<input type="file">`
- **Display:** `none`
- **Trigger:** Clicked programmatically when drop zone is clicked

#### File Info Display
- **ID:** `fileInfo`
- **Initial State:** Hidden (`display: none`)
- **Shown When:** File selected
- **Contents:**
  - **File Name:** `<span id="fileName">`
  - **File Size:** `<span id="fileSize">` (formatted as B/KB/MB)

#### Test Document Button
- **Text:** "📋 Load Test Document"
- **Class:** `.btn .btn-test`
- **Color:** Green (#28a745)
- **Function:** `loadTestDocument()` (stub - not implemented)

---

### 1.4 Question Configuration Section

**Element:** `.section` (Question Management)
**Location:** Lines 757-793
**Styling:** Lines 243-290

**Components:**

#### Question Sections Grid
- **ID:** `questionSections`
- **Class:** `.question-sections`
- **Layout:** CSS Grid, auto-fit, min 300px columns
- **Contents:** 10 section cards (dynamically generated)

#### Section Card Structure
Each card (`.question-section`) displays:
- **Section Name:** E.g., "Project Information"
- **Question Count Badge:** E.g., "10" (small rounded badge)
- **States:**
  - **Enabled:** Green border (#28a745), light green background
  - **Disabled:** Red border (#dc3545), light red background, 70% opacity
  - **Hover:** Enhanced border, brighter background

#### Active Question Counter
- **Label:** "Active Questions:"
- **ID:** `activeQuestionCount`
- **Value:** Dynamically calculated (sum of enabled sections)
- **Format:** "X questions selected"

#### Context Guardrails Input
- **Location:** Lines 768-787
- **ID:** `contextGuardrails`
- **Type:** `<textarea>`
- **Purpose:** Optional global constraints for AI analysis
- **Placeholder:** "Enter background rules or context constraints..."
- **Styling:**
  - Light blue dashed border
  - Min-height: 80px
  - Resizable vertically
- **Features:**
  - Auto-save on input (`saveContextGuardrails()`)
  - Active guardrails display (hidden initially)
  - Help text explaining purpose

#### Action Buttons
1. **Manage Questions** (`showQuestionManager()`)
   - Icon: 📝
   - Opens question manager modal

2. **Add Custom Section** (`addQuestionSection()`)
   - Icon: ➕
   - Stub function

3. **Export Questions** (`exportQuestions()`)
   - Icon: 📤
   - Stub function

4. **Settings** (`showSettings()`)
   - Icon: ⚙️
   - Opens settings modal

---

### 1.5 Analysis Controls Section

**Element:** `.section` (Analysis Controls)
**Location:** Lines 796-834
**Styling:** Lines 135-167

**Components:**

#### Primary Action Buttons
1. **Start Analysis Button**
   - **ID:** `analyzeBtn`
   - **Text:** "🚀 Start Analysis (Pass 1)"
   - **Initial State:** Disabled (requires file upload)
   - **Function:** `startAnalysis()`
   - **Style:** Blue gradient

2. **Run Second Pass Button**
   - **ID:** `secondPassBtn`
   - **Text:** "🔍 Run Second Pass"
   - **Initial State:** Hidden (`display: none`)
   - **Enabled When:** First pass complete with unanswered questions
   - **Function:** `runSecondPass()`
   - **Style:** Orange gradient (#f59e0b → #d97706)

3. **Stop Analysis Button**
   - **ID:** `stopBtn`
   - **Text:** "⏹️ Stop Analysis"
   - **Initial State:** Disabled
   - **Enabled When:** Analysis running
   - **Function:** `stopAnalysis()`
   - **Style:** Red (#dc3545)

4. **Clear Results Button**
   - **Text:** "🗑️ Clear Results"
   - **Function:** `clearResults()`
   - **Style:** Secondary gray

#### Second Pass Banner
- **ID:** `secondPassBanner`
- **Initial State:** Hidden
- **Shown When:** First pass completes with unanswered questions
- **Components:**
  - Icon: 🔍 (2em)
  - Title: "Second Pass Available!" (orange)
  - Description: Shows count of unanswered questions
  - **Unanswered Count:** `<span id="unansweredCount">`
  - Call-to-action button (duplicate of second pass button)
- **Styling:**
  - Orange gradient background (10% opacity)
  - 4px left border (#f59e0b)
  - Flexbox layout

#### Export Results Dropdown
- **ID:** `exportBtn`
- **Initial State:** Disabled
- **Enabled When:** Analysis complete
- **Function:** `showExportMenu()`
- **Dropdown Menu ID:** `exportMenu`
- **Initial State:** Hidden

**Export Menu Options:**
1. **Excel Dashboard (Charts)** - `exportExcelDashboard()`
   - Premium option (green, bold, ⭐)
   - Server-side generation

2. **Excel (Styled Table)** - `exportResults('excel-simple')`
   - Client-side XLSX generation

3. **CSV (Simple)** - `exportResults('csv')`
   - Plain CSV download

4. **HTML Report** - `exportResults('html')`
   - Styled executive report

5. **Markdown Table** - `exportResults('markdown')`
   - Markdown formatted

6. **JSON Data** - `exportResults('json')`
   - Raw JSON structure

---

### 1.6 Debug Tools Panel (Collapsible)

**Element:** `.debug-panel`
**Location:** Lines 837-908
**Styling:** Lines 363-436

**Master Toggle:**
- **Button Text:** "Show Debug Tools" / "Hide Debug Tools"
- **Icon:** 🛠️ (collapsed) / 🔧 (expanded)
- **Function:** `toggleMasterDebugPanel()`
- **Style:** Purple gradient (#667eea → #764ba2)

**Collapsible Sections (4 total):**

#### 1. Analysis Configuration
- **Header:** "⚙️ Analysis Configuration"
- **ID:** `analysisConfigSection`
- **Initial State:** Collapsed
- **Contents:**
  - **Chunk Size Input**
    - **ID:** `chunkSize`
    - **Type:** Number
    - **Default:** 1500
    - **Range:** 500-2000
    - **Label:** "Characters per Analysis Chunk"
    - **Help Text:** "Recommended: 1500 characters per chunk to stay within token limits"

#### 2. PDF Service Status
- **Header:** "📄 PDF Service Status"
- **ID:** `pdfServiceSection`
- **Initial State:** Collapsed
- **Contents:**
  - **Service Status Display**
    - **ID:** `serviceStatus`
    - **Classes:** `.service-status`, `.service-running` or `.service-stopped`
    - **Text ID:** `serviceStatusText`
    - **Default:** "📄 Checking document extraction service..."

#### 3. API Configuration
- **Header:** "API Configuration" (with status indicator)
- **ID:** `apiConfigSection`
- **Initial State:** Collapsed
- **Contents:**
  - **Status Indicator:** `<span id="apiStatus" class="status-indicator">`
  - **Status Text:** `<p id="apiStatusText">Loading API configuration...</p>`
  - **Test Connection Button**
    - **ID:** `testConnectionBtn`
    - **Text:** "🔗 Test Connection"
    - **Function:** `testApiConnection()`
    - **Class:** `.btn .btn-test`
  - **Test Status Display:** `<span id="testStatusDisplay">` (hidden initially)

#### 4. Activity Log
- **Header:** "📋 Activity Log"
- **ID:** `logSection`
- **Initial State:** Collapsed
- **Contents:**
  - **Action Buttons:**
    - Export Log (`exportLog()`)
    - Clear Log (`clearLog()`)
  - **Log Container**
    - **ID:** `logContainer`
    - **Initial Display:** Block (when debug panel open)
    - **Max Height:** 400px
    - **Overflow:** Vertical scroll
    - **Background:** #f8f9fa
    - **Font:** 'Courier New', monospace, 12px
  - **Log Content:** `<div id="logContent">`

**Log Entry Types:**
- `.log-info` - Cyan (#17a2b8)
- `.log-success` - Green (#28a745)
- `.log-warning` - Yellow (#ffc107)
- `.log-error` - Red (#dc3545)
- `.log-debug` - Purple (#6f42c1)
- `.log-api` - Orange background (#fff3cd)
- `.log-request` - Blue background (#cce5ff)
- `.log-response` - Green background (#d4edda)

---

### 1.7 Progress Indicator

**Element:** `.progress-container`
**Location:** Lines 911-916
**Styling:** Lines 172-196

**Components:**
- **Container ID:** `progressContainer`
- **Initial State:** Hidden (`display: none`)
- **Progress Bar:**
  - **Class:** `.progress-bar`
  - **Fill Element:** `<div id="progressFill" class="progress-fill">`
  - **Initial Width:** 0%
  - **Transition:** Smooth (0.3s)
  - **Colors:** Blue gradient (#5B7FCC → #1E3A8A)
- **Progress Text:**
  - **ID:** `progressText`
  - **Class:** `.progress-text`
  - **Color:** White
  - **Default Text:** "Ready"

**States:**
- Hidden when not analyzing
- Shows during upload (10%)
- Shows during analysis (20-95%)
- Hidden when complete

---

### 1.8 Live Results Section

**Element:** `.results-section`
**Location:** Lines 922-928
**Styling:** Lines 238-241

**Components:**
- **Section ID:** `resultsSection`
- **Initial State:** Hidden (`display: none`)
- **Title:** "📋 Analysis Results (Live Updates)"
- **Container:** `<div id="liveResultsContainer">`
  - **Table Container:** `<div id="liveResultsTable">`
  - **Content Container:** `<div id="resultsContent">`

**Display States:**
1. **Loading State:** Shows during analysis
   - Animated spinner (🔄)
   - Message: "Analysis in Progress"
   - Subtext: "Live results will appear here as windows are processed..."

2. **Results State:** Shows completed analysis
   - Sectioned question/answer display
   - White background, rounded corners
   - Per-section headers
   - Per-question cards with border-left accent

---

### 1.9 Industry Intelligence Dashboards

**Element:** `.results-section` (Dashboard)
**Location:** Lines 930-998
**Styling:** Lines 439-546, 638-722

**Toggle Button Container:**
- **ID:** `dashboardButtonContainer`
- **Initial State:** Hidden
- **Button:**
  - Text: "Show Industry Intelligence Dashboards"
  - Icon: 📊
  - Toggle Function: `toggleDashboardPanel()`
  - Style: Green gradient (#11998e → #38ef7d)
  - Description: "Interactive visualizations of your bid specification analysis"

**Dashboard Section:**
- **ID:** `dashboardSection`
- **Initial State:** Hidden
- **Background:** Purple gradient (#667eea → #764ba2)
- **Header:**
  - Title: "📊 CIPP Industry Intelligence Dashboards"
  - Refresh Button: `refreshDashboards()`
  - Subtitle: "Visual insights extracted from your bid specification analysis"

**Dashboard Grid (5 Cards):**

#### 1. Risk Assessment Matrix
- **Card Class:** `.dashboard-card`
- **Title:** "🎯 Risk Assessment Matrix"
- **Chart Canvas:** `<canvas id="riskMatrixChart">`
- **Max Height:** 300px
- **Summary:** `<div id="riskSummary">` (insights panel)

#### 2. Cost Driver Breakdown
- **Title:** "💰 Cost Driver Breakdown"
- **Chart Canvas:** `<canvas id="costDriverChart">`
- **Max Height:** 300px
- **Summary:** `<div id="costSummary">`

#### 3. Compliance Scorecard
- **Title:** "✅ Compliance Scorecard"
- **Chart Canvas:** `<canvas id="complianceChart">`
- **Max Height:** 300px
- **Summary:** `<div id="complianceSummary">`

#### 4. Timeline & Key Milestones
- **Title:** "📅 Timeline & Key Milestones"
- **Chart Canvas:** `<canvas id="timelineChart">`
- **Max Height:** 300px
- **Summary:** `<div id="timelineSummary">`

#### 5. Bid Competitiveness Gauge (Full Width)
- **Grid Column:** Span 2
- **Title:** "🏆 Bid Competitiveness Gauge"
- **Layout:** Flexbox (gauge + summary side-by-side)
- **Chart Canvas:** `<canvas id="competitivenessGauge">`
- **Max Dimensions:** 300x300px
- **Summary:** `<div id="competitivenessSummary">` (larger text panel)

**Responsive Behavior:**
- **<1024px:** Single column grid
- **<768px:** Reduced chart heights (250px), smaller fonts
- **<480px:** Further reduced (200px charts), compact spacing

---

### 1.10 Modals

#### Settings Modal

**Element ID:** `settingsModal`
**Location:** Lines 1002-1025
**Styling:** Lines 312-360

**Structure:**
- **Modal Overlay:** Full-screen (rgba(0,0,0,0.5))
- **Modal Content:** Center-aligned, white, rounded, 90% max width/height
- **Close Button:** Top-right X (`.close-btn`)

**Contents:**
- **Title:** "⚙️ Application Settings"
- **API Key Info Panel:**
  - Blue background (#e7f3ff)
  - Left border (#2196F3)
  - Message: "The OpenAI API key is configured via environment variables on the server. Contact your system administrator to update the API key."
- **GPT Model Selector:**
  - **ID:** `gptModel`
  - **Options:**
    1. `gpt-4o` (Recommended - 128K context)
    2. `gpt-4-turbo` (128K context)
    3. `gpt-4` (8K context - may fail on large docs)
    4. `gpt-3.5-turbo` (16K context)
- **Action Buttons:**
  - Save Settings (`saveSettings()`)
  - Close (`hideSettings()`)

#### Question Manager Modal

**Element ID:** `questionManagerModal`
**Location:** Lines 1028-1071
**Styling:** Same as settings modal

**Structure:**
- **Title:** "📝 Question Manager"
- **Max Width:** 95%
- **Max Height:** 90%

**Contents:**

1. **Section Selector:**
   - **ID:** `sectionSelect`
   - **Options:** Populated dynamically from config
   - **OnChange:** `loadSectionForEdit()`
   - **Default:** "-- Select a section --"

2. **Section Actions:**
   - Add New Section (`addNewSectionInManager()`)
   - Delete Section (`deleteCurrentSection()`) - Danger button

3. **Section Editor (Initially Hidden):**
   - **ID:** `sectionEditor`
   - **Display:** None until section selected

   **Components:**
   - **Section Name Display:** `<h3 id="currentSectionName">`
   - **Enabled Checkbox:**
     - **ID:** `sectionEnabled`
     - **OnChange:** `toggleSectionEnabled()`
   - **Section Name Input:**
     - **ID:** `sectionNameInput`
     - **OnChange:** `updateSectionName()`
   - **Questions List:**
     - **ID:** `questionsList`
     - **Max Height:** 400px
     - **Overflow:** Vertical scroll
     - **Background:** #f9f9f9
   - **Add Question Button:** `addNewQuestion()`

4. **Bottom Actions:**
   - Save All Changes (`saveQuestions()`)
   - Close (`hideQuestionManager()`)
   - Export Questions (`exportQuestions()`)
   - Import Questions (hidden file input + button)
     - **ID:** `importQuestionsFile`
     - **Accept:** `.json`
     - **OnChange:** `importQuestions(event)`

---

## 2. Features & Functionality

### 2.1 File Upload System

**Supported Methods:**
1. **Click-to-Select:** Triggers hidden file input
2. **Drag-and-Drop:** Drop zone with visual feedback

**Supported Formats:**
- PDF (`.pdf`)
- Text (`.txt`)
- Word (`.docx`)
- Rich Text (`.rtf`)

**Upload Flow:**
1. User selects/drops file
2. `handleFileSelect(event)` triggered
3. File stored in `currentFile` global variable
4. UI updates:
   - File name displayed
   - File size formatted and displayed
   - File info section shown
   - Analyze button enabled
5. Logger entry created

**File Size Formatting:**
- <1KB: Bytes
- <1MB: Kilobytes (2 decimals)
- ≥1MB: Megabytes (2 decimals)

---

### 2.2 Analysis Workflow

**Pass 1 (Primary Analysis):**

1. **Pre-Analysis Validation:**
   - Check `currentFile` exists
   - Validate context guardrails (optional)

2. **File Upload Phase:**
   - Create FormData with file
   - POST to `/api/upload`
   - Receive `filepath` in response
   - Update progress (10% → 20%)

3. **Session Initialization:**
   - Generate session ID: `session_${Date.now()}`
   - Store in `currentSessionId`
   - Save to localStorage for resume support

4. **SSE Connection (Real-time Progress):**
   - Connect to `/api/progress/${sessionId}`
   - Listen for events (before analysis starts)
   - Auto-expand debug panel
   - Auto-show live results section

5. **Start Analysis:**
   - POST to `/api/analyze` with:
     - `session_id`
     - `pdf_path`
     - `context_guardrails` (optional)
   - Analysis runs in background
   - UI state changes:
     - Analyze button disabled
     - Stop button enabled
     - Progress bar shown

6. **Live Progress Updates (via SSE):**
   - `connected` → Log connection established
   - `document_ingested` → Show page count, window count
   - `config_loaded` → Show question count
   - `expert_generated` → Log expert creation
   - `window_processing` → Update progress bar (40-90%)
   - `experts_dispatched` → Log concurrent API calls
   - `experts_complete` → Log answers found, tokens used
   - `window_complete` → Log timing, display unitary log
   - `progress_milestone` → General progress updates
   - `done` → Close SSE, fetch results
   - `error` → Close SSE, show error

7. **Results Retrieval:**
   - GET `/api/results/${sessionId}`
   - Parse result structure
   - Display Q&A by section
   - Show statistics
   - Enable export button
   - Check for unanswered questions

8. **Second Pass Trigger (if needed):**
   - Count unanswered questions
   - If > 0:
     - Show second pass banner
     - Enable second pass button
     - Display unanswered count

**Pass 2 (Enhanced Scrutiny):**
- **Trigger:** User clicks "Run Second Pass" button
- **Purpose:** Re-analyze unanswered questions with:
  - Expanded search patterns
  - Relaxed confidence thresholds
  - Adjacent page scanning
- **Status:** Not fully implemented (stub function)

---

### 2.3 Live Analysis Window

**Purpose:** Show real-time progress and results during analysis

**Components:**
1. **Loading State:** Animated spinner with instructions
2. **Live Updates:** Markdown-formatted unitary logs from each window
3. **Final State:** Fully rendered Q&A results

**Content Types:**
- **Unitary Log Markdown:**
  - Shows window-by-window progress
  - Lists questions answered in each window
  - Includes page citations
  - Simple markdown-to-HTML conversion:
    - `**text**` → `<strong>text</strong>`
    - `# Header` → `<h1>Header</h1>`
    - `## Header` → `<h2>Header</h2>`
    - `### Header` → `<h3>Header</h3>`
    - `\n` → `<br>`

---

### 2.4 Activity Log System

**Class:** `Logger`
**Location:** Lines 1092-1115

**Methods:**
- `Logger.log(message, type)` - Base logging method
- `Logger.info(msg)` - Info level (cyan)
- `Logger.success(msg)` - Success level (green)
- `Logger.error(msg)` - Error level (red)
- `Logger.warning(msg)` - Warning level (yellow)
- `Logger.debug(msg)` - Debug level (purple)

**Features:**
- Timestamp on every entry
- Color-coded by type
- Supports object logging (JSON.stringify)
- Auto-scroll to bottom
- Exportable as text file
- Clearable

**Entry Format:**
```
[HH:MM:SS] Message text
```

**Log Container Behavior:**
- Initially hidden
- Auto-shows when first log entry added
- Max height 400px with scroll
- Monospace font for readability

---

### 2.5 Results Display

**Structure:** Hierarchical by section

**Display Format:**

```
Section Name (H2)
  ├─ Question 1
  │   ├─ Question Text (bold)
  │   ├─ Answer (paragraph)
  │   └─ Page Citations (small, gray, "Pages: 1, 3, 5")
  ├─ Question 2
  │   ├─ Question Text
  │   └─ "Not found in document" (italic, gray)
  ...
```

**Styling:**
- White background container
- 20px padding, 8px border-radius
- Questions: 15px margin, 10px padding
- Left border accent: 3px solid #5b7fcc
- Unanswered: Italic, gray text (#999)

**Statistics Panel:**
- Questions Answered: X / Y
- Processing Time: X.XX seconds
- Total Tokens: X,XXX (with commas)
- Estimated Cost: $X.XX
- Average Confidence: XX%

---

### 2.6 Footnote/Citation Display

**Format:** Inline page citations

**Appearance:**
- Small font size
- Gray color (#666)
- Format: "Pages: 1, 3, 5"
- Position: Below answer text

**Data Source:** `q.page_citations` array

---

### 2.7 Question Configuration (100 Questions, 10 Sections)

**Default Configuration:** (Lines 1983-2010)

**Sections:**
1. **Project Information** (10 questions)
2. **Pipe Specifications** (10 questions)
3. **CIPP Liner Requirements** (10 questions)
4. **Pre-Installation Work** (10 questions)
5. **Installation Process** (10 questions)
6. **Quality Control & Testing** (10 questions)
7. **Warranty & Maintenance** (10 questions)
8. **Environmental & Safety** (10 questions)
9. **Payment & Documentation** (10 questions)
10. **Special Conditions** (10 questions)

**Data Structure:**
```javascript
{
  sections: [
    {
      id: 'section_id',
      name: 'Section Name',
      questions: 10,
      enabled: true/false
    }
  ],
  totalQuestions: 100
}
```

**Display:**
- Grid layout (auto-fit, min 300px)
- Clickable cards
- Visual state indicators (enabled/disabled)
- Live counter updates

---

### 2.8 Question Modification Capability

**Access:** Via Question Manager Modal

**Features:**
1. **Select Section:** Dropdown selector
2. **Enable/Disable Section:** Checkbox toggle
3. **Rename Section:** Text input with live update
4. **Edit Questions:** Scrollable list
5. **Add New Question:** Button-triggered
6. **Delete Section:** With confirmation
7. **Import/Export:** JSON file support

**Persistence:** (Not shown in code - likely server-side or localStorage)

---

### 2.9 Export Functionality

**Formats Supported:**

#### 1. Excel Dashboard (Server-Side)
- **Function:** `exportExcelDashboard()`
- **Endpoint:** `/api/export/excel-dashboard/${sessionId}`
- **Features:**
  - Professional charts (openpyxl)
  - Multiple worksheets
  - Formatted headers
  - Visual dashboards
- **Filename:** `CIPP_Executive_Dashboard.xlsx`

#### 2. Excel Simple (Client-Side)
- **Function:** `exportExcelSimple(data)`
- **Library:** SheetJS (XLSX)
- **Features:**
  - Styled table (15pt font)
  - Text wrapping enabled
  - Auto-sized columns (35/70/90/22 width)
  - Row heights set to 60px
  - Bold header row
  - Blue header background (#1E3A8A)
- **Filename:** `cipp_analysis.xlsx`

#### 3. CSV
- **Function:** `downloadCSV(data)`
- **Format:** Standard comma-separated
- **Columns:** Section, Question, Answer, Pages
- **Quote Handling:** Double-quote escaping
- **Filename:** `cipp_analysis.csv`

#### 4. HTML Report
- **Function:** `exportHTML(data)`
- **Features:**
  - Executive report styling
  - Print-optimized CSS
  - Section badges (X/Y answered)
  - Color-coded Q&A cards
  - Page citations in blue boxes
  - Generated timestamp
- **Filename:** `cipp_analysis_report.html`

#### 5. Markdown
- **Function:** `exportMarkdown(data)`
- **Features:**
  - Executive summary table
  - Section breakdowns with percentages
  - Numbered questions
  - Blockquotes for citations
  - Horizontal rules between sections
- **Filename:** `CIPP_Analysis_Executive_Report.md`

#### 6. JSON
- **Function:** `downloadJSON(data, filename)`
- **Format:** Pretty-printed (2-space indent)
- **Filename:** `cipp_analysis.json`

---

### 2.10 Session Resumption (Laptop Sleep Support)

**Purpose:** Resume analysis after browser close or laptop sleep

**Mechanism:**

1. **Save State:**
   - Triggered when analysis starts
   - Stores in localStorage:
     - `cipp_active_session_id`
     - `cipp_session_start_time`

2. **Check on Load:**
   - `checkForResumeSession()` runs on DOMContentLoaded
   - Validates session age (<30 minutes)
   - If valid:
     - Try to fetch results
     - If not ready, reconnect SSE
     - If ready, display results

3. **Polling Mechanism:**
   - Retry every 5 seconds if SSE fails
   - Maximum 30-minute window

4. **Clear State:**
   - On successful completion
   - On stop/cancel
   - On error

---

### 2.11 Error Handling

**Levels:**

1. **Network Errors:**
   - Try/catch on all fetch calls
   - Logger.error() messages
   - Alert() to user
   - State cleanup (buttons re-enabled)

2. **SSE Errors:**
   - `onerror` handler logs disconnection
   - Automatic reconnection attempts
   - Fallback to polling

3. **Validation Errors:**
   - File upload check
   - Session ID check
   - Data parsing failures

4. **User Feedback:**
   - Progress bar updates
   - Status text changes
   - Logger entries
   - Alert dialogs (for critical errors)

---

## 3. JavaScript Functions Catalog

### 3.1 Global Variables

```javascript
let currentFile = null;              // Currently selected file object
let currentSessionId = null;         // Active analysis session ID
let currentAnalysisResult = null;    // Completed analysis results
let activeEventSource = null;        // SSE connection object
let questionConfig = {               // Question configuration
  sections: [],
  totalQuestions: 0
};
```

---

### 3.2 Utility Classes

#### Logger Class
**Lines:** 1092-1115

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `Logger.log()` | `message, type='info'` | void | Base logging function |
| `Logger.info()` | `msg` | void | Log info message (cyan) |
| `Logger.success()` | `msg` | void | Log success message (green) |
| `Logger.error()` | `msg` | void | Log error message (red) |
| `Logger.warning()` | `msg` | void | Log warning message (yellow) |
| `Logger.debug()` | `msg` | void | Log debug message (purple) |

**Dependencies:** DOM elements (`logContent`, `logContainer`)

#### ProgressTracker Class
**Lines:** 1121-1134

| Method | Parameters | Returns | Purpose |
|--------|-----------|---------|---------|
| `ProgressTracker.show()` | none | void | Display progress bar |
| `ProgressTracker.hide()` | none | void | Hide progress bar |
| `ProgressTracker.update()` | `percentage, text` | void | Update bar and text |

**Dependencies:** DOM elements (`progressContainer`, `progressFill`, `progressText`)

---

### 3.3 File Handling Functions

#### handleFileSelect()
**Lines:** 1140-1177
**Called By:** File input change event, drop zone drop event

```javascript
function handleFileSelect(event)
```

**Parameters:** `event` - File input change event or drop event
**Returns:** void
**Side Effects:**
- Sets `currentFile` global
- Updates UI (file name, size, info visibility)
- Enables analyze button
- Logs file selection

**Dependencies:**
- `formatFileSize()`
- DOM elements: `fileName`, `fileSize`, `fileInfo`, `analyzeBtn`

**Error Handling:**
- Try/catch for UI updates
- Alert on error
- Console logging

#### formatFileSize()
**Lines:** 1179-1183

```javascript
function formatFileSize(bytes)
```

**Parameters:** `bytes` (number)
**Returns:** Formatted string (e.g., "1.5 MB")
**Logic:**
- <1024: "X B"
- <1MB: "X.XX KB"
- ≥1MB: "X.XX MB"

---

### 3.4 Core Analysis Functions

#### startAnalysis()
**Lines:** 1189-1356
**Called By:** Analyze button click

```javascript
async function startAnalysis()
```

**Flow:**
1. Validate `currentFile` exists
2. Get context guardrails (optional)
3. Disable/enable control buttons
4. Show progress (10%)
5. Upload file via `/api/upload`
6. Generate session ID
7. Save session state
8. Connect SSE to `/api/progress/${sessionId}`
9. Auto-expand debug tools
10. Auto-show live results
11. Start analysis via `/api/analyze`
12. Listen for SSE events

**SSE Event Handlers:**
- `connected` - Stream established
- `document_ingested` - PDF parsed
- `config_loaded` - Questions loaded
- `expert_generated` - AI expert created
- `window_processing` - Processing chunk
- `experts_dispatched` - Parallel API calls
- `experts_complete` - Answers received
- `window_complete` - Chunk done, show log
- `progress_milestone` - General update
- `done` - Analysis complete, fetch results
- `error` - Show error, cleanup

**Error Handling:**
- Try/catch wrapper
- Logger.error() on failure
- Alert user
- Cleanup state (hide progress, enable buttons, close SSE)

**Dependencies:**
- `ProgressTracker`
- `Logger`
- `saveSessionState()`
- `autoExpandDebugTools()`
- `showLiveResults()`
- `fetchResults()`
- `displayLiveUnitaryLog()`

#### fetchResults()
**Lines:** 1362-1394
**Called By:** `startAnalysis()` on 'done' event

```javascript
async function fetchResults()
```

**Flow:**
1. GET `/api/results/${currentSessionId}`
2. Parse JSON response
3. Store in `currentAnalysisResult`
4. Log statistics
5. Display results via `displayResults()`
6. Display statistics via `displayStatistics()`
7. Enable export button
8. Hide progress, reset buttons
9. Clear session state

**Error Handling:**
- Try/catch
- Logger.error() on failure

#### stopAnalysis()
**Lines:** 1475-1504
**Called By:** Stop button click

```javascript
async function stopAnalysis()
```

**Flow:**
1. Validate `currentSessionId` exists
2. POST `/api/stop/${sessionId}`
3. Close SSE connection
4. Reset UI state
5. Clear session state

**Error Handling:**
- Try/catch
- Logger.error() on failure

#### runSecondPass()
**Lines:** 2180-2211
**Called By:** Second pass button click

```javascript
async function runSecondPass()
```

**Status:** Stub implementation (not fully functional)

**Planned Flow:**
1. Validate session and results exist
2. Count unanswered questions
3. Show progress
4. Call backend second pass endpoint (not implemented)
5. Enhanced scrutiny analysis
6. Update results

---

### 3.5 Display Functions

#### displayResults()
**Lines:** 1400-1436

```javascript
function displayResults(result)
```

**Parameters:** `result` - Analysis result object
**Returns:** void
**Side Effects:**
- Updates `resultsContent` innerHTML
- Shows `resultsSection`

**HTML Structure Generated:**
```html
<div style="background: white; ...">
  <h2>Section Name</h2>
  <div style="margin: 15px 0; ...">
    <strong>Q: Question text</strong><br>
    <p>Answer text</p>
    <small>Pages: 1, 3, 5</small>
  </div>
  ...
</div>
```

#### displayStatistics()
**Lines:** 1438-1453

```javascript
function displayStatistics(stats)
```

**Parameters:** `stats` - Statistics object
**Returns:** void
**Side Effects:** Updates `statisticsContent` innerHTML

**Stats Displayed:**
- Questions Answered (X / Y)
- Processing Time (seconds)
- Total Tokens (with thousand separators)
- Estimated Cost
- Average Confidence

#### displayLiveUnitaryLog()
**Lines:** 1455-1469

```javascript
function displayLiveUnitaryLog(markdownContent)
```

**Parameters:** `markdownContent` - Markdown-formatted log
**Returns:** void
**Side Effects:**
- Converts markdown to HTML
- Updates `resultsContent`
- Shows `resultsSection`

**Markdown Conversions:**
- `**text**` → `<strong>`
- `# H1` → `<h1>`
- `## H2` → `<h2>`
- `### H3` → `<h3>`
- `\n` → `<br>`

---

### 3.6 Export Functions

#### showExportMenu()
**Lines:** 1510-1513

```javascript
function showExportMenu()
```

**Returns:** void
**Side Effects:** Toggles export dropdown visibility

#### exportResults()
**Lines:** 1515-1543

```javascript
function exportResults(format)
```

**Parameters:** `format` - Export format string
**Supported Formats:**
- `'json'` → `downloadJSON()`
- `'csv'` → `downloadCSV()`
- `'excel-simple'` → `exportExcelSimple()`
- `'html'` → `exportHTML()`
- `'markdown'` → `exportMarkdown()`

**Returns:** void
**Side Effects:**
- Triggers file download
- Logs export action
- Hides export menu

#### downloadJSON()
**Lines:** 1545-1552

```javascript
function downloadJSON(data, filename)
```

**Parameters:**
- `data` - Object to export
- `filename` - Download filename

**Returns:** void
**Mechanism:** Blob + createObjectURL + temporary anchor click

#### downloadCSV()
**Lines:** 1554-1571

```javascript
function downloadCSV(data)
```

**Parameters:** `data` - Analysis results object
**Returns:** void
**CSV Format:**
```
Section,Question,Answer,Pages
"Section Name","Question text","Answer text","1;3;5"
```

**Escaping:** Double-quotes escaped as `""`

#### exportExcelSimple()
**Lines:** 1573-1644

```javascript
function exportExcelSimple(data)
```

**Parameters:** `data` - Analysis results object
**Returns:** void
**Library:** SheetJS (XLSX)

**Styling Features:**
- Column widths: 35, 70, 90, 22
- Row height: 60px
- Text wrapping: Enabled
- Font: Calibri, 15pt
- Header: Bold, blue background
- Vertical alignment: Top

#### exportHTML()
**Lines:** 1646-1793

```javascript
function exportHTML(data)
```

**Parameters:** `data` - Analysis results object
**Returns:** void

**HTML Features:**
- Full HTML document with CSS
- Print-optimized (@page, @media print)
- Executive styling
- Section badges (X/Y answered)
- Color-coded answers/unanswered
- Page citation boxes
- Gradient header
- Professional typography (Calibri, 15pt base)

#### exportMarkdown()
**Lines:** 1795-1846

```javascript
function exportMarkdown(data)
```

**Parameters:** `data` - Analysis results object
**Returns:** void

**Markdown Features:**
- Executive summary table
- Section-by-section breakdown
- Answer rate percentages
- Numbered questions
- Blockquotes for citations
- Horizontal rule separators

#### exportExcelDashboard()
**Lines:** 2213-2247

```javascript
async function exportExcelDashboard()
```

**Returns:** void (async)
**Endpoint:** `/api/export/excel-dashboard/${sessionId}`
**Method:** Server-side generation (openpyxl)

**Features:**
- Professional charts
- Multiple worksheets
- Executive formatting
- Visual dashboards

---

### 3.7 State Management Functions

#### saveSessionState()
**Lines:** 1868-1874

```javascript
function saveSessionState()
```

**Returns:** void
**Storage:** localStorage
**Keys:**
- `cipp_active_session_id` - Current session ID
- `cipp_session_start_time` - Timestamp (milliseconds)

#### checkForResumeSession()
**Lines:** 1876-1896

```javascript
function checkForResumeSession()
```

**Returns:** void
**Called By:** DOMContentLoaded event

**Flow:**
1. Load session ID and timestamp from localStorage
2. Calculate elapsed time
3. If >30 minutes: Clear and abort
4. If <30 minutes: Log and attempt resume
5. Set `currentSessionId`
6. Call `pollForResults()`

#### pollForResults()
**Lines:** 1898-1924

```javascript
async function pollForResults()
```

**Returns:** void (async)

**Flow:**
1. GET `/api/results/${currentSessionId}`
2. If successful:
   - Display results
   - Clear session state
3. If not ready:
   - Log status
   - Call `reconnectSSE()`

**Error Handling:**
- Try/catch
- Clear session on error

#### reconnectSSE()
**Lines:** 1926-1956

```javascript
function reconnectSSE()
```

**Returns:** void

**Flow:**
1. Create new EventSource to `/api/progress/${sessionId}`
2. Listen for `done` event → fetch results
3. Listen for `error` event → clear state
4. On SSE error: Retry polling in 5 seconds

#### clearSessionState()
**Lines:** 1958-1961

```javascript
function clearSessionState()
```

**Returns:** void
**Storage:** Removes localStorage keys

---

### 3.8 UI Helper Functions

#### clearResults()
**Lines:** 1852-1862

```javascript
function clearResults()
```

**Returns:** void
**Side Effects:**
- Hides results section
- Clears HTML content
- Disables export button
- Resets globals (`currentAnalysisResult`, `currentSessionId`)
- Hides progress
- Logs action

#### toggleMasterDebugPanel()
**Lines:** 2061-2075

```javascript
function toggleMasterDebugPanel()
```

**Returns:** void
**Side Effects:**
- Toggles debug panel visibility
- Updates button text/icon

#### toggleDebugSection()
**Lines:** 2077-2091

```javascript
function toggleDebugSection(sectionId)
```

**Parameters:** `sectionId` - Debug section element ID
**Returns:** void
**Side Effects:**
- Toggles section visibility
- Updates header class (collapsed/expanded)
- Rotates toggle icon (▼/▲)

#### autoExpandDebugTools()
**Lines:** 2097-2124

```javascript
function autoExpandDebugTools()
```

**Returns:** void
**Purpose:** Auto-show debug panel and activity log when analysis starts

**Flow:**
1. Show master debug panel if hidden
2. Expand activity log section
3. Scroll debug panel into view (smooth)

#### showLiveResults()
**Lines:** 2126-2146

```javascript
function showLiveResults()
```

**Returns:** void
**Purpose:** Show loading state in results section

**Side Effects:**
- Shows results section
- Displays animated spinner
- Shows "Analysis in Progress" message
- Adds instructional text

---

### 3.9 Question Configuration Functions

#### loadQuestionConfig()
**Lines:** 1981-2010

```javascript
function loadQuestionConfig()
```

**Returns:** void
**Called By:** DOMContentLoaded event

**Flow:**
1. Initialize `questionConfig` with default 10 sections
2. Render section cards to `questionSections` container
3. Call `updateActiveQuestionCount()`

**Default Sections:**
- Project Information (10)
- Pipe Specifications (10)
- CIPP Liner Requirements (10)
- Pre-Installation Work (10)
- Installation Process (10)
- Quality Control & Testing (10)
- Warranty & Maintenance (10)
- Environmental & Safety (10)
- Payment & Documentation (10)
- Special Conditions (10)

#### updateActiveQuestionCount()
**Lines:** 2012-2018

```javascript
function updateActiveQuestionCount()
```

**Returns:** void
**Side Effects:** Updates `activeQuestionCount` text content

**Calculation:** Sum of `questions` count for all enabled sections

#### toggleSection()
**Lines:** 2172-2178

```javascript
function toggleSection(sectionId)
```

**Parameters:** `sectionId` - Section identifier
**Returns:** void
**Side Effects:**
- Toggles section `enabled` flag
- Calls `loadQuestionConfig()` to re-render

---

### 3.10 File Upload Setup

#### setupFileDragDrop()
**Lines:** 2020-2055

```javascript
function setupFileDragDrop()
```

**Returns:** void
**Called By:** DOMContentLoaded event

**Setup:**
1. Attach `change` event listener to file input
2. Attach drag-and-drop handlers to drop zone:
   - `dragover` - Prevent default, change border color
   - `dragleave` - Reset border color
   - `drop` - Prevent default, handle files

**Event Handlers:**
- File input change: Call `handleFileSelect()`
- Drag over: Visual feedback (blue border)
- Drop: Extract files, update input, call handler

---

### 3.11 Stub/Not Implemented Functions

#### loadTestDocument()
**Lines:** 2152-2154

```javascript
function loadTestDocument()
```

**Status:** Stub (alert placeholder)

#### showQuestionManager()
**Lines:** 2156-2158

```javascript
function showQuestionManager()
```

**Status:** Stub (alert placeholder)

#### addQuestionSection()
**Lines:** 2160-2162

```javascript
function addQuestionSection()
```

**Status:** Stub (alert placeholder)

#### exportQuestions()
**Lines:** 2164-2166

```javascript
function exportQuestions()
```

**Status:** Stub (alert placeholder)

#### showSettings()
**Lines:** 2168-2170

```javascript
function showSettings()
```

**Status:** Stub (alert placeholder)

#### exportLog()
**Lines:** 2249-2252

```javascript
function exportLog()
```

**Status:** Partial implementation (uses `downloadJSON()`)

#### clearLog()
**Lines:** 2254-2256

```javascript
function clearLog()
```

**Status:** Implemented (clears `logContent` innerHTML)

---

### 3.12 Initialization

#### DOMContentLoaded Handler
**Lines:** 1967-1979

```javascript
document.addEventListener('DOMContentLoaded', () => {
  Logger.info('CIPP Bid-Spec Analyzer initialized');
  loadQuestionConfig();
  setupFileDragDrop();
  checkForResumeSession();
});
```

**Initialization Sequence:**
1. Log startup message
2. Load question configuration (render sections)
3. Setup file drag-and-drop handlers
4. Check for resumable session (laptop sleep recovery)

---

## 4. Styling & Visual Design

### 4.1 Background & Container System

#### Background Layer 1 (Image)
**Element:** `body::before`
**Styling:** Lines 25-39

**Properties:**
- Position: Fixed, full-screen
- Image: `/shared/assets/images/bg3.jpg`
- Background-size: Cover
- Background-position: Center center
- Background-attachment: Fixed
- Filter: brightness(0.75) - 25% darkened
- Z-index: -2 (behind everything)

**Responsive:**
- <768px: `background-attachment: scroll`
- <480px: `background-size: auto 100%`

#### Background Layer 2 (Gradient Overlay)
**Element:** `body::after`
**Styling:** Lines 41-50

**Properties:**
- Position: Fixed, full-screen
- Gradient: 135deg, rgba(91,127,204,0.4) → rgba(30,58,138,0.5)
- Z-index: -1 (above image, below content)

#### Main Container
**Element:** `.container`
**Styling:** Lines 52-62

**Properties:**
- Background: rgba(255,255,255,0.15) - 15% white translucent
- Backdrop-filter: blur(2.5px) - glassmorphism effect
- Border-radius: 15px
- Box-shadow: 0 20px 40px rgba(0,0,0,0.1)
- Padding: 30px
- Max-width: 1000px
- Width: calc(100% - 40px)
- Min-height: 600px
- Margin: 20px auto (centered)

**Responsive:**
- <768px: Padding 20px, width calc(100% - 20px)
- <480px: Padding 15px

---

### 4.2 Typography

#### Font Stack
**Primary:** 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
**Monospace (logs):** 'Courier New', monospace

#### Headers
- **H1:** 2.5em, white, margin-bottom 10px
- **H2:** 1.3em, white, margin-bottom 15px (in sections)
- **H3:** Varies by context

**Responsive H1:**
- <768px: 1.8em
- <480px: 1.5em

#### Body Text
- **Paragraphs:** 1.1em (in header), white
- **Labels:** White, font-weight 500
- **Small text:** 12px (in section badges)

---

### 4.3 Color Palette

#### Primary Colors
- **Primary Blue:** #5B7FCC
- **Dark Blue:** #1E3A8A
- **Light Blue (info):** #17a2b8

#### Status Colors
- **Success:** #28a745 (green)
- **Warning:** #ffc107 (yellow)
- **Error/Danger:** #dc3545 (red)
- **Debug:** #6f42c1 (purple)

#### Neutral Colors
- **Gray:** #6c757d
- **Light Gray:** #e0e0e0, #f8f9fa
- **Border Gray:** #ddd, #dee2e6

#### Gradients
1. **Primary Button:** 45deg, #5B7FCC → #1E3A8A
2. **Navbar:** 135deg, #1E3A8A → #5B7FCC
3. **Background Overlay:** 135deg, rgba(91,127,204,0.4) → rgba(30,58,138,0.5)
4. **Dashboard Section:** 135deg, #667eea → #764ba2
5. **Second Pass Button:** 45deg, #f59e0b → #d97706
6. **Dashboard Toggle:** 135deg, #11998e → #38ef7d
7. **Debug Tools Toggle:** 135deg, #667eea → #764ba2

---

### 4.4 Button Styles

#### Base Button (`.btn`)
**Styling:** Lines 135-158

**Properties:**
- Background: Gradient (45deg, #5B7FCC → #1E3A8A)
- Color: White
- Border: None
- Padding: 12px 25px
- Border-radius: 6px
- Cursor: Pointer
- Font-size: 16px
- Font-weight: 500
- Transition: all 0.3s
- Margin: 10px 10px 10px 0

**Hover:**
- Transform: translateY(-2px)
- Box-shadow: 0 5px 15px rgba(102,126,234,0.4)

**Disabled:**
- Opacity: 0.6
- Cursor: not-allowed
- Transform: none

#### Button Variants
- **`.btn-secondary`:** Background #6c757d (gray)
- **`.btn-danger`:** Background #dc3545 (red)
- **`.btn-test`:** Background #28a745 (green)

---

### 4.5 Section Cards

#### General Section (`.section`)
**Styling:** Lines 80-86

**Properties:**
- Margin-bottom: 25px
- Padding: 20px
- Border: 1px solid rgba(224,224,224,0.5)
- Border-radius: 8px
- Background: Transparent

#### Question Section Cards (`.question-section`)
**Styling:** Lines 250-274

**Properties:**
- Border: 1px solid rgba(221,221,221,0.6)
- Border-radius: 6px
- Padding: 15px
- Background: rgba(255,255,255,0.9)
- Backdrop-filter: blur(5px)
- Cursor: Pointer
- Transition: all 0.3s

**States:**
- **Hover:** Border #5B7FCC, background rgba(255,255,255,0.95)
- **Enabled:** Border #28a745, background rgba(248,255,248,0.9)
- **Disabled:** Border #dc3545, background rgba(255,248,248,0.9), opacity 0.7

**Layout:**
- Grid: auto-fit, minmax(300px, 1fr)
- Gap: 10px

---

### 4.6 Form Elements

#### Text Inputs & Textareas
**Styling:** Lines 105-117

**Properties:**
- Width: 100%
- Padding: 12px
- Border: 2px solid #ddd
- Border-radius: 6px
- Font-size: 14px
- Transition: border-color 0.3s

**Focus:**
- Outline: None
- Border-color: #5B7FCC

#### File Upload Zone
**Styling:** Lines 119-133

**Properties:**
- Border: 2px dashed rgba(221,221,221,0.7)
- Border-radius: 8px
- Padding: 30px
- Text-align: Center
- Cursor: Pointer
- Transition: all 0.3s
- Background: rgba(255,255,255,0.95)
- Backdrop-filter: blur(5px)

**Hover:**
- Border-color: #5B7FCC
- Background: rgba(248,249,255,0.95)

---

### 4.7 Progress Bar

**Container:** `.progress-container`
**Styling:** Lines 172-196

**Properties:**
- Margin-top: 20px
- Display: None (initially)

**Progress Bar:**
- Width: 100%
- Height: 20px
- Background: #e0e0e0
- Border-radius: 10px
- Overflow: Hidden

**Progress Fill:**
- Height: 100%
- Background: Gradient (45deg, #5B7FCC → #1E3A8A)
- Width: 0-100% (animated)
- Transition: width 0.3s

**Progress Text:**
- Text-align: Center
- Margin-top: 10px
- Color: White

---

### 4.8 Log Container

**Element:** `.log-container`
**Styling:** Lines 198-224

**Properties:**
- Margin-top: 20px
- Max-height: 400px
- Overflow-y: Auto
- Background: #f8f9fa
- Border: 1px solid #dee2e6
- Border-radius: 6px
- Padding: 15px
- Font-family: 'Courier New', monospace
- Font-size: 12px
- Display: None (initially)

**Log Entry:**
- Margin-bottom: 5px
- Padding: 2px 0
- White-space: pre-wrap

**Entry Types (Colors):**
- `.log-info`: #17a2b8 (cyan)
- `.log-success`: #28a745 (green)
- `.log-warning`: #ffc107 (yellow)
- `.log-error`: #dc3545 (red)
- `.log-debug`: #6f42c1 (purple)
- `.log-api`: #fd7e14, background #fff3cd
- `.log-request`: #0056b3, background #cce5ff
- `.log-response`: #155724, background #d4edda

---

### 4.9 Modal Styling

**Element:** `.modal`
**Styling:** Lines 312-360

**Properties:**
- Display: None (initially)
- Position: Fixed
- Z-index: 1000
- Full-screen overlay
- Background: rgba(0,0,0,0.5)
- Justify-content: Center
- Align-items: Center

**Modal Content:**
- Background: White
- Border-radius: 15px
- Padding: 30px
- Max-width: 90%
- Max-height: 90%
- Overflow-y: Auto
- Position: Relative
- Box-shadow: 0 20px 40px rgba(0,0,0,0.3)

**Close Button:**
- Position: Absolute (top-right)
- Top: 15px, Right: 20px
- Background: None
- Border: None
- Font-size: 24px
- Cursor: Pointer
- Color: #999
- Font-weight: Bold

**Close Hover:**
- Color: #666

---

### 4.10 Dashboard Styling

#### Dashboard Container
**Element:** `.dashboard-container`
**Styling:** Lines 439-447

**Properties:**
- Display: None (initially)
- Margin: 30px 0
- Padding: 25px
- Background: rgba(255,255,255,0.98)
- Backdrop-filter: blur(10px)
- Border-radius: 12px
- Box-shadow: 0 4px 15px rgba(0,0,0,0.1)

#### Dashboard Grid
**Styling:** Lines 467-472

**Properties:**
- Display: Grid
- Grid-template-columns: repeat(auto-fit, minmax(450px, 1fr))
- Gap: 20px
- Margin-bottom: 20px

**Responsive:**
- <1024px: 1 column
- <1200px: Force single column

#### Dashboard Card
**Styling:** Lines 474-541

**Properties:**
- Background: White
- Border-radius: 10px
- Padding: 20px
- Box-shadow: 0 2px 8px rgba(0,0,0,0.08)
- Border: 1px solid #e0e0e0
- Transition: all 0.3s

**Hover:**
- Box-shadow: 0 4px 12px rgba(91,127,204,0.15)
- Transform: translateY(-2px)

**Card Title (H3):**
- Color: #1E3A8A
- Font-size: 1.1em
- Margin-bottom: 15px
- Padding-bottom: 10px
- Border-bottom: 2px solid #f0f0f0
- Display: Flex
- Align-items: Center
- Gap: 8px

**Canvas:**
- Max-height: 300px (desktop)
- Max-height: 250px (<768px)
- Max-height: 200px (<480px)

---

### 4.11 Debug Panel Styling

**Element:** `.debug-panel`
**Styling:** Lines 363-386

**Properties:**
- Margin: 20px auto
- Max-width: 1200px
- Background: rgba(255,255,255,0.95)
- Backdrop-filter: blur(10px)
- Border-radius: 10px
- Padding: 20px
- Box-shadow: 0 2px 10px rgba(0,0,0,0.1)
- Animation: slideDown 0.3s ease-out

**Animation (slideDown):**
```css
from {
  opacity: 0;
  transform: translateY(-20px);
  max-height: 0;
}
to {
  opacity: 1;
  transform: translateY(0);
  max-height: 2000px;
}
```

#### Debug Section
**Styling:** Lines 388-429

**Properties:**
- Margin-bottom: 15px
- Border: 1px solid #ddd
- Border-radius: 8px
- Overflow: Hidden
- Background: White

**Section Header:**
- Background: Gradient (135deg, #6c757d → #495057)
- Color: White
- Padding: 12px 20px
- Cursor: Pointer
- Display: Flex
- Justify-content: Space-between
- Align-items: Center
- Font-weight: 500
- Transition: all 0.3s
- User-select: None

**Header Hover:**
- Background: Gradient (135deg, #5a6268 → #3d4246)

**Toggle Icon:**
- Font-size: 20px
- Transition: transform 0.3s

**Collapsed State:**
- Icon rotates -90deg (points right)

**Section Content:**
- Padding: 20px
- Display: None (initially)

**Expanded State:**
- Display: Block

---

### 4.12 Status Indicators

**Element:** `.status-indicator`
**Styling:** Lines 226-236

**Properties:**
- Display: Inline-block
- Width: 12px
- Height: 12px
- Border-radius: 50% (circle)
- Margin-right: 8px

**States:**
- `.status-ready`: Background #28a745 (green)
- `.status-processing`: Background #ffc107 (yellow)
- `.status-error`: Background #dc3545 (red)

---

### 4.13 Responsive Design

#### Mobile Breakpoints

**<768px (Tablet):**
- Navbar stacks vertically
- Container padding reduced (20px)
- H1 font size reduced (1.8em)
- Background attachment: scroll

**<480px (Phone):**
- Container padding further reduced (15px)
- H1 font size reduced (1.5em)
- Background size: auto 100%

**Dashboard Responsive (<1200px):**
- Single column grid
- Cards take full width

**Dashboard Responsive (<768px):**
- Reduced font sizes
- Card padding reduced (15px)
- Chart heights reduced (250px)
- Competitiveness gauge: 250x250px

**Dashboard Responsive (<480px):**
- Further reduced fonts
- Card padding minimal (12px)
- Chart heights minimal (200px)
- Competitiveness gauge: 200x200px
- Compact spacing throughout

---

## 5. Data Flow Architecture

### 5.1 File Upload Flow

```
User Action
    ↓
[Click Drop Zone] OR [Drag & Drop File]
    ↓
File Input Triggered
    ↓
handleFileSelect(event)
    ↓
currentFile = file
    ↓
Update UI:
  - fileName.textContent = file.name
  - fileSize.textContent = formatFileSize(file.size)
  - fileInfo.style.display = 'block'
  - analyzeBtn.disabled = false
    ↓
Logger.info(`File selected: ${file.name}`)
```

---

### 5.2 Analysis Flow (Pass 1)

```
[Start Analysis Button Click]
    ↓
startAnalysis()
    ↓
Validation: currentFile exists?
    ↓
Get Context Guardrails (optional)
    ↓
Update UI State:
  - analyzeBtn.disabled = true
  - stopBtn.disabled = false
    ↓
ProgressTracker.show()
ProgressTracker.update(10%, "Uploading document...")
    ↓
[API Call] POST /api/upload
    ↓
FormData: { file: currentFile }
    ↓
Response: { filepath: "/path/to/uploaded.pdf" }
    ↓
pdfPath = response.filepath
Logger.success("File uploaded")
    ↓
ProgressTracker.update(20%, "Connecting to HOTDOG AI...")
    ↓
Generate Session ID: `session_${Date.now()}`
currentSessionId = sessionId
    ↓
saveSessionState() → localStorage
    ↓
[SSE Connection] EventSource(`/api/progress/${sessionId}`)
    ↓
activeEventSource.onopen
    ↓
Logger.info("Connected to live progress stream")
autoExpandDebugTools()
showLiveResults()
    ↓
[API Call] POST /api/analyze
    ↓
Request Body: {
  session_id: sessionId,
  pdf_path: pdfPath,
  context_guardrails: guardrails || undefined
}
    ↓
Response: { status: "started" }
    ↓
Logger.success("Analysis started in background")
    ↓
[SSE Event Loop] activeEventSource.onmessage
    ↓
Parse JSON: data = JSON.parse(e.data)
    ↓
Route by event type:
    ├─ 'connected' → Log connection
    ├─ 'document_ingested' → Log pages/windows
    ├─ 'config_loaded' → Log question count
    ├─ 'expert_generated' → Log expert creation
    ├─ 'window_processing' → Update progress (40-90%)
    ├─ 'experts_dispatched' → Log API calls
    ├─ 'experts_complete' → Log answers/tokens
    ├─ 'window_complete' → Log timing, display unitary log
    ├─ 'progress_milestone' → Log general update
    ├─ 'done' → Close SSE, fetchResults()
    └─ 'error' → Close SSE, show error, cleanup
    ↓
[On 'done' Event]
    ↓
fetchResults()
    ↓
[API Call] GET /api/results/${sessionId}
    ↓
Response: {
  success: true,
  result: { sections: [...] },
  statistics: { ... }
}
    ↓
currentAnalysisResult = result
    ↓
Logger.success(`Questions answered: ${stats.questions_answered}/${stats.total_questions}`)
    ↓
displayResults(result)
displayStatistics(statistics)
    ↓
exportBtn.disabled = false
ProgressTracker.hide()
analyzeBtn.disabled = false
stopBtn.disabled = true
    ↓
clearSessionState()
    ↓
Check for unanswered questions:
  If > 0:
    - Show secondPassBanner
    - Enable secondPassBtn
    - Update unansweredCount
```

---

### 5.3 Results Display Flow

```
displayResults(result)
    ↓
Validate: result && result.sections exist?
    ↓
html = '<div style="background: white; ...">'
    ↓
For each section in result.sections:
    ↓
    html += `<h2>${section.section_name}</h2>`
        ↓
    For each question in section.questions:
        ↓
        html += `<div style="margin: 15px 0; ...">`
        html += `<strong>Q: ${q.question}</strong><br>`
            ↓
        If q.answer:
            html += `<p>${q.answer}</p>`
            If q.page_citations:
                html += `<small>Pages: ${q.page_citations.join(', ')}</small>`
        Else:
            html += `<p style="color: #999; ...">Not found in document</p>`
            ↓
        html += `</div>`
    ↓
html += '</div>'
    ↓
resultsContent.innerHTML = html
resultsSection.style.display = 'block'
```

---

### 5.4 Export Flow (Excel Simple Example)

```
[Export Button Click] → showExportMenu()
    ↓
exportMenu.style.display = 'block'
    ↓
[User Selects Format] → exportResults('excel-simple')
    ↓
Validate: currentAnalysisResult exists?
    ↓
Logger.info("Exporting as excel-simple...")
    ↓
exportExcelSimple(currentAnalysisResult)
    ↓
Create Workbook: wb = XLSX.utils.book_new()
    ↓
Create Data Array: wsData = [['Section', 'Question', 'Answer', 'Page Citations']]
    ↓
For each section in result.sections:
    For each question in section.questions:
        wsData.push([
            section.section_name,
            q.question,
            q.answer || 'Not found in document',
            q.page_citations.join(', ')
        ])
    ↓
Create Worksheet: ws = XLSX.utils.aoa_to_sheet(wsData)
    ↓
Set Column Widths: ws['!cols'] = [35, 70, 90, 22]
    ↓
Set Row Heights: ws['!rows'] = [{hpt: 60}, ...]
    ↓
For each cell in worksheet:
    Apply styling:
      - Text wrapping: true
      - Vertical alignment: top
      - Font: Calibri, 15pt
      - If header row: Bold, blue background
    ↓
Append Worksheet: XLSX.utils.book_append_sheet(wb, ws, 'Analysis Results')
    ↓
Write File: XLSX.writeFile(wb, 'cipp_analysis.xlsx')
    ↓
Logger.success("Excel file downloaded")
    ↓
exportMenu.style.display = 'none'
```

---

### 5.5 Session Resume Flow

```
[Page Load] → DOMContentLoaded Event
    ↓
checkForResumeSession()
    ↓
Load from localStorage:
  - sessionId = 'cipp_active_session_id'
  - startTime = 'cipp_session_start_time'
    ↓
sessionId exists?
    ↓ Yes
Calculate elapsed time: (Date.now() - startTime) / 60000
    ↓
elapsed > 30 minutes?
    ↓ Yes → clearSessionState(), abort
    ↓ No
Logger.info(`Found recent session (${elapsed} min ago)`)
currentSessionId = sessionId
    ↓
pollForResults()
    ↓
[API Call] GET /api/results/${sessionId}
    ↓
Response OK?
    ↓ Yes
    data.success?
        ↓ Yes → Analysis complete
        Logger.success("Analysis completed while you were away!")
        displayResults(data.result)
        displayStatistics(data.statistics)
        exportBtn.disabled = false
        clearSessionState()
        ↓ No → Still running
        Logger.info("Analysis may still be running - reconnecting...")
        reconnectSSE()
            ↓
            EventSource(`/api/progress/${sessionId}`)
                ↓
                onmessage: Listen for 'done' or 'error'
                onerror: Retry pollForResults() in 5 seconds
    ↓ No (Network Error)
    Logger.warning("Could not resume session")
    clearSessionState()
```

---

### 5.6 Data Structures

#### File Object (currentFile)
```javascript
{
  name: "bid_spec.pdf",
  size: 1048576,
  type: "application/pdf",
  lastModified: 1234567890,
  // ... (native File object properties)
}
```

#### Question Config (questionConfig)
```javascript
{
  sections: [
    {
      id: "project_info",
      name: "Project Information",
      questions: 10,
      enabled: true
    },
    // ... 9 more sections
  ],
  totalQuestions: 100
}
```

#### Analysis Result (currentAnalysisResult)
```javascript
{
  sections: [
    {
      section_name: "General Project Information",
      questions: [
        {
          id: "Q1",
          question: "What is the project name and location?",
          answer: "City of Springfield CIPP Rehabilitation Project, Springfield, IL",
          page_citations: [1, 2],
          confidence: 0.95
        },
        {
          id: "Q2",
          question: "What is the total project duration?",
          answer: null,
          page_citations: [],
          confidence: null
        },
        // ... more questions
      ]
    },
    // ... more sections
  ]
}
```

#### Statistics Object
```javascript
{
  questions_answered: 85,
  total_questions: 100,
  processing_time: 45.67,
  total_tokens: 125340,
  estimated_cost: "$1.25",
  average_confidence: "92.3%"
}
```

#### SSE Event Data Examples

**connected:**
```json
{
  "event": "connected",
  "message": "Progress stream established"
}
```

**document_ingested:**
```json
{
  "event": "document_ingested",
  "total_pages": 45,
  "window_count": 5
}
```

**window_processing:**
```json
{
  "event": "window_processing",
  "window_num": 3,
  "total_windows": 5,
  "pages": "11-20"
}
```

**window_complete:**
```json
{
  "event": "window_complete",
  "window_num": 3,
  "answers_found": 18,
  "processing_time": 8.4,
  "unitary_log_markdown": "## Window 3 Complete\n\n**Answers Found:** 18\n..."
}
```

**done:**
```json
{
  "event": "done",
  "message": "Analysis complete"
}
```

**error:**
```json
{
  "event": "error",
  "error": "OpenAI API rate limit exceeded"
}
```

---

## 6. Configuration System

### 6.1 Question Configuration Structure

**Source File:** `config/cipp_questions_default.json`
**Lines:** 1-677

**Top-Level Structure:**
```json
{
  "config_name": "CIPP Bid Specification Analysis",
  "version": "1.0",
  "description": "Default question configuration for analyzing CIPP (Cured-In-Place Pipe) project specifications",
  "sections": [ ... ]
}
```

---

### 6.2 Section Structure

**Total Sections:** 10
**Total Questions:** 100

Each section contains:
```json
{
  "section_id": "unique_identifier",
  "section_name": "Human-Readable Name",
  "description": "Purpose of this section",
  "questions": [ ... ]
}
```

**Section List:**

1. **general_info** - General Project Information (Q1-Q10)
2. **materials_standards** - Materials & Technical Standards (Q11-Q20)
3. **installation_process** - Installation Methods & Procedures (Q21-Q30)
4. **testing_qa** - Testing & Quality Assurance (Q31-Q40)
5. **safety_compliance** - Safety & Environmental Compliance (Q41-Q50)
6. **equipment_resources** - Equipment & Resource Requirements (Q51-Q60)
7. **warranty_closeout** - Warranty & Project Closeout (Q61-Q70)
8. **special_conditions** - Special Conditions & Constraints (Q71-Q80)
9. **pricing_payment** - Pricing Structure & Payment (Q81-Q90)
10. **experience_qualifications** - Contractor Experience & Qualifications (Q91-Q100)

---

### 6.3 Question Structure

Each question contains:
```json
{
  "id": "Q1",
  "text": "What is the project name and location?",
  "required": true,
  "expected_type": "string"
}
```

**Field Definitions:**

- **id:** Unique identifier (Q1-Q100)
- **text:** The question to be answered
- **required:** Boolean - critical question flag
- **expected_type:** Data type hint for answer validation

**Expected Types:**
- `"string"` - Text answer
- `"number"` - Numeric value
- `"date"` - Date/deadline
- `"technical_spec"` - Technical specification (may include units, ranges, standards)

---

### 6.4 Sample Questions by Section

#### General Project Information (Q1-Q10)
- Q1: Project name and location?
- Q2: Total project duration or timeline?
- Q3: Total linear footage of pipe to be rehabilitated?
- Q4: Pipe sizes (diameters) included?
- Q5: Project budget or estimated cost?
- Q6: Submission deadlines for bids or proposals?
- Q7: Project owner or contracting authority?
- Q8: Pre-bid meetings or site visits scheduled?
- Q9: Bonding and insurance requirements?
- Q10: Payment terms and schedule?

#### Materials & Technical Standards (Q11-Q20)
- Q11: Resin type required (polyester, vinyl ester, epoxy)?
- Q12: ASTM standards for CIPP materials?
- Q13: Required design thickness of the liner?
- Q14: Flexural strength requirements?
- Q15: Flexural modulus requirements?
- Q16: Specific felt material requirements?
- Q17: Chemical resistance requirements?
- Q18: Liner permeability requirements?
- Q19: Certification or testing documentation for materials?
- Q20: Material submittal or approval requirements?

#### Installation Methods & Procedures (Q21-Q30)
- Q21: Installation method specified (inversion, pull-in-place, other)?
- Q22: Curing method required (steam, hot water, UV, ambient)?
- Q23: Minimum and maximum curing temperature requirements?
- Q24: Required curing duration?
- Q25: Pre-installation cleaning or inspection requirements?
- Q26: Bypass pumping requirements?
- Q27: Service lateral reconnection requirements?
- Q28: End seal requirements?
- Q29: Manhole-to-manhole or continuous lining requirements?
- Q30: Requirements for monitoring curing parameters?

*(Pattern continues for all 100 questions)*

---

### 6.5 Configuration Loading

**Client-Side (HTML):**
- Hardcoded default configuration (Lines 1983-2010)
- 10 sections with 10 questions each
- All sections enabled by default

**Expected Server-Side:**
- Load from `config/cipp_questions_default.json`
- Allow customization per project
- Support import/export of custom configs

---

### 6.6 Modification System (Question Manager)

**Modal UI:** Lines 1028-1071

**Features:**
1. **Section Selection:** Dropdown to choose section
2. **Section Enable/Disable:** Checkbox toggle
3. **Section Rename:** Text input
4. **Question List:** Scrollable editor
5. **Add New Question:** Dynamic addition
6. **Delete Section:** Remove entire section
7. **Import Config:** Load JSON file
8. **Export Config:** Download JSON file

**Functions (Stub):**
- `loadSectionForEdit()` - Populate editor with section data
- `toggleSectionEnabled()` - Toggle section active state
- `updateSectionName()` - Rename section
- `addNewQuestion()` - Add question to section
- `deleteCurrentSection()` - Remove section
- `saveQuestions()` - Persist changes
- `importQuestions(event)` - Load JSON config
- `exportQuestions()` - Download JSON config

---

## 7. External Dependencies

### 7.1 JavaScript Libraries

#### SheetJS (XLSX)
**Source:** https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js
**Line:** 8
**Purpose:** Excel file generation (client-side)
**Used In:**
- `exportExcelSimple()` - Styled table export

**Key Functions Used:**
- `XLSX.utils.book_new()` - Create workbook
- `XLSX.utils.aoa_to_sheet()` - Array to worksheet
- `XLSX.utils.book_append_sheet()` - Add worksheet to workbook
- `XLSX.writeFile()` - Download file

#### Chart.js
**Source:** https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js
**Line:** 10
**Purpose:** Interactive dashboard charts
**Used In:** Dashboard section (competitiveness gauge, risk matrix, cost drivers, etc.)

**Charts Expected:**
- Doughnut (Competitiveness Gauge)
- Bar (Risk Assessment)
- Pie (Cost Drivers)
- Radar (Compliance)
- Horizontal Bar (Timeline)

**Note:** Chart rendering code not shown in HTML (likely server-side or separate JS file)

---

### 7.2 Images & Assets

#### Background Image
**Path:** `/shared/assets/images/bg3.jpg`
**Line:** 32
**Usage:** Fixed background layer
**Filters:** brightness(0.75)

#### Company Logo
**Path:** `/shared/assets/images/logo.png`
**Line:** 729
**Usage:** Navbar branding
**Dimensions:** 40px height (width auto)

---

### 7.3 Font Dependencies

**Primary Font Stack:**
```css
'Segoe UI', Tahoma, Geneva, Verdana, sans-serif
```

**Monospace Font Stack (Logs):**
```css
'Courier New', monospace
```

**No External Font Loading:** All system fonts

---

## 8. State Management

### 8.1 Global State Variables

**Location:** Lines 1078-1086

```javascript
let currentFile = null;              // File: Selected document
let currentSessionId = null;         // String: Active session ID
let currentAnalysisResult = null;    // Object: Completed results
let activeEventSource = null;        // EventSource: SSE connection
let questionConfig = {               // Object: Question configuration
  sections: [],
  totalQuestions: 0
};
```

---

### 8.2 LocalStorage State

**Keys Used:**
- `cipp_active_session_id` - Resume support
- `cipp_session_start_time` - Resume timeout validation

**Lifecycle:**
- **Set:** When analysis starts (`saveSessionState()`)
- **Read:** On page load (`checkForResumeSession()`)
- **Clear:** On completion, stop, or error (`clearSessionState()`)

---

### 8.3 UI State

**Button States:**

| Button | Initial | During Analysis | After Analysis |
|--------|---------|----------------|----------------|
| `analyzeBtn` | Disabled | Disabled | Enabled |
| `stopBtn` | Disabled | Enabled | Disabled |
| `exportBtn` | Disabled | Disabled | Enabled |
| `secondPassBtn` | Hidden | Hidden | Shown (if unanswered) |

**Section Visibility:**

| Section | Initial | During Analysis | After Analysis |
|---------|---------|----------------|----------------|
| `progressContainer` | Hidden | Visible | Hidden |
| `resultsSection` | Hidden | Visible (loading) | Visible (results) |
| `dashboardSection` | Hidden | Hidden | Visible (optional) |
| `secondPassBanner` | Hidden | Hidden | Visible (if unanswered) |
| `logContainer` | Hidden | Visible (auto-expand) | Visible |

---

### 8.4 State Transitions

#### File Upload State
```
No File → File Selected
  - currentFile: null → File object
  - analyzeBtn: disabled → enabled
  - fileInfo: hidden → visible
```

#### Analysis State
```
Ready → Analyzing → Complete

Ready:
  - currentSessionId: null
  - currentAnalysisResult: null
  - activeEventSource: null
  - Progress: hidden
  - Results: hidden

Analyzing:
  - currentSessionId: set
  - currentAnalysisResult: null
  - activeEventSource: connected
  - Progress: visible, updating
  - Results: visible (loading state)
  - Buttons: analyze disabled, stop enabled

Complete:
  - currentSessionId: null (cleared)
  - currentAnalysisResult: set
  - activeEventSource: closed
  - Progress: hidden
  - Results: visible (full results)
  - Buttons: analyze enabled, stop disabled, export enabled
```

---

## 9. API Endpoints

### 9.1 File Upload

**Endpoint:** `POST /api/upload`
**Request:**
```javascript
FormData: {
  file: File object
}
```
**Response:**
```json
{
  "success": true,
  "filepath": "/uploads/bid_spec_1234567890.pdf"
}
```

**Client Function:** `startAnalysis()` (Line 1219)

---

### 9.2 Start Analysis

**Endpoint:** `POST /api/analyze`
**Request:**
```json
{
  "session_id": "session_1234567890",
  "pdf_path": "/uploads/bid_spec_1234567890.pdf",
  "context_guardrails": "Optional constraint text"
}
```
**Response:**
```json
{
  "status": "started",
  "session_id": "session_1234567890"
}
```

**Client Function:** `startAnalysis()` (Line 1327)

---

### 9.3 Progress Stream (SSE)

**Endpoint:** `GET /api/progress/{session_id}`
**Protocol:** Server-Sent Events (EventSource)
**Response:** Stream of JSON events

**Event Types:**
- `connected`
- `document_ingested`
- `config_loaded`
- `expert_generated`
- `window_processing`
- `experts_dispatched`
- `experts_complete`
- `window_complete`
- `progress_milestone`
- `done`
- `error`

**Client Function:** `startAnalysis()` (Line 1239)

---

### 9.4 Get Results

**Endpoint:** `GET /api/results/{session_id}`
**Response:**
```json
{
  "success": true,
  "result": {
    "sections": [
      {
        "section_name": "General Project Information",
        "questions": [
          {
            "id": "Q1",
            "question": "What is the project name?",
            "answer": "Springfield CIPP Project",
            "page_citations": [1, 2],
            "confidence": 0.95
          }
        ]
      }
    ]
  },
  "statistics": {
    "questions_answered": 85,
    "total_questions": 100,
    "processing_time": 45.67,
    "total_tokens": 125340,
    "estimated_cost": "$1.25",
    "average_confidence": "92.3%"
  }
}
```

**Client Function:** `fetchResults()` (Line 1364)

---

### 9.5 Stop Analysis

**Endpoint:** `POST /api/stop/{session_id}`
**Response:**
```json
{
  "success": true,
  "message": "Analysis stopped"
}
```

**Client Function:** `stopAnalysis()` (Line 1482)

---

### 9.6 Export Excel Dashboard

**Endpoint:** `GET /api/export/excel-dashboard/{session_id}`
**Response:** Binary Excel file (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
**Filename:** `CIPP_Executive_Dashboard.xlsx`

**Client Function:** `exportExcelDashboard()` (Line 2223)

---

## 10. Event Handling

### 10.1 DOM Events

#### File Input Change
**Element:** `#fileInput`
**Event:** `change`
**Handler:** `handleFileSelect(event)`
**Setup:** Line 2025

#### Drop Zone Events
**Element:** `#fileUpload`

| Event | Handler | Purpose |
|-------|---------|---------|
| `dragover` | Inline | Prevent default, change border color |
| `dragleave` | Inline | Reset border color |
| `drop` | Inline | Extract files, trigger handleFileSelect |
| `click` | Inline (onclick) | Trigger file input click |

**Setup:** Lines 2036-2054

---

### 10.2 Button Click Events

**Inline onclick Handlers:**

| Button ID | onclick Handler |
|-----------|----------------|
| `analyzeBtn` | `startAnalysis()` |
| `stopBtn` | `stopAnalysis()` |
| `secondPassBtn` | `runSecondPass()` |
| `exportBtn` | `showExportMenu()` |
| Test Document Button | `loadTestDocument()` |
| Manage Questions | `showQuestionManager()` |
| Add Section | `addQuestionSection()` |
| Export Questions | `exportQuestions()` |
| Settings | `showSettings()` |

---

### 10.3 Server-Sent Events (SSE)

**EventSource:** `/api/progress/{session_id}`

**Event Handlers:**

| Event | Handler | Purpose |
|-------|---------|---------|
| `onopen` | Inline | Log connection, auto-expand UI |
| `onmessage` | Inline | Parse JSON, route by event type |
| `onerror` | Inline | Log disconnection |

**Setup:** Line 1240

**Message Router:** Lines 1250-1320

---

### 10.4 Modal Events

**Settings Modal:**
- Open: `showSettings()` (stub)
- Close: `hideSettings()` (stub)
- Save: `saveSettings()` (stub)

**Question Manager Modal:**
- Open: `showQuestionManager()` (stub)
- Close: `hideQuestionManager()` (stub)
- Section Select: `loadSectionForEdit()` (onchange)
- Section Enabled: `toggleSectionEnabled()` (onchange)
- Section Name: `updateSectionName()` (onchange)
- Add Question: `addNewQuestion()`
- Delete Section: `deleteCurrentSection()`
- Save: `saveQuestions()`
- Import: `importQuestions(event)` (file input onchange)

---

### 10.5 Input Events

**Context Guardrails:**
- Element: `#contextGuardrails`
- Event: `oninput`
- Handler: `saveContextGuardrails()` (not shown - likely saves to localStorage)

**Chunk Size:**
- Element: `#chunkSize`
- Event: None (value read during analysis)

**GPT Model:**
- Element: `#gptModel`
- Event: None (value read on save settings)

---

## 11. Summary & Key Insights

### 11.1 Architecture Pattern

**Type:** Single-Page Application (SPA) with Server-Side Processing

**Communication:**
- REST API for commands (upload, analyze, stop)
- Server-Sent Events (SSE) for real-time progress
- Polling fallback for resume support

**State Management:**
- Global variables for runtime state
- LocalStorage for persistence (resume support)
- No framework (vanilla JavaScript)

---

### 11.2 Key Features Summary

1. **Multi-Format File Upload** (PDF, TXT, DOCX, RTF)
2. **Real-Time Progress Tracking** (SSE with detailed logging)
3. **100 Configurable Questions** (10 sections, 10 questions each)
4. **Live Analysis Window** (Markdown-formatted updates)
5. **Comprehensive Export System** (6 formats: Excel Dashboard, Excel Simple, CSV, HTML, Markdown, JSON)
6. **Session Resumption** (Laptop sleep recovery via localStorage)
7. **Second Pass Analysis** (Enhanced scrutiny for unanswered questions)
8. **Interactive Dashboards** (Chart.js visualizations)
9. **Debug Tools Panel** (Collapsible sections, activity log, API testing)
10. **Context Guardrails** (Optional global constraints)

---

### 11.3 Technical Debt & Gaps

**Stub Functions (Not Implemented):**
- `loadTestDocument()`
- `showQuestionManager()` / `hideQuestionManager()`
- `addQuestionSection()`
- `exportQuestions()` / `importQuestions()`
- `showSettings()` / `hideSettings()` / `saveSettings()`
- `addNewSectionInManager()`
- `deleteCurrentSection()`
- `loadSectionForEdit()`
- `toggleSectionEnabled()`
- `updateSectionName()`
- `addNewQuestion()`
- `saveQuestions()`
- `testApiConnection()`
- `saveContextGuardrails()`
- `toggleDashboardPanel()`
- `refreshDashboards()`
- Dashboard chart rendering

**Missing Features:**
- Question manager full implementation
- Settings persistence
- Test document loader
- API connection testing
- Dashboard chart initialization
- Second pass backend integration

---

### 11.4 Complexity Metrics

**Total Lines:** 2,257
**JavaScript Lines:** ~1,200 (53%)
**CSS Lines:** ~700 (31%)
**HTML Lines:** ~357 (16%)

**Functions:** 40+ (including stubs)
**Classes:** 2 (Logger, ProgressTracker)
**Global Variables:** 5
**API Endpoints:** 6
**SSE Event Types:** 11
**Export Formats:** 6
**Modal Windows:** 2
**Debug Sections:** 4
**Dashboard Charts:** 5

---

### 11.5 Rebuild Recommendations

#### Priority 1 (Core Functionality)
1. File upload system
2. Analysis workflow (SSE + API integration)
3. Results display
4. Logger + Progress tracker
5. Basic export (CSV, JSON)

#### Priority 2 (Enhanced Features)
1. Excel export (simple + dashboard)
2. HTML/Markdown export
3. Session resumption
4. Debug panel
5. Context guardrails

#### Priority 3 (Advanced Features)
1. Question manager (full implementation)
2. Settings modal
3. Dashboard charts
4. Second pass analysis
5. Test document loader

#### Code Quality Improvements
1. **Modularize:** Break into separate JS files (api.js, ui.js, export.js, logger.js)
2. **Framework:** Consider React/Vue for complex state management
3. **TypeScript:** Add type safety
4. **Error Handling:** Centralize error handling, user-friendly messages
5. **Testing:** Add unit tests, integration tests
6. **Accessibility:** ARIA labels, keyboard navigation
7. **Performance:** Lazy load charts, virtualize long lists

---

## Appendix A: File Structure Reference

```
cipp_analyzer_clean.html (2,257 lines)
│
├── Head (1-11)
│   ├── Meta tags
│   ├── Title
│   ├── SheetJS CDN
│   └── Chart.js CDN
│
├── Style (11-723)
│   ├── Global reset
│   ├── Background layers (body::before, body::after)
│   ├── Container system
│   ├── Typography
│   ├── Form elements
│   ├── Buttons
│   ├── Progress bar
│   ├── Log container
│   ├── Modals
│   ├── Debug panel
│   ├── Dashboard
│   └── Responsive breakpoints
│
├── Body (724-2257)
│   ├── Navbar (727-733)
│   ├── Main Container (735-999)
│   │   ├── Header (736-739)
│   │   ├── File Upload Section (742-754)
│   │   ├── Question Config Section (757-793)
│   │   ├── Analysis Controls (796-834)
│   │   ├── Debug Panel (837-908)
│   │   ├── Progress Bar (911-916)
│   │   ├── Live Results (922-928)
│   │   └── Dashboards (930-998)
│   │
│   ├── Settings Modal (1002-1025)
│   ├── Question Manager Modal (1028-1071)
│   │
│   └── Script (1073-2257)
│       ├── Global State (1078-1086)
│       ├── Logger Class (1092-1115)
│       ├── ProgressTracker Class (1121-1134)
│       ├── File Handling (1140-1183)
│       ├── Analysis Functions (1189-1504)
│       ├── Display Functions (1400-1469)
│       ├── Export Functions (1510-1846)
│       ├── State Management (1868-1961)
│       ├── Initialization (1967-2055)
│       ├── UI Helpers (2061-2146)
│       └── Stubs (2152-2256)
```

---

## Appendix B: Color Reference

### Primary Palette
| Color Name | Hex | RGB | Usage |
|------------|-----|-----|-------|
| Primary Blue | #5B7FCC | 91, 127, 204 | Buttons, accents |
| Dark Blue | #1E3A8A | 30, 58, 138 | Navbar, headers |
| Success Green | #28a745 | 40, 167, 69 | Success states |
| Warning Yellow | #ffc107 | 255, 193, 7 | Warning states |
| Error Red | #dc3545 | 220, 53, 69 | Error states |
| Info Cyan | #17a2b8 | 23, 162, 184 | Info logs |
| Debug Purple | #6f42c1 | 111, 66, 193 | Debug logs |

### Neutral Palette
| Color Name | Hex | RGB | Usage |
|------------|-----|-----|-------|
| White | #ffffff | 255, 255, 255 | Text, backgrounds |
| Light Gray | #f8f9fa | 248, 249, 250 | Backgrounds |
| Medium Gray | #6c757d | 108, 117, 125 | Secondary text |
| Border Gray | #ddd | 221, 221, 221 | Borders |
| Dark Gray | #333 | 51, 51, 51 | Body text |

---

**End of Inventory Document**
