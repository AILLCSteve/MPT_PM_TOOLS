# Project Digest Synopsis — ssREFINEMENT (CIPP Dashboard Generator)

**Generated**: 2025-12-06
**Purpose**: Comprehensive technical digest for faster, better, and more accurate refactoring and brainstorming

---

## 1. High-Level Summary (175 words)

**ssREFINEMENT** is a CIPP (Cured-In-Place Pipe) project dashboard generator that transforms Excel shot schedules into comprehensive visual dashboards. The system processes pipe rehabilitation project data and generates analytical summaries with multiple visualization approaches.

**Core Capabilities:**
- Ingests CIPP shot schedule Excel files (*.xlsx) with project segment data
- Computes project stage based on completion date hierarchies (6 stages: Not Started → Grouted/Done)
- Generates 5 analytical summary tables (stage footage, pipe size analysis, length distribution, easement/traffic metrics)
- Produces 5 interactive visualizations (progress charts, distribution graphs, comparative analytics)
- Outputs dashboards via 3 different approaches: (1) openpyxl native Excel charts, (2) xlsxwriter enhanced formatting, (3) Plotly image embedding

**Dual Application Architecture:**
1. **Flask web app** (`app.py`) — upload, process, web-based interactive dashboards with Plotly.js
2. **Dash web app** (`app_dash.py`) — modern, reactive dashboarding with enhanced UX, radar charts, and comprehensive visualizations

**Technology Stack:** Python, Flask, Dash, openpyxl, xlsxwriter, Plotly, Pandas, Bootstrap 5

**Domain:** Construction project management, specifically CIPP pipe rehabilitation tracking and progress visualization

---

## 2. Architecture & Major Components

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION LAYER                   │
├─────────────────────────────────────────────────────────────┤
│  Flask Web App (app.py)          Dash Web App (app_dash.py) │
│  - Upload interface               - Modern reactive UI       │
│  - Session management             - Real-time visualizations │
│  - Download endpoints             - Enhanced charts          │
└─────────────────┬───────────────────────────┬───────────────┘
                  │                           │
                  ▼                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  CORE PROCESSING LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  CIPPDataProcessor (data_processor.py)                      │
│  - Excel file ingestion (openpyxl)                          │
│  - Data validation & filtering                               │
│  - Stage computation (priority-based)                        │
│  - 5 summary table generation                                │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                  VISUALIZATION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  ExcelDashboardGenerator (excel_generator.py)               │
│  - Approach 1: openpyxl native charts                       │
│  - Approach 2: xlsxwriter enhanced charts                   │
│  - Approach 3: Plotly images embedded in Excel              │
│                                                              │
│  ExcelDashboardGeneratorV2 (excel_generator_v2.py)          │
│  - Modifies ORIGINAL Excel files (preserves source data)    │
│  - Adds Dashboard & Dashboard_Data sheets                   │
└─────────────────────────────────────────────────────────────┘

        ▼                           ▼                 ▼
   Excel Files            Web Visualizations      Session Storage
   (outputs/)             (Plotly.js/Dash)       (In-memory dict)
```

### 2.2 Component Breakdown

#### **Core Components**

1. **`data_processor.py`** — `CIPPDataProcessor` class
   - **Responsibility:** Single source of truth for data ingestion, validation, and analytical table generation
   - **Key Principle:** SRP - all data processing logic centralized
   - **Dependencies:** openpyxl, typing, collections

2. **`excel_generator.py`** — `ExcelDashboardGenerator` class
   - **Responsibility:** Generate NEW Excel workbooks with dashboards (3 approaches)
   - **Key Principle:** Strategy pattern - 3 different generation strategies
   - **Dependencies:** openpyxl, xlsxwriter, plotly, Pillow, kaleido

3. **`excel_generator_v2.py`** — `ExcelDashboardGeneratorV2` class
   - **Responsibility:** Modify ORIGINAL Excel files by adding dashboard sheets
   - **Key Principle:** SRP - preserves original data, augments with dashboards
   - **Dependencies:** openpyxl, xlsxwriter, plotly, shutil

4. **`app.py`** — Flask web application
   - **Responsibility:** HTTP server, file upload, session management, API endpoints
   - **Key Principle:** MVC pattern - controller layer for web requests
   - **Dependencies:** Flask, werkzeug, plotly, json

5. **`app_dash.py`** — Dash web application
   - **Responsibility:** Modern reactive dashboarding with enhanced UX
   - **Key Principle:** Component-based architecture, reactive programming
   - **Dependencies:** Dash, dash-bootstrap-components, plotly, pandas

#### **Supporting Components**

- **`templates/index.html`** — Upload page for Flask app
- **`templates/dashboard.html`** — Dashboard display page for Flask app
- **`static/css/style.css`** — Custom styling (Bootstrap 5 enhancements)

### 2.3 Bounded Contexts (DDD)

| Context | Components | Domain Language |
|---------|-----------|-----------------|
| **Data Ingestion** | `CIPPDataProcessor.load_data()` | VIDEO ID, Line Segment, Pipe Size, Map Length, Stage |
| **Stage Computation** | `CIPPDataProcessor._compute_stage()` | Grout State Date, Final Post TV Date, Lining Date, Ready to Line, Prep Complete |
| **Analytics** | `CIPPDataProcessor.get_*_summary()` | Segment Count, Total Feet, Pct of Total Feet, Length Bins |
| **Visualization** | Excel generators, Flask/Dash apps | Charts, Tables, Dashboard, Approach |
| **Session Management** | Flask/Dash apps | session_id, processed_data, uploads, outputs |

### 2.4 Data Flow — Critical Path

**User Upload → Dashboard Generation (End-to-End)**

1. **Upload** (Flask: `/upload` or Dash: `process_upload` callback)
   - User uploads `.xlsx` file via web form
   - File saved to `uploads/` with timestamp prefix
   - Returns: `session_id`

2. **Data Processing** (`CIPPDataProcessor`)
   ```
   load_data() →
     ├─ locate sheet (find "MOINES" or "SHOT")
     ├─ parse headers (row 1)
     ├─ validate segments (VIDEO ID ≥ 1, Map Length > 0)
     ├─ extract data (11 columns)
     └─ compute stage (6-level priority logic)
   ```

3. **Analytics Generation** (`get_all_tables()`)
   - 5 tables computed in parallel (independent calculations)
   - Each table: filter → aggregate → calculate percentages

4. **Visualization** (3 approaches)
   - **Approach 1:** openpyxl `BarChart`, `PieChart` → native Excel objects
   - **Approach 2:** xlsxwriter charts with enhanced styling → Excel file
   - **Approach 3:** Plotly `go.Figure` → PNG images → embedded in Excel

5. **Web Dashboard** (Flask or Dash)
   - Render 5 Plotly.js interactive charts
   - Display 5 summary tables with formatting
   - Provide download links for 3 Excel approaches

---

## 3. Data Models & Integrations

### 3.1 Domain Entities & Value Objects

#### **Entity: Segment** (core domain object)
```python
{
    "video_id": int,              # Entity ID (≥1)
    "line_segment": str,          # Segment name
    "pipe_size": int/float,       # Pipe diameter (inches)
    "map_length": float,          # Segment length (feet)
    "prep_complete": bool,        # Stage flag
    "ready_to_line": bool,        # Stage flag
    "lining_date": date/None,     # Completion date
    "final_post_tv_date": date/None,  # Completion date
    "grout_state_date": date/None,    # Completion date
    "easement": bool,             # Operational constraint
    "traffic_control": bool,      # Operational constraint
    "stage": str                  # Computed value (6 stages)
}
```

**Invariants:**
- `video_id >= 1` (validation in `_is_valid_segment`)
- `map_length > 0` (validation in `_is_valid_segment`)
- `stage` is always one of 6 defined stages (STAGES constant)

#### **Value Object: Stage** (computed, immutable)
Priority hierarchy (first match wins):
1. `Grout State Date` not blank → `"Grouted/Done"`
2. `Final Post TV Date` not blank → `"Post TV Complete"`
3. `Lining Date` not blank → `"Lined"`
4. `Ready to Line` truthy → `"Ready to Line"`
5. `Prep Complete` truthy → `"Prep Complete"`
6. Otherwise → `"Not Started"`

**Implemented in:** `CIPPDataProcessor._compute_stage()` (data_processor.py:126-139)

#### **Value Object: Length Bin** (configuration)
```python
{
    "label": str,           # Display name (e.g., "0–50")
    "min": int,             # Minimum length (inclusive)
    "max": int/None         # Maximum length (inclusive, None = open-ended)
}
```

**Default bins** (configurable via `LENGTH_BINS` constant):
- 0–50, 51–150, 151–250, 251–350, 351+

### 3.2 External Contracts & Integrations

#### **Input: Excel File Schema**

**Required Sheet Name:**
- Must contain "MOINES" or "SHOT" (case-insensitive)
- Example: "WEST DES MOINES, IA Shot Schedu"

**Required Columns** (header row 1):

| Column Name | Type | Validation | Usage |
|------------|------|------------|-------|
| VIDEO ID | numeric | ≥ 1 | Segment identifier |
| Line Segment | string | - | Segment name |
| Pipe Size | numeric | - | Pipe diameter (inches) |
| Map Length | numeric | > 0 | Segment length (feet) |
| Prep Complete | boolean | truthy check | Stage computation |
| Ready to Line - Certified by Prep Crew Lead | boolean | truthy check | Stage computation |
| Lining Date | date/blank | - | Stage computation |
| Final Post TV Date | date/blank | - | Stage computation |
| Grout State Date | date/blank | - | Stage computation |
| Easement | boolean | truthy check | Operational metrics |
| Traffic Control | boolean | truthy check | Operational metrics |

**Truthy values:** `True`, `"TRUE"`, `"YES"`, `"Y"`, `"Yes"`, `1` (implemented in `_is_truthy()`)

#### **Output: 5 Summary Tables**

**Table 1: Stage_Footage_Summary**
```python
{
    "Stage": str,                   # One of 6 stages
    "Segment_Count": int,           # Number of segments
    "Total_Feet": float,            # Sum of map_length
    "Pct_of_Total_Feet": float      # Percentage (0.0-1.0)
}
```
**Location in Excel:** Dashboard_Data!A1:D7

**Table 2: Stage_by_PipeSize**
```python
{
    "Pipe Size": int/float,
    "Not Started": float,           # Footage by stage
    "Prep Complete": float,
    "Ready to Line": float,
    "Lined": float,
    "Post TV Complete": float,
    "Grouted/Done": float,
    "Total_Feet": float             # Row sum
}
```
**Location in Excel:** Dashboard_Data!A10:H{10+n}

**Table 3: Pipe_Size_Mix**
```python
{
    "Pipe Size": int/float,
    "Segment_Count": int,
    "Total_Feet": float,
    "Avg_Length_ft": float,
    "Pct_of_Total_Feet": float
}
```
**Location in Excel:** Dashboard_Data!A19:E{19+n}

**Table 4: Length_Bins**
```python
{
    "Length_Bin_Label": str,        # e.g., "0–50"
    "Min_Length_ft": int,
    "Max_Length_ft": int/None,
    "Segment_Count": int,
    "Total_Feet": float,
    "Pct_of_Total_Feet": float
}
```
**Location in Excel:** Dashboard_Data!A27:F32

**Table 5: Easement_Traffic_Summary**
```python
{
    "Category": str,                # "Easement" or "Traffic Control"
    "Flag": str,                    # "Yes" or "No"
    "Segment_Count": int,
    "Total_Feet": float,
    "Pct_of_Total_Feet": float
}
```
**Location in Excel:** Dashboard_Data!A37:E41

#### **Output: Excel Files (3 Approaches)**

**Approach 1:** openpyxl native charts
- Native Excel `BarChart`, `PieChart` objects
- Fully interactive in Excel
- Lightweight file size
- Best for: Standard Excel workflows

**Approach 2:** xlsxwriter enhanced charts
- Superior formatting and styling
- Gradients, data labels, enhanced legends
- Best for: Professional presentations

**Approach 3:** Plotly images
- PNG images embedded in Excel
- Publication-quality visuals
- Static (not interactive in Excel)
- Best for: Reports and documentation

#### **API Endpoints (Flask app)**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Upload page |
| `/upload` | POST | Handle file upload, returns session_id |
| `/dashboard/<session_id>` | GET | Display dashboard HTML |
| `/api/charts/<session_id>/<approach>` | GET | Return chart JSON (plotly/chartjs) |
| `/api/tables/<session_id>` | GET | Return all table data |
| `/download/<session_id>/<approach>` | GET | Download Excel file |

### 3.3 Session Management & State

**In-Memory Storage** (Flask app):
```python
processed_data = {
    "<session_id>": {
        "processor": CIPPDataProcessor,  # Instance
        "tables": dict,                  # 5 tables
        "filepath": str,                 # Uploaded file path
        "filename": str,                 # Original filename
        "output_files": {                # Generated Excel files
            "approach1": str,
            "approach2": str,
            "approach3": str
        }
    }
}
```

**Session ID Format:** `YYYYMMDD_HHMMSS` (timestamp)

**File Storage:**
- Uploads: `uploads/<timestamp>_<filename>.xlsx`
- Outputs: `outputs/<session_id>_<approach>.xlsx`

**⚠️ Production Concerns:**
- In-memory storage NOT suitable for production (use Redis/DB)
- No session cleanup (memory leak over time)
- No authentication/authorization
- Hardcoded secret key (`app.secret_key`)

---

## 4. Critical Flows & Behaviors

### 4.1 Stage Computation Flow

**Function:** `CIPPDataProcessor._compute_stage(segment: Dict) -> str`
**Location:** data_processor.py:126-139

**Algorithm:**
```python
if segment["grout_state_date"] is not None:
    return "Grouted/Done"
elif segment["final_post_tv_date"] is not None:
    return "Post TV Complete"
elif segment["lining_date"] is not None:
    return "Lined"
elif segment["ready_to_line"]:
    return "Ready to Line"
elif segment["prep_complete"]:
    return "Prep Complete"
else:
    return "Not Started"
```

**Critical:** Order matters! First truthy condition wins.

**Edge Cases:**
- All dates blank + flags False → "Not Started"
- Multiple dates present → highest priority stage wins
- Date parsing handled by openpyxl (`data_only=True`)

### 4.2 Data Loading & Validation Flow

**Function:** `CIPPDataProcessor.load_data() -> List[Dict]`
**Location:** data_processor.py:38-94

**Step-by-step:**

1. **Load workbook** (openpyxl with `data_only=True` to evaluate formulas)
   ```python
   wb = load_workbook(self.file_path, data_only=True)
   ```

2. **Locate sheet** (flexible sheet name matching)
   ```python
   if self.sheet_name not in wb.sheetnames:
       for sheet in wb.sheetnames:
           if "MOINES" in sheet.upper() or "SHOT" in sheet.upper():
               self.sheet_name = sheet
               break
   ```

3. **Parse headers** (row 1, build column index map)
   ```python
   headers = {}
   for col_idx, cell in enumerate(ws[1], start=1):
       if cell.value:
           headers[str(cell.value).strip()] = col_idx
   ```

4. **Iterate rows** (starting from row 2)
   - Get VIDEO ID and Map Length
   - Validate: `video_id >= 1 and map_length > 0`
   - If invalid: skip row (continue to next)

5. **Extract segment data** (11 fields)
   - Use `_get_cell_value()` for safe access
   - Use `_is_truthy()` for boolean conversion
   - Convert dates (handled by openpyxl)

6. **Compute stage** (call `_compute_stage()`)

7. **Store** in `self.segments` list

8. **Calculate total footage** (sum of all map_length)

**Returns:** List of segment dictionaries

**Error Handling:**
- Sheet not found: raises `ValueError` with available sheet names
- Missing columns: returns `None` from `_get_cell_value()`, handled gracefully
- Invalid data types: `_is_valid_segment()` catches exceptions, returns False

### 4.3 Table Generation Flows

#### **Table 1: Stage Footage Summary**
**Function:** `get_stage_footage_summary()`
**Location:** data_processor.py:141-160

1. Initialize `defaultdict` for each stage (count=0, footage=0)
2. Iterate all segments:
   - Increment count for segment's stage
   - Add map_length to footage for segment's stage
3. Build result list in STAGES order (ensures consistent ordering)
4. Calculate percentage: `footage / total_footage`
5. Round: footage to 2 decimals, percentage to 4 decimals

**Output:** 6 rows (one per stage), even if count=0

#### **Table 2: Stage by Pipe Size**
**Function:** `get_stage_by_pipe_size()`
**Location:** data_processor.py:162-184

1. Collect unique pipe sizes, sort ascending
2. For each pipe size:
   - For each stage:
     - Sum map_length where pipe_size matches AND stage matches
   - Calculate row total (sum of all stage columns)
3. Round to 2 decimals

**Output:** n rows (one per unique pipe size)

#### **Table 3: Pipe Size Mix**
**Function:** `get_pipe_size_mix()`
**Location:** data_processor.py:186-204

1. Collect unique pipe sizes, sort ascending
2. For each pipe size:
   - Filter segments for this pipe size
   - Count segments
   - Sum map_length
   - Calculate average: `footage / count`
   - Calculate percentage: `footage / total_footage`

**Output:** n rows (one per unique pipe size)

#### **Table 4: Length Bins**
**Function:** `get_length_bins()`
**Location:** data_processor.py:206-237

1. For each bin definition in `LENGTH_BINS`:
   - Filter segments where:
     - `map_length >= min_len`
     - If `max_len` is None: no upper bound
     - Else: `map_length <= max_len`
   - Count segments in bin
   - Sum map_length
   - Calculate percentage

**Output:** 5 rows (fixed bins)

**Edge Case:** Segment fits first matching bin only (no double-counting)

#### **Table 5: Easement/Traffic Summary**
**Function:** `get_easement_traffic_summary()`
**Location:** data_processor.py:239-283

1. Filter segments by `easement` flag (Yes/No)
2. Filter segments by `traffic_control` flag (Yes/No)
3. For each category+flag combination:
   - Count segments
   - Sum map_length
   - Calculate percentage

**Output:** 4 rows (Easement Yes/No, Traffic Yes/No)

### 4.4 Excel Generation Flows (Approach 1 Example)

**Function:** `ExcelDashboardGenerator.generate_approach_1()`
**Location:** excel_generator.py:25-41

1. **Create workbook** (`openpyxl.Workbook()`)
2. **Remove default sheet** ("Sheet")
3. **Create Dashboard_Data sheet** (index 0)
   - Write all 5 tables via `_write_all_tables()`
   - Apply header formatting (blue background, white font)
   - Apply number formatting (percentages, thousands separators)
4. **Create Dashboard sheet** (index 1)
   - Add KPI cells (total segments, total footage)
   - Create 5 charts via `_create_openpyxl_charts()`
     - Chart 1: 100% stacked column (Overall Progress)
     - Chart 2: Stacked bar (Progress by Pipe Size)
     - Chart 3: Clustered column (Pipe Size Mix)
     - Chart 4: Column chart (Length Distribution)
     - Chart 5: Clustered column (Easement/Traffic)
   - Position charts on sheet (A5, J5, A25, J25, A45)
5. **Save workbook** to output_path

**Approach 2 Differences (xlsxwriter):**
- Uses xlsxwriter instead of openpyxl
- Enhanced chart styling (gradients, data labels, style=11)
- Series-based chart construction (more control)

**Approach 3 Differences (Plotly images):**
- Generate Plotly figures (`go.Figure`)
- Export to PNG via `fig.to_image(format="png")`
- Embed images in Excel via `openpyxl.drawing.image.Image`

### 4.5 Web Dashboard Rendering (Flask)

**Endpoint:** `/dashboard/<session_id>`
**Function:** `dashboard(session_id)`
**Location:** app.py:116-127

1. **Validate session** (check if session_id in `processed_data`)
2. **Render template** (`dashboard.html`)
   - Pass: session_id, filename, total_segments, total_footage
3. **Client-side JavaScript:**
   - On page load: call `/api/charts/<session_id>/plotly`
   - Parse JSON response (5 Plotly chart objects)
   - Render via `Plotly.newPlot()` for each chart
   - Call `/api/tables/<session_id>` for table data
   - Render tables via `renderTable()` function

**Chart Generation Flow:**
**Endpoint:** `/api/charts/<session_id>/<approach>`
**Function:** `get_charts(session_id, approach)`
**Location:** app.py:130-151

1. Validate session
2. Get processor and tables from session
3. Call `generate_plotly_charts()` (default) or `generate_chartjs_data()`
4. Return JSON (5 chart objects)

**Plotly Chart Construction:**
**Function:** `generate_plotly_charts(processor, tables)`
**Location:** app.py:181-308

For each chart:
1. Get relevant table data
2. Create `go.Figure` with appropriate chart type
   - Chart 1: `go.Bar` (vertical bar)
   - Chart 2: `go.Bar` (horizontal stacked bar, multiple traces)
   - Chart 3: `go.Bar` (clustered, 2 series)
   - Chart 4: `go.Bar` (vertical bar with text labels)
   - Chart 5: `go.Bar` (vertical bar with color mapping)
3. Update layout (titles, axes, colors, hover templates)
4. Serialize to JSON via `PlotlyJSONEncoder`

---

## 5. Risks, Gaps, and Open Questions

### 5.1 Security Risks

**🔴 HIGH PRIORITY:**

1. **Hardcoded Secret Key** (app.py:19)
   - `app.secret_key = 'cipp-dashboard-secret-key-2025'`
   - **Risk:** Session hijacking, CSRF attacks
   - **Fix:** Use environment variable (`os.getenv('SECRET_KEY')`)

2. **No File Upload Validation** (beyond extension check)
   - **Risk:** Malicious Excel files (macros, XXE, zip bombs)
   - **Fix:** Implement file size limits, content validation, virus scanning

3. **No Authentication/Authorization**
   - **Risk:** Anyone can access any session via session_id (predictable timestamp)
   - **Fix:** Add authentication layer, session ownership validation

4. **In-Memory Session Storage**
   - **Risk:** Memory exhaustion, session data loss on restart
   - **Fix:** Use Redis, database, or encrypted cookies

5. **No Input Sanitization for Excel Data**
   - **Risk:** Formula injection in Excel cells (e.g., `=1+1` or `=CMD|...`)
   - **Fix:** Use `data_only=True` (already done), sanitize output

6. **No HTTPS Enforcement**
   - **Risk:** Man-in-the-middle attacks
   - **Fix:** Configure HTTPS in production deployment

**🟡 MEDIUM PRIORITY:**

7. **No Rate Limiting**
   - **Risk:** DoS attacks via repeated uploads
   - **Fix:** Implement rate limiting (Flask-Limiter)

8. **Unvalidated Redirects** (dashboard redirect in index.html:214)
   - **Risk:** Open redirect vulnerability
   - **Fix:** Validate session_id before redirect

9. **Sensitive Data in Logs**
   - **Risk:** Approach failures logged with full exception (app.py:87, 93, 99)
   - **Fix:** Sanitize logs, use structured logging

### 5.2 Architecture & Design Gaps

**🔴 HIGH PRIORITY:**

1. **No Database Layer**
   - All data in memory (`processed_data` dict)
   - No persistence, no audit trail
   - **Gap:** Cannot track historical uploads, generate reports over time
   - **Fix:** Add database (SQLite for dev, PostgreSQL for prod)

2. **Tight Coupling Between Layers**
   - Flask routes directly instantiate `CIPPDataProcessor`, `ExcelDashboardGenerator`
   - **Gap:** Violates DIP (Dependency Inversion Principle)
   - **Fix:** Introduce service layer, dependency injection

3. **No Error Recovery**
   - Upload failures leave orphaned files in `uploads/`
   - Partial failures in Excel generation not cleaned up
   - **Gap:** Disk space accumulation, no cleanup
   - **Fix:** Implement cleanup on errors, scheduled cleanup task

4. **No Logging/Observability**
   - Only basic print statements for errors (app.py:87, 93, 99)
   - **Gap:** Cannot debug production issues, no metrics
   - **Fix:** Add structured logging (JSON), metrics (Prometheus), tracing

**🟡 MEDIUM PRIORITY:**

5. **Duplicate Code Between Flask and Dash Apps**
   - Chart generation logic duplicated in:
     - `app.py:generate_plotly_charts()`
     - `app_dash.py:update_*_chart()` callbacks
   - **Gap:** Violates DRY principle
   - **Fix:** Extract shared chart generation to module

6. **No Configuration Management**
   - Hardcoded paths (`uploads/`, `outputs/`)
   - Hardcoded file size limit (16MB)
   - Hardcoded port (5000)
   - **Gap:** Cannot configure per environment
   - **Fix:** Use config file or environment variables

7. **No Testing**
   - Zero unit tests, integration tests, or end-to-end tests
   - **Gap:** Cannot safely refactor, high regression risk
   - **Fix:** Add pytest suite, test critical paths

8. **ExcelGeneratorV2 Approach 2 Inefficiency**
   - Copies ALL original sheets cell-by-cell (excel_generator_v2.py:65-73)
   - **Gap:** Slow for large files, loses formatting
   - **Fix:** Use openpyxl for copy (preserves formatting)

### 5.3 Data Model & Business Logic Gaps

**🟡 MEDIUM PRIORITY:**

1. **Stage Priority Order Not Configurable**
   - Hardcoded in `_compute_stage()` (data_processor.py:126-139)
   - **Gap:** Cannot adapt to different project workflows
   - **Fix:** Make stage logic configurable (strategy pattern)

2. **Length Bins Not User-Configurable**
   - Hardcoded in `LENGTH_BINS` constant (data_processor.py:23-29)
   - **Gap:** Cannot adapt to different project length distributions
   - **Fix:** Allow user to specify bins in UI or config

3. **No Validation of Pipe Sizes**
   - Accepts any numeric value (including negative, zero, or unrealistic values)
   - **Gap:** Garbage data in, garbage visualizations out
   - **Fix:** Add pipe size range validation (e.g., 4-48 inches)

4. **No Handling of Missing/Null Pipe Sizes**
   - Filters out `None` values (data_processor.py:165, 188)
   - **Gap:** Silent data loss, no warning to user
   - **Fix:** Report segments with missing pipe sizes

5. **No Date Validation**
   - Accepts any date format openpyxl parses
   - **Gap:** Could have future dates, dates out of order
   - **Fix:** Validate date ranges, order (prep < ready < lined < post TV < grouted)

**🟢 LOW PRIORITY:**

6. **Percentage Rounding Inconsistency**
   - Some use 4 decimals (data_processor.py:157), others unspecified
   - **Gap:** Inconsistent precision in reports
   - **Fix:** Standardize to 2 decimals (0.42 = 42%)

7. **No Support for Multiple Projects**
   - Single upload per session, cannot compare projects
   - **Gap:** Cannot do cross-project analytics
   - **Fix:** Add multi-project comparison feature

### 5.4 Performance & Scalability Gaps

**🟡 MEDIUM PRIORITY:**

1. **No Pagination for Large Datasets**
   - All segments loaded into memory at once
   - **Gap:** Could fail for files with 10,000+ segments
   - **Fix:** Use pandas for larger datasets, implement pagination

2. **Synchronous File Processing**
   - Upload endpoint blocks until all processing done
   - **Gap:** Slow response for large files (>1MB)
   - **Fix:** Use background job queue (Celery, RQ)

3. **No Caching**
   - Charts regenerated on every request
   - **Gap:** Wasteful recomputation
   - **Fix:** Cache charts per session (Redis, in-memory with TTL)

4. **Plotly Image Generation Slow**
   - `fig.to_image()` uses kaleido (heavy process)
   - **Gap:** Approach 3 generation takes 5-10 seconds
   - **Fix:** Pre-generate images asynchronously

**🟢 LOW PRIORITY:**

5. **Excel File Not Streamed**
   - Entire file loaded into memory before sending (app.py:177)
   - **Gap:** High memory usage for large files
   - **Fix:** Stream file with `send_file(as_attachment=True, mimetype=...)`

### 5.5 Open Questions & Ambiguities

**❓ Clarification Needed:**

1. **What happens if two stages have the same date?**
   - Example: `lining_date = final_post_tv_date = same date`
   - Current: Priority order still applies (Final Post TV wins)
   - **Question:** Is this correct business logic?

2. **Should "Easement" and "Traffic Control" be mutually exclusive?**
   - Current: A segment can be both, neither, or one
   - Table 5 shows all 4 combinations
   - **Question:** Does this reflect reality? Or should they be exclusive?

3. **What is the expected file size range?**
   - Current limit: 16MB (app.py:22)
   - **Question:** Is this sufficient? What's typical project size?

4. **Should original Excel file be preserved or deleted?**
   - Current: Preserved in `uploads/` forever
   - **Question:** Retention policy? Privacy concerns?

5. **What is "session expiration" policy?**
   - Current: In-memory data lives until server restart
   - **Question:** Should sessions expire after N hours?

6. **Should there be user roles (admin, viewer, editor)?**
   - Current: No roles, everyone can upload
   - **Question:** Is multi-tenancy needed?

7. **Color scheme for stages — is there business meaning?**
   - Dash app (app_dash.py:36-43): Light colors for incomplete, dark for complete
   - Flask app: Different colors (app.py:211)
   - **Question:** Should this be consistent? Is there a standard?

---

## 6. Edge Cases, Failure Modes, and Quality

### 6.1 Known Edge Cases

**✅ Handled Correctly:**

1. **Empty stages** (no segments in a stage)
   - Table 1: Shows stage with count=0, footage=0
   - Charts: Empty bars (correct)

2. **Single pipe size**
   - Tables 2 & 3: Single row, correct
   - Charts: Single bar (works)

3. **All segments in one length bin**
   - Table 4: Other bins show count=0
   - Chart: Single bar (correct)

4. **No easement or traffic control**
   - Table 5: "No" rows have full footage
   - Chart: Correct distribution

5. **Missing columns in Excel**
   - `_get_cell_value()` returns None
   - Validation catches it, skips row (safe)

6. **Invalid VIDEO ID or Map Length**
   - `_is_valid_segment()` returns False
   - Row skipped, no error (silent handling)

7. **Sheet name variations**
   - Fuzzy match with "MOINES" or "SHOT" (data_processor.py:46)
   - Falls back gracefully

**⚠️ Potential Issues:**

8. **Pipe size = 0**
   - NOT validated (only map_length > 0 checked)
   - **Result:** Could appear in tables/charts as "0" pipe
   - **Fix Needed:** Add pipe size validation

9. **Extremely long segment names**
   - No truncation in table rendering
   - **Result:** Could break chart labels or table layout
   - **Fix Needed:** Truncate to N characters

10. **Unicode/special characters in segment names**
    - openpyxl handles Unicode
    - **Result:** Should work, but untested for emoji, RTL text
    - **Fix Needed:** Test with international characters

11. **Dates in wrong order** (e.g., grout date < lining date)
    - NO validation of date sequence
    - **Result:** Stage computed correctly per priority, but illogical data not flagged
    - **Fix Needed:** Add date sequence validation

12. **Future dates**
    - NO validation of date ranges
    - **Result:** Accepts dates in year 2099
    - **Fix Needed:** Validate dates <= today

13. **Negative map_length**
    - Validation checks `> 0` (data_processor.py:110)
    - **Result:** Correctly rejected
    - **Status:** ✅ Handled

14. **Non-numeric pipe_size**
    - openpyxl returns None for text cells
    - Filtered out in table generation (data_processor.py:165)
    - **Result:** Silent data loss
    - **Fix Needed:** Warn user

### 6.2 Failure Modes & Error Handling

**Graceful Degradation:**

1. **Approach 1 Excel generation fails**
   - Caught in try/except (app.py:84-88)
   - Logs error, sets `output_files['approach1'] = None`
   - Other approaches still attempted
   - **Download:** Returns 404 for failed approach

2. **Approach 2 Excel generation fails** (same as above)

3. **Approach 3 Excel generation fails**
   - Common failure: kaleido not installed or incompatible
   - Caught in try/except (app.py:96-100)
   - **Download:** Returns 404

4. **Sheet not found**
   - Raises ValueError with clear message (data_processor.py:50)
   - Caught in Flask route (app.py:112)
   - Returns JSON error to user

5. **No valid segments found**
   - `self.segments = []`, `self.total_footage = 0`
   - Table generation: All tables empty (no rows)
   - Charts: Render empty (Plotly handles gracefully)

**Catastrophic Failures:**

6. **Corrupted Excel file**
   - openpyxl raises exception
   - Caught in Flask route (app.py:112)
   - **Result:** Error message to user
   - **Gap:** Error message may expose stack trace

7. **Out of memory**
   - Large file + all approaches + session storage
   - **Result:** Server crash, 500 error
   - **Gap:** No memory limits, no cleanup

8. **Disk full**
   - Cannot save uploaded file or output file
   - **Result:** OSError raised, 500 error
   - **Gap:** No disk space check

9. **kaleido process hangs** (Approach 3)
   - `fig.to_image()` can hang indefinitely
   - **Result:** Request timeout
   - **Gap:** No timeout on kaleido subprocess

10. **Session ID collision**
    - Timestamp format `YYYYMMDD_HHMMSS` — two uploads in same second
    - **Result:** Second upload overwrites first session
    - **Gap:** No collision detection
    - **Fix Needed:** Add UUID or milliseconds

### 6.3 Testing Status

**Current Status:** ❌ **ZERO TESTS**

**Critical Paths Needing Tests:**

1. **Stage Computation Logic**
   - Test all 6 stage scenarios
   - Test priority order
   - Test edge cases (all None, multiple dates)

2. **Data Validation**
   - Test valid segments pass
   - Test invalid segments rejected
   - Test boundary conditions (VIDEO_ID=0, 1, -1; map_length=0, 0.01, -1)

3. **Table Generation**
   - Test each table with known input
   - Test empty dataset
   - Test single segment
   - Test percentage calculations

4. **Excel Generation**
   - Test all 3 approaches
   - Test file structure (sheet names, cell values)
   - Test chart references

5. **Upload Flow**
   - Test valid file upload
   - Test invalid file types
   - Test oversized files
   - Test concurrent uploads

**Recommended Test Structure:**

```
tests/
├── unit/
│   ├── test_data_processor.py
│   ├── test_excel_generator.py
│   └── test_excel_generator_v2.py
├── integration/
│   ├── test_flask_routes.py
│   ├── test_dash_callbacks.py
│   └── test_end_to_end.py
├── fixtures/
│   ├── sample_valid.xlsx
│   ├── sample_empty.xlsx
│   ├── sample_invalid.xlsx
│   └── expected_outputs/
└── conftest.py
```

### 6.4 Code Quality Observations

**✅ Strengths:**

1. **Clear module separation**
   - Data processing, Excel generation, web apps are distinct
   - Good SRP adherence at module level

2. **Type hints used**
   - Most functions have type annotations (data_processor.py)
   - Improves readability and IDE support

3. **Docstrings present**
   - Module-level and class-level docstrings
   - Explains purpose clearly

4. **Consistent naming**
   - Domain terms used throughout (`segment`, `stage`, `pipe_size`)
   - Good ubiquitous language (DDD)

5. **Defensive programming**
   - Safe cell access (`_get_cell_value`)
   - Exception handling in validation (`_is_valid_segment`)

**⚠️ Areas for Improvement:**

1. **Magic numbers**
   - Row numbers (1, 2, 10, 19, 27, 37) hardcoded (excel_generator.py)
   - **Fix:** Extract to named constants

2. **Long functions**
   - `_create_xlsxwriter_charts()` (excel_generator.py:279-370) is 91 lines
   - Violates SRP (creates 5 different charts)
   - **Fix:** Extract each chart to separate method

3. **No input validation in constructors**
   - `CIPPDataProcessor.__init__()` accepts any file_path
   - **Fix:** Validate file exists, is .xlsx

4. **No logging**
   - Only `print()` statements for errors
   - **Fix:** Use `logging` module

5. **Commented-out code**
   - None found (good!)

6. **Dead code**
   - `generate_chartjs_data()` (app.py:311-332) incomplete
   - **Fix:** Remove or complete

7. **Inconsistent error handling**
   - Some functions raise exceptions, others return None/False
   - **Fix:** Define error handling strategy (exceptions vs. result types)

---

## 7. Opportunities and Next Steps

### 7.1 Immediate Refactoring Opportunities

**🎯 High Impact, Low Effort:**

1. **Extract Magic Numbers to Constants** (1 hour)
   ```python
   # excel_generator.py
   TABLE_1_START_ROW = 1
   TABLE_2_START_ROW = 10
   TABLE_3_START_ROW = 19
   TABLE_4_START_ROW = 27
   TABLE_5_START_ROW = 37
   ```

2. **Add Environment-Based Configuration** (2 hours)
   ```python
   # config.py
   class Config:
       SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
       UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
       OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
       MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024))
   ```

3. **Add Structured Logging** (3 hours)
   ```python
   import logging
   import json

   logger = logging.getLogger(__name__)
   logger.info("Processing file", extra={
       "session_id": session_id,
       "filename": filename,
       "segments": len(processor.segments)
   })
   ```

4. **Introduce Service Layer** (4 hours)
   ```python
   # services/dashboard_service.py
   class DashboardService:
       def __init__(self, processor_factory, generator_factory):
           self.processor_factory = processor_factory
           self.generator_factory = generator_factory

       def process_upload(self, filepath):
           processor = self.processor_factory.create(filepath)
           processor.load_data()
           return processor
   ```

5. **Add Input Validation** (3 hours)
   - Validate file exists before processing
   - Validate pipe size ranges (4-48 inches)
   - Validate date sequences
   - Warn on missing data

**🎯 High Impact, Medium Effort:**

6. **Add Unit Tests** (2 days)
   - Focus on `CIPPDataProcessor` first (core logic)
   - Test stage computation, table generation, validation
   - Use pytest, pytest-cov for coverage

7. **Implement Background Job Processing** (3 days)
   - Use RQ (Redis Queue) or Celery
   - Offload Excel generation to background
   - Return immediately, poll for completion

8. **Add Database Layer** (3 days)
   - SQLAlchemy ORM
   - Models: Upload, Session, GeneratedFile
   - Persist sessions, enable audit trail

9. **Deduplicate Chart Generation Logic** (2 days)
   - Extract to `charts.py` module
   - Shared by Flask and Dash apps
   - Use factory pattern or builder pattern

**🎯 High Impact, High Effort:**

10. **Add Authentication & Authorization** (1 week)
    - Flask-Login or JWT
    - User model, session ownership
    - Secure session storage

11. **Implement Multi-Project Comparison** (1 week)
    - Allow upload of multiple files
    - Side-by-side comparison dashboards
    - Aggregate analytics across projects

12. **Add Real-Time Progress Tracking** (1 week)
    - WebSocket updates during processing
    - Progress bar for large files
    - Cancel operation support

### 7.2 Feature Enhancement Ideas

**📊 Analytics Enhancements:**

1. **Time-Series Analysis**
   - Plot completion dates over time
   - Velocity metrics (feet/day, segments/week)
   - Burndown charts

2. **Geospatial Visualization**
   - If lat/lon data available
   - Map view of segments
   - Color-coded by stage

3. **Cost Estimation**
   - Add cost per foot by pipe size
   - Calculate project budget
   - Track actual vs. estimated

4. **Risk Analysis**
   - Identify segments behind schedule
   - Flag segments with missing data
   - Predictive completion dates

**🎨 UX Enhancements:**

5. **Drag-and-Drop Upload**
   - Already present in Dash app
   - Add to Flask app

6. **Export to PDF**
   - Generate printable reports
   - Include all charts and tables

7. **Email Delivery**
   - Send generated dashboards via email
   - Scheduled reporting

8. **Mobile-Responsive Design**
   - Optimize for tablets/phones
   - Touch-friendly charts

**🔧 Technical Enhancements:**

9. **API Versioning**
   - `/api/v1/charts` vs. `/api/v2/charts`
   - Support multiple API versions

10. **GraphQL Endpoint**
    - Flexible queries for table data
    - Reduce over-fetching

11. **Webhook Support**
    - Notify external systems on completion
    - Integrate with project management tools

12. **Docker Containerization**
    - Dockerfile, docker-compose.yml
    - Easy deployment

### 7.3 Documentation Needs

**📖 Missing Documentation:**

1. **API Documentation**
   - OpenAPI/Swagger spec
   - Example requests/responses

2. **Deployment Guide**
   - Production setup (HTTPS, WSGI, Nginx)
   - Environment configuration
   - Database migrations

3. **User Guide**
   - Screenshots of upload flow
   - Explanation of each visualization
   - How to interpret tables

4. **Developer Guide**
   - Architecture diagrams
   - How to add new table types
   - How to add new chart types
   - Testing guidelines

5. **ADR (Architecture Decision Records)**
   - Why 3 Excel approaches?
   - Why Flask AND Dash?
   - Why in-memory storage (for now)?

### 7.4 Performance Optimization Opportunities

**⚡ Quick Wins:**

1. **Cache Plotly Charts** (1 day)
   - Use `@lru_cache` or Redis
   - Invalidate on new upload

2. **Lazy Load Dashboard Components** (1 day)
   - Load charts on scroll/click
   - Reduce initial page load time

3. **Compress Responses** (1 hour)
   - Enable gzip in Flask (`flask-compress`)

**⚡ Bigger Wins:**

4. **Use Pandas for Large Datasets** (2 days)
   - Replace manual iteration with vectorized ops
   - 10-100x speedup for large files

5. **Parallel Excel Generation** (2 days)
   - Generate 3 approaches in parallel threads
   - Use `concurrent.futures`

6. **Pre-Aggregate Data** (3 days)
   - Compute tables once, cache
   - Only regenerate on new upload

---

## 8. EXHAUSTIVE FUNCTION & MODULE MAPPING

### 8.1 Module: `data_processor.py` (CIPPDataProcessor)

**Purpose:** Core data processing engine — loads, validates, and analyzes CIPP shot schedule data

| Function/Method | Line Range | Signature | Purpose | Called By | Calls |
|----------------|-----------|-----------|---------|-----------|-------|
| `__init__` | 31-36 | `(file_path: str, sheet_name: str = "WEST DES MOINES, IA Shot Schedu")` | Initialize processor with file path | Flask/Dash apps, ExcelGenerator | - |
| `load_data` | 38-94 | `() -> List[Dict[str, Any]]` | **CRITICAL PATH** — Load and validate Excel data | Flask/Dash upload handlers | `_get_cell_value`, `_is_valid_segment`, `_is_truthy`, `_compute_stage` |
| `_get_cell_value` | 96-103 | `(row, col_idx)` | Safe cell access (handles None/IndexError) | `load_data` | openpyxl row access |
| `_is_valid_segment` | 105-112 | `(video_id, map_length) -> bool` | Validate segment (VIDEO_ID ≥ 1, map_length > 0) | `load_data` | - |
| `_is_truthy` | 114-124 | `(value) -> bool` | Convert Excel values to boolean | `load_data` | - |
| `_compute_stage` | 126-139 | `(segment: Dict[str, Any]) -> str` | **CORE BUSINESS LOGIC** — Compute stage via priority | `load_data` | - |
| `get_stage_footage_summary` | 141-160 | `() -> List[Dict[str, Any]]` | Generate Table 1 (6 rows, stage summary) | `get_all_tables` | - |
| `get_stage_by_pipe_size` | 162-184 | `() -> List[Dict[str, Any]]` | Generate Table 2 (n rows, progress by pipe size) | `get_all_tables` | - |
| `get_pipe_size_mix` | 186-204 | `() -> List[Dict[str, Any]]` | Generate Table 3 (n rows, pipe size mix) | `get_all_tables` | - |
| `get_length_bins` | 206-237 | `() -> List[Dict[str, Any]]` | Generate Table 4 (5 rows, length distribution) | `get_all_tables` | - |
| `get_easement_traffic_summary` | 239-283 | `() -> List[Dict[str, Any]]` | Generate Table 5 (4 rows, easement/traffic) | `get_all_tables` | - |
| `get_all_tables` | 285-293 | `() -> Dict[str, List[Dict[str, Any]]]` | **PUBLIC API** — Return all 5 tables | Flask/Dash apps, ExcelGenerator | All `get_*_summary` methods |

**Class Attributes:**
- `STAGES` (14-21): List of 6 stage names (constant, ordering matters)
- `LENGTH_BINS` (23-29): List of 5 bin definitions (configurable constant)

**Instance Attributes:**
- `file_path`: Path to uploaded Excel file
- `sheet_name`: Name of sheet to process
- `segments`: List of segment dictionaries (populated by `load_data`)
- `total_footage`: Sum of all map_length values

**Dependencies:**
- `openpyxl.load_workbook`
- `typing.List`, `typing.Dict`, `typing.Any`, `typing.Optional`
- `collections.defaultdict`

---

### 8.2 Module: `excel_generator.py` (ExcelDashboardGenerator)

**Purpose:** Generate NEW Excel workbooks with dashboards (3 approaches)

| Function/Method | Line Range | Signature | Purpose | Called By | Calls |
|----------------|-----------|-----------|---------|-----------|-------|
| `__init__` | 20-23 | `(data_processor)` | Initialize with processor instance | Flask/Dash apps | `data_processor.get_all_tables()` |
| `generate_approach_1` | 25-41 | `(output_path: str)` | Generate openpyxl native charts Excel | Flask/Dash download | `_write_all_tables`, `_create_openpyxl_charts` |
| `generate_approach_2` | 43-61 | `(output_path: str)` | Generate xlsxwriter enhanced charts Excel | Flask/Dash download | `_write_all_tables_xlsxwriter`, `_create_xlsxwriter_charts` |
| `generate_approach_3` | 63-86 | `(output_path: str)` | Generate Plotly images embedded in Excel | Flask/Dash download | `_write_all_tables`, `_create_plotly_charts` |
| `_write_all_tables` | 88-106 | `(ws)` | Write all 5 tables to sheet (openpyxl) | `generate_approach_1`, `generate_approach_3` | `_write_table` |
| `_write_table` | 108-132 | `(ws, start_row, start_col, data, header_fill, header_font)` | Write single table with formatting | `_write_all_tables` | openpyxl cell access |
| `_create_openpyxl_charts` | 133-221 | `(ws_dash, ws_data)` | Create 5 openpyxl charts | `generate_approach_1` | openpyxl chart creation |
| `_write_all_tables_xlsxwriter` | 223-254 | `(wb, ws)` | Write all 5 tables (xlsxwriter) | `generate_approach_2` | `_write_table_xlsxwriter` |
| `_write_table_xlsxwriter` | 256-278 | `(ws, start_row, start_col, data, header_fmt, num_fmt, pct_fmt)` | Write single table (xlsxwriter) | `_write_all_tables_xlsxwriter` | xlsxwriter write |
| `_create_xlsxwriter_charts` | 279-370 | `(wb, ws_dash, ws_data)` | Create 5 xlsxwriter charts | `generate_approach_2` | xlsxwriter chart creation |
| `_create_plotly_charts` | 372-517 | `(ws_dash, ws_data)` | Create 5 Plotly charts as images | `generate_approach_3` | plotly `go.Figure`, `to_image` |

**Dependencies:**
- `openpyxl` (Workbook, load_workbook, chart, drawing.image, styles)
- `xlsxwriter` (optional, imported in method)
- `plotly.graph_objects`, `plotly.express` (optional, imported in method)
- `PIL.Image` (optional, imported in method)
- `io`, `os`

**Table Positioning (Excel cells):**
- Table 1: A1:D7
- Table 2: A10:H{10+n}
- Table 3: A19:E{19+n}
- Table 4: A27:F32
- Table 5: A37:E41

**Chart Positioning (Excel cells):**
- Chart 1: A5 (Overall Progress)
- Chart 2: J5 (Progress by Pipe Size)
- Chart 3: A25 (Pipe Size Mix)
- Chart 4: J25 (Length Distribution)
- Chart 5: A45 (Easement/Traffic)

---

### 8.3 Module: `excel_generator_v2.py` (ExcelDashboardGeneratorV2)

**Purpose:** Generate Excel dashboards by MODIFYING original uploaded file (preserves source data)

| Function/Method | Line Range | Signature | Purpose | Called By | Calls |
|----------------|-----------|-----------|---------|-----------|-------|
| `__init__` | 18-22 | `(data_processor, original_filepath)` | Initialize with processor and original file path | Dash app download | `data_processor.get_all_tables()` |
| `generate_approach_1` | 24-49 | `(output_path: str)` | Copy original, add dashboard sheets (openpyxl) | Dash app download | `shutil.copy2`, `_write_all_tables`, `_create_openpyxl_charts` |
| `generate_approach_2` | 51-84 | `(output_path: str)` | Create new workbook, copy data, add dashboards (xlsxwriter) | Dash app download | `_write_all_tables_xlsxwriter`, `_create_xlsxwriter_charts` |
| `generate_approach_3` | 86-116 | `(output_path: str)` | Copy original, add dashboard sheets with Plotly images | Dash app download | `shutil.copy2`, `_write_all_tables`, `_create_plotly_charts` |
| `_write_all_tables` | 118-139 | `(ws, wb)` | Write all 5 tables with DYNAMIC positioning | `generate_approach_1`, `generate_approach_3` | `_write_table` |
| `_write_table` | 141-164 | `(ws, start_row, start_col, data, header_fill, header_font)` | Write single table (same as excel_generator.py) | `_write_all_tables` | openpyxl cell access |
| `_create_openpyxl_charts` | 166-219 | `(ws_dash, ws_data)` | Create 3 charts (fewer than v1) | `generate_approach_1` | openpyxl chart creation |
| `_write_all_tables_xlsxwriter` | 221-237 | `(wb, ws)` | Write all 5 tables dynamically (xlsxwriter) | `generate_approach_2` | `_write_table_xlsxwriter` |
| `_write_table_xlsxwriter` | 239-260 | `(ws, start_row, start_col, data, header_fmt, num_fmt, pct_fmt)` | Write single table (xlsxwriter) | `_write_all_tables_xlsxwriter` | xlsxwriter write |
| `_create_xlsxwriter_charts` | 262-278 | `(wb, ws_dash, ws_data)` | Create 1 pie chart (fewer than v1) | `generate_approach_2` | xlsxwriter chart creation |
| `_create_plotly_charts` | 280-301 | `(ws_dash, ws_data)` | Create 1 donut chart (fewer than v1) | `generate_approach_3` | plotly `go.Figure`, `to_image` |

**Key Difference from `excel_generator.py`:**
- V2 preserves original Excel sheets
- V2 adds Dashboard_Data and Dashboard as NEW sheets (index 0, 1)
- V2 Approach 2 inefficiently copies ALL original sheets cell-by-cell (performance concern)

**Dependencies:** Same as `excel_generator.py` + `shutil`

---

### 8.4 Module: `app.py` (Flask Web Application)

**Purpose:** HTTP server for file upload, processing, and web-based dashboards

| Route/Function | Line Range | Method | Purpose | Calls |
|---------------|-----------|--------|---------|-------|
| `/` (index) | 32-35 | GET | Render upload page | `render_template('index.html')` |
| `/upload` (upload_file) | 38-113 | POST | **CRITICAL PATH** — Handle file upload & processing | `CIPPDataProcessor.load_data`, `ExcelDashboardGenerator.generate_*`, `secure_filename`, `datetime.now` |
| `/dashboard/<session_id>` (dashboard) | 116-127 | GET | Render dashboard page | `render_template('dashboard.html')` |
| `/api/charts/<session_id>/<approach>` (get_charts) | 130-151 | GET | Return chart data as JSON | `generate_plotly_charts` or `generate_chartjs_data` |
| `/api/tables/<session_id>` (get_tables) | 154-161 | GET | Return table data as JSON | - |
| `/download/<session_id>/<approach>` (download_file) | 164-178 | GET | Download Excel file | `send_file` |
| `generate_plotly_charts` | 181-308 | - | **CORE LOGIC** — Generate 5 Plotly charts for web | `go.Figure`, `go.Bar`, `PlotlyJSONEncoder` |
| `generate_chartjs_data` | 311-332 | - | Generate Chart.js data (incomplete) | - |

**Global State:**
- `app` (Flask instance)
- `processed_data` (dict): In-memory session storage

**Configuration:**
- `app.secret_key` (19): Hardcoded secret key (SECURITY RISK)
- `UPLOAD_FOLDER` (20): `'uploads'`
- `OUTPUT_FOLDER` (21): `'outputs'`
- `MAX_CONTENT_LENGTH` (22): 16MB

**Dependencies:**
- `flask` (Flask, render_template, request, send_file, jsonify, session)
- `werkzeug.utils.secure_filename`
- `os`, `json`, `datetime`
- `plotly` (graph_objects, express, utils.PlotlyJSONEncoder)
- `data_processor.CIPPDataProcessor`
- `excel_generator.ExcelDashboardGenerator`

**Session Data Structure:**
```python
processed_data[session_id] = {
    'processor': CIPPDataProcessor,
    'tables': dict,
    'filepath': str,
    'filename': str,
    'output_files': {
        'approach1': str,
        'approach2': str,
        'approach3': str
    }
}
```

**Upload Flow Detail (app.py:38-113):**
1. Validate file present and `.xlsx` extension
2. Save to `uploads/` with timestamp prefix
3. Create `CIPPDataProcessor` and call `load_data()`
4. Call `get_all_tables()`
5. Store in `processed_data[session_id]`
6. Create `ExcelDashboardGenerator`
7. Generate all 3 approaches (wrapped in try/except)
8. Return JSON with success + session_id

**Chart Generation Detail (app.py:181-308):**
- Chart 1: Vertical bar (Overall Progress)
- Chart 2: Horizontal stacked bar (Progress by Pipe Size, 6 traces)
- Chart 3: Clustered bar (Pipe Size Mix, 2 series)
- Chart 4: Vertical bar with text labels (Length Distribution)
- Chart 5: Vertical bar with color mapping (Easement/Traffic)
- All charts use custom hover templates
- All charts serialized via `PlotlyJSONEncoder`

---

### 8.5 Module: `app_dash.py` (Dash Web Application)

**Purpose:** Modern, reactive dashboarding with enhanced UX, interactive visualizations, and advanced charts

**Layout Components:**
- Navbar (50-64)
- Upload section (67-86)
- Dashboard section (89-238) — hidden until upload
  - KPIs (91-129): 4 cards (segments, footage, avg length, % complete)
  - Download buttons (132-149)
  - Visualizations (152-207): 5 charts in grid layout
  - Data tables (210-226): 5 tabs
  - Original Excel table (229-238)
- Session store (243)

**Callbacks (Reactive Functions):**

| Callback | Line Range | Inputs | Outputs | Purpose | Calls |
|----------|-----------|--------|---------|---------|-------|
| `process_upload` | 248-318 | `upload-data.contents`, `upload-data.filename` | 7 outputs (status, visibility, KPIs) | **CRITICAL PATH** — Process uploaded file | `CIPPDataProcessor.load_data`, `base64.b64decode` |
| `update_progress_bar` | 321-385 | `session-data.data` | `progress-bar-chart.figure` | Render horizontal stacked bar (ALL 6 stages) | `go.Figure`, `go.Bar` |
| `update_radar_chart` | 388-456 | `session-data.data` | `radar-chart.figure` | Render radar/spider chart (segment characteristics) | `go.Figure`, `go.Scatterpolar` |
| `update_pipe_progress` | 459-497 | `session-data.data` | `pipe-progress-chart.figure` | Render stacked bar (progress by pipe size) | `go.Figure`, `go.Bar` |
| `update_pipe_size_chart` | 500-537 | `session-data.data` | `pipe-size-chart.figure` | Render donut chart (pipe size distribution) | `go.Figure`, `go.Pie` |
| `update_length_distribution` | 540-584 | `session-data.data` | `length-distribution-chart.figure` | Render horizontal bar (length distribution) | `go.Figure`, `go.Bar` |
| `update_easement_traffic` | 587-631 | `session-data.data` | `easement-traffic-chart.figure` | Render pie chart (easement/traffic/regular) | `go.Figure`, `go.Pie` |
| `render_table_content` | 634-685 | `table-tabs.active_tab`, `session-data.data` | `table-content.children` | Render selected table as DataTable | `pd.DataFrame`, `dash_table.DataTable` |
| `render_excel_table` | 688-750 | `session-data.data` | `excel-table-container.children` | Render original Excel data as DataTable | `load_workbook`, `pd.DataFrame`, `dash_table.DataTable` |
| `download_excel` | 753-799 | 3 button clicks, `session-data.data` | `download-file.data` | Generate and download Excel file | `ExcelDashboardGeneratorV2.generate_*`, `dcc.send_file` |

**Global State:**
- `app` (Dash instance)
- `processed_data_store` (dict): In-memory session storage (same structure as Flask app)

**Color Scheme (36-43):**
- Light colors: Not Started, Prep Complete, Ready to Line (incomplete stages)
- Dark colors: Lined, Post TV Complete, Grouted/Done (complete stages)

**Stage Order (45):**
- `STAGE_ORDER` list ensures consistent ordering across all charts

**Dependencies:**
- `dash` (Dash, dcc, html, dash_table, Input, Output, State, exceptions)
- `dash_bootstrap_components` (dbc)
- `plotly` (graph_objects, express)
- `pandas` (pd)
- `base64`, `io`, `os`, `datetime`
- `data_processor.CIPPDataProcessor`
- `excel_generator_v2.ExcelDashboardGeneratorV2`

**Unique Charts (Not in Flask app):**
- **Radar/Spider Chart** (388-456): Shows segment characteristics (easement %, traffic %, regular %, large pipe %, 6" pipe %) in polar coordinates with webbed visualization
- **Horizontal Progress Bar** (321-385): Single bar with ALL 6 stages stacked, color-coded (light for incomplete, dark for complete)

**Enhanced Styling:**
- Bootstrap 5 theme
- Font Awesome icons
- Custom color scheme
- Responsive grid layout
- Hover effects on cards

---

### 8.6 Module: `templates/index.html` (Flask Upload Page)

**Purpose:** HTML template for file upload interface

**Structure:**
- Bootstrap 5 layout
- Font Awesome icons
- Welcome card with features (38-66)
- Upload form (69-96)
  - File input (accept=".xlsx")
  - Submit button
  - Loading spinner
  - Alert container
- Instructions card (100-132)
- Three approaches info card (134-173)

**JavaScript (180-237):**
- Event listener on form submit
- Fetch API POST to `/upload`
- Loading state management
- Error/success alerts
- Redirect to `/dashboard/<session_id>` on success

**Dependencies:**
- Bootstrap 5 CDN
- Font Awesome CDN
- Custom CSS (`style.css`)

---

### 8.7 Module: `templates/dashboard.html` (Flask Dashboard Page)

**Purpose:** HTML template for dashboard display

**Structure:**
- Navbar with "Upload New File" link (14-25)
- File info + KPIs (29-68)
- Approach selector + download buttons (72-107)
- 5 chart containers (120-177)
- 5 table tabs (189-246)

**JavaScript (251-341):**
- `loadCharts()`: Fetch from `/api/charts/<session_id>/<approach>`, render via `Plotly.newPlot()`
- `loadTables()`: Fetch from `/api/tables/<session_id>`, render via `renderTable()`
- `renderTable()`: Build HTML table from JSON data, format percentages/numbers
- Event listener on approach selector (change charts)

**Dependencies:**
- Bootstrap 5 CDN
- Font Awesome CDN
- Plotly.js 2.26.0 CDN
- Custom CSS (`style.css`)

---

### 8.8 Module: `static/css/style.css` (Custom Styling)

**Purpose:** Custom CSS for both Flask and Dash apps

**Key Styles:**
- CSS variables (3-11): Color palette
- Navbar (19-23)
- Welcome card (25-34): Gradient background
- Feature items (36-47): Left border accent
- Upload section (49-84): Input styling, button hover effects
- KPI boxes (112-133): Gradient background, hover lift
- Cards (136-150): Border radius, shadow on hover
- Chart containers (152-156): Min height
- Tables (158-178): Striped rows, hover effect
- Tabs (180-204): Bottom border on active
- Animations (253-267): fadeIn keyframe
- Scrollbar (269-286): Custom styling
- Print styles (288-297): Hide interactive elements

**Responsive (239-251):**
- Mobile breakpoints for cards, KPIs, charts

**Dependencies:** None (pure CSS)

---

### 8.9 File Structure & Organization

```
ssREFINEMENT/
├── app.py                      # Flask web application (336 lines)
├── app_dash.py                 # Dash web application (803 lines)
├── data_processor.py           # Core data processing (294 lines)
├── excel_generator.py          # Excel generation (3 approaches) (517 lines)
├── excel_generator_v2.py       # Excel generation V2 (modifies original) (301 lines)
├── requirements.txt            # Python dependencies (12 lines)
├── README.md                   # User documentation (249 lines)
├── CLAUDE.md                   # Engineering guidelines (437 lines)
├── excelrefinement.txt         # Original requirements spec (295 lines)
├── templates/
│   ├── index.html             # Upload page (240 lines)
│   └── dashboard.html         # Dashboard page (344 lines)
├── static/
│   └── css/
│       └── style.css          # Custom styling (298 lines)
├── uploads/                   # Uploaded Excel files (auto-created)
├── outputs/                   # Generated Excel files (auto-created)
└── .claude/
    └── settings.local.json    # Claude Code settings
```

**Total Lines of Code:** ~3,700 (excluding comments/blank lines)

**Language Distribution:**
- Python: ~2,300 lines (62%)
- HTML: ~600 lines (16%)
- CSS: ~300 lines (8%)
- Documentation: ~500 lines (14%)

---

## 9. Evidence & Rationale

### 9.1 Documentation Insights

**Evidence from README.md:**
- Project name: "CIPP Dashboard Generator"
- 5 summary tables explicitly listed (lines 7-12)
- 5 visualizations explicitly listed (lines 14-19)
- 3 Excel approaches explicitly listed (lines 21-36)
- Flask web app confirmed (lines 59-79)
- Dash app NOT mentioned in README (evidence: exists in codebase but undocumented)

**Evidence from excelrefinement.txt:**
- Original requirements document (detailed spec)
- Stage determination logic explicitly defined (lines 9-16)
- Table structures with exact column headers (lines 18-270)
- Chart mappings to tables (lines 143-161)

**Evidence from CLAUDE.md:**
- Engineering guidelines for this project
- Digest-first rule (mandatory use of this synopsis)
- SOLID, DRY, KISS/YAGNI principles explicitly required
- Observability, resilience, IaC awareness mandated

**Inferred:**
- Project is actively developed (version 1.0.0 dated 2025-12-06 per README)
- Multiple developers likely (CLAUDE.md provides shared standards)
- Production deployment intended (security notes in README:222-228)

### 9.2 Code Analysis — Architectural Decisions

**Why 3 Excel approaches?**
- **Evidence:** README lines 21-36, excelrefinement.txt lines 162-295
- **Rationale:** Different use cases:
  - Approach 1 (openpyxl): Standard workflows, full Excel interactivity
  - Approach 2 (xlsxwriter): Professional presentations, superior formatting
  - Approach 3 (Plotly): Publication-quality, modern design
- **Trade-offs:** Increased complexity, dependency on 3 libraries (openpyxl, xlsxwriter, plotly+kaleido)

**Why Flask AND Dash apps?**
- **Evidence:** Both apps present in codebase, serve on same port (5000)
- **Inferred Rationale:**
  - Flask app: Quick prototype, simpler deployment
  - Dash app: Modern UX, reactive components, better visualizations
  - Likely evolved from Flask to Dash, kept both for compatibility
- **Gap:** No documentation on which app to use when

**Why in-memory session storage?**
- **Evidence:** `processed_data = {}` (app.py:29, app_dash.py:33)
- **Rationale:** Simplicity for development, no database dependency
- **Trade-off:** NOT production-ready (acknowledged in README:223-224)

**Why manual iteration vs. pandas?**
- **Evidence:** `data_processor.py` uses manual loops, not pandas
- **Inferred Rationale:** Avoid pandas dependency for core logic, keep lightweight
- **Trade-off:** Slower for large datasets, more verbose code

### 9.3 Skeptical Review — What Could Be Better?

**Claim:** "System handles all edge cases gracefully"
- **Challenge:** No evidence of testing (zero test files)
- **Counter-evidence:** Many edge cases NOT handled (pipe_size=0, future dates, date sequence)
- **Conclusion:** Claim OVERSTATED, many edge cases unhandled

**Claim:** "Three approaches provide flexibility"
- **Support:** README and code confirm 3 distinct implementations
- **Challenge:** Approach 2 (xlsxwriter) in `excel_generator_v2.py` is incomplete (only 1 chart)
- **Conclusion:** Claim MOSTLY TRUE, but Approach 2 V2 is underdeveloped

**Claim:** "Production-ready"
- **Challenge:** Security risks, no tests, in-memory storage, hardcoded secrets
- **Counter-evidence:** README explicitly says "For production deployment: [list of fixes needed]" (lines 222-228)
- **Conclusion:** Claim FALSE, system is NOT production-ready (correctly acknowledged in README)

**Claim:** "Comprehensive dashboards"
- **Support:** 5 tables + 5 charts confirmed in code and docs
- **Challenge:** Dash app has MORE charts (radar chart, different progress bar) than Flask app
- **Conclusion:** Claim TRUE, but "comprehensive" varies by app

**Claim:** "Modular and maintainable"
- **Support:** Clear module separation, SRP at module level, type hints
- **Challenge:** Long functions (e.g., `_create_xlsxwriter_charts`), magic numbers, tight coupling (routes instantiate processors directly)
- **Conclusion:** Claim PARTIALLY TRUE, good at module level, needs improvement at function level

### 9.4 Reconciliation — Furthered Understanding

**Initial Understanding (Pass 1 + Pass 2):**
- CIPP dashboard generator with Flask web app
- 3 Excel approaches, 5 tables, 5 charts
- In-memory storage, not production-ready

**Skeptical Findings (Pass 2 continued):**
- TWO web apps (Flask AND Dash), not one
- Dash app has MORE features (radar chart, better UX)
- V2 Excel generators preserve original files (important distinction)
- Many security risks and edge cases unhandled

**Reconciled Understanding:**
- This is a **dual-app system**: Flask (simple, original) + Dash (modern, enhanced)
- Excel generation has **two variants**: V1 (new workbooks) + V2 (modify originals)
- System is **development-stage**, not production-ready (correctly acknowledged)
- Documentation is **incomplete** (Dash app undocumented, many edge cases not mentioned)

**New Insights (Pass 3):**
- **Radar chart** in Dash app is unique, not in Flask app (app_dash.py:388-456)
- **Color scheme** has business meaning: light=incomplete, dark=complete (app_dash.py:36-43)
- **Session ID collision** is a real risk (timestamp-based, no UUID)
- **Stage computation order** is critical, not just a detail (first match wins)
- **Dynamic table positioning** in V2 vs. fixed in V1 (important for flexibility)

---

## 10. Critical Refactoring Paths (Based on CLAUDE.md Principles)

### 10.1 Applying SRP (Single Responsibility Principle)

**Current Violations:**
1. **`_create_xlsxwriter_charts()`** (excel_generator.py:279-370)
   - Responsibility: Creates 5 different charts
   - Violation: Multiple reasons to change (any chart modification)
   - **Fix:** Extract to 5 methods:
     ```python
     def _create_overall_progress_chart(self, wb, ws_dash, ws_data):
         # Chart 1 only
     def _create_pipe_progress_chart(self, wb, ws_dash, ws_data):
         # Chart 2 only
     # ... etc.
     ```

2. **`upload_file()` in Flask** (app.py:38-113)
   - Responsibility: HTTP handling, file saving, data processing, Excel generation, session management
   - Violation: Too many concerns
   - **Fix:** Extract service layer:
     ```python
     class UploadService:
         def save_file(self, file) -> str:
         def process_file(self, filepath) -> CIPPDataProcessor:
         def generate_excel_files(self, processor, session_id) -> dict:
     ```

### 10.2 Applying DIP (Dependency Inversion Principle)

**Current Violations:**
1. **Flask routes directly instantiate processors**
   - `processor = CIPPDataProcessor(filepath)` (app.py:60)
   - High-level module (Flask route) depends on low-level module (CIPPDataProcessor)
   - **Fix:** Inject via factory or dependency injection:
     ```python
     class DashboardService:
         def __init__(self, processor_factory, generator_factory):
             self.processor_factory = processor_factory
             self.generator_factory = generator_factory
     ```

### 10.3 Applying DRY (Don't Repeat Yourself)

**Current Violations:**
1. **Chart generation duplicated in Flask and Dash**
   - `generate_plotly_charts()` (app.py:181-308)
   - `update_*_chart()` callbacks (app_dash.py:321-631)
   - **Fix:** Extract to shared `charts.py` module:
     ```python
     # charts.py
     class ChartFactory:
         def create_progress_chart(self, stage_summary) -> go.Figure:
         def create_pipe_progress_chart(self, stage_by_pipe) -> go.Figure:
         # ... etc.
     ```

2. **Table writing duplicated in excel_generator.py and excel_generator_v2.py**
   - `_write_table()` appears in both files (nearly identical)
   - **Fix:** Extract to base class or utility module

### 10.4 Applying ODD (Observability-Driven Development)

**Current Gaps:**
- No structured logging
- No metrics
- No tracing

**Proposed Observability Strategy:**

```python
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

# In CIPPDataProcessor.load_data():
logger.info("data_loading_started",
    filepath=self.file_path,
    sheet_name=self.sheet_name
)

# After validation:
logger.info("data_loading_completed",
    segments_loaded=len(self.segments),
    total_footage=self.total_footage,
    duration_ms=duration
)

# On errors:
logger.error("data_loading_failed",
    filepath=self.file_path,
    error=str(e),
    exc_info=True
)
```

**Metrics to Track:**
- Upload count (by success/failure)
- Processing duration (p50, p95, p99)
- Excel generation duration per approach
- Session count (active, total)
- File size distribution

### 10.5 Test Coverage Priority (FIRST Principles)

**Critical Paths to Test First:**

1. **Stage Computation** (data_processor.py:126-139)
   ```python
   # tests/unit/test_stage_computation.py
   def test_stage_grouted_done():
       segment = {"grout_state_date": "2025-01-01", ...}
       assert processor._compute_stage(segment) == "Grouted/Done"

   def test_stage_priority_order():
       segment = {
           "grout_state_date": "2025-01-01",
           "lining_date": "2025-01-02",  # Should be ignored
           ...
       }
       assert processor._compute_stage(segment) == "Grouted/Done"  # Grout wins
   ```

2. **Data Validation** (data_processor.py:105-112)
   ```python
   def test_valid_segment_accepted():
       assert processor._is_valid_segment(1, 100.0) == True

   def test_invalid_video_id_rejected():
       assert processor._is_valid_segment(0, 100.0) == False
       assert processor._is_valid_segment(-1, 100.0) == False

   def test_invalid_map_length_rejected():
       assert processor._is_valid_segment(1, 0) == False
       assert processor._is_valid_segment(1, -1) == False
   ```

3. **Table Generation** (data_processor.py:141-283)
   ```python
   def test_stage_footage_summary_correct():
       processor.segments = [
           {"stage": "Not Started", "map_length": 100},
           {"stage": "Not Started", "map_length": 200},
           {"stage": "Lined", "map_length": 300},
       ]
       processor.total_footage = 600

       result = processor.get_stage_footage_summary()

       not_started = next(r for r in result if r["Stage"] == "Not Started")
       assert not_started["Segment_Count"] == 2
       assert not_started["Total_Feet"] == 300.0
       assert not_started["Pct_of_Total_Feet"] == 0.5
   ```

---

## 11. Final Recommendations

### 11.1 Immediate Actions (Do First)

1. **Add `.gitignore`** (if not exists)
   ```
   uploads/
   outputs/
   *.pyc
   __pycache__/
   .env
   .venv/
   ```

2. **Create `config.py`** (environment-based configuration)

3. **Add structured logging** (use `structlog` or Python `logging` with JSON formatter)

4. **Write 10 critical unit tests** (stage computation, validation, table generation)

5. **Document Dash app in README** (it's currently undocumented)

### 11.2 Short-Term Refactors (Next 2 Weeks)

1. **Extract service layer** (decouple Flask routes from business logic)

2. **Deduplicate chart generation** (shared module for Flask and Dash)

3. **Add input validation** (pipe size ranges, date sequences, missing data warnings)

4. **Implement background job processing** (RQ or Celery for Excel generation)

5. **Add database layer** (SQLite for dev, PostgreSQL for prod)

### 11.3 Long-Term Enhancements (Next 3 Months)

1. **Add authentication** (Flask-Login or JWT)

2. **Implement multi-project comparison** (upload multiple files, compare dashboards)

3. **Add time-series analysis** (completion velocity, burndown charts)

4. **Containerize with Docker** (Dockerfile, docker-compose.yml)

5. **Deploy to cloud** (AWS, GCP, or Azure with HTTPS, autoscaling)

---

## 12. Glossary (Domain Terms)

| Term | Definition | Location in Code |
|------|-----------|------------------|
| **CIPP** | Cured-In-Place Pipe — rehabilitation method for underground pipes | Project name, README |
| **Shot Schedule** | Excel spreadsheet listing all pipe segments to be rehabilitated | Input file format |
| **Segment** | Individual pipe section with VIDEO ID, location, size, and completion status | Core entity (data_processor.py) |
| **Stage** | Completion status of a segment (6 levels: Not Started → Grouted/Done) | Computed value (data_processor.py:126-139) |
| **VIDEO ID** | Numeric identifier for each segment (≥1) | Validation key (data_processor.py:66) |
| **Map Length** | Length of pipe segment in feet | Measurement field (data_processor.py:67) |
| **Pipe Size** | Diameter of pipe in inches | Dimension field (data_processor.py:77) |
| **Easement** | Segment located on private property (requires easement agreement) | Boolean flag (data_processor.py:84) |
| **Traffic Control** | Segment requiring road closure or traffic management | Boolean flag (data_processor.py:85) |
| **Prep Complete** | Segment preparation finished (cleaning, inspection) | Stage flag (data_processor.py:79) |
| **Ready to Line** | Segment certified ready for liner installation | Stage flag (data_processor.py:80) |
| **Lining Date** | Date liner installed | Stage trigger (data_processor.py:81) |
| **Final Post TV Date** | Date post-installation video inspection completed | Stage trigger (data_processor.py:82) |
| **Grout State Date** | Date grouting completed (final stage) | Stage trigger (data_processor.py:83) |
| **Approach** | One of 3 Excel generation methods (openpyxl, xlsxwriter, Plotly) | excel_generator.py |
| **Session** | User upload session, identified by timestamp | Flask/Dash apps |
| **Dashboard_Data** | Excel sheet containing 5 summary tables | Excel output (excel_generator.py) |
| **Dashboard** | Excel sheet containing 5 visualizations | Excel output (excel_generator.py) |

---

**End of Digest Synopsis** — Use this document as the **canonical map** for all refactoring, debugging, and extension work on the ssREFINEMENT (CIPP Dashboard Generator) project.
