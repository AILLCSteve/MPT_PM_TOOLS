# Architecture Overview - PM Tools Suite

Visual guide to the application architecture and data flow.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Landing    │  │     CIPP     │  │   Progress   │      │
│  │     Page     │  │   Analyzer   │  │  Estimator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     FLASK APPLICATION                         │
│                         (app.py)                              │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Main Application Factory                 │   │
│  │  - Route Management                                   │   │
│  │  - Error Handling                                     │   │
│  │  - CORS Configuration                                 │   │
│  │  - Static Asset Serving                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                  │
│  ┌─────────────────────────┴───────────────────────────┐   │
│  │                                                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────┐│   │
│  │  │   Routes     │  │   Static     │  │   API      ││   │
│  │  │   /          │  │   /shared    │  │  /health   ││   │
│  │  │   /cipp      │  │   Assets     │  │            ││   │
│  │  │   /progress  │  │              │  │            ││   │
│  │  └──────────────┘  └──────────────┘  └────────────┘│   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      FILE SYSTEM                             │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Shared     │  │    CIPP      │  │   Progress   │     │
│  │   Assets     │  │  Templates   │  │   Files      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow

### Landing Page Request

```
User Browser
    │
    │ GET /
    ▼
Flask App (app.py)
    │
    │ route: @app.route('/')
    │ function: index()
    ▼
File System
    │
    │ serves: index.html
    ▼
User Browser
    │
    │ renders HTML
    │ loads CSS from /shared/assets/css/common.css
    │ loads images from /shared/assets/images/
    ▼
Display Landing Page
```

### CIPP Analyzer Request

```
User Browser
    │
    │ GET /cipp-analyzer
    ▼
Flask App (app.py)
    │
    │ route: @app.route('/cipp-analyzer')
    │ function: cipp_analyzer()
    ▼
File System
    │
    │ serves: Bid-Spec Analysis for CIPP/cipp_analyzer_complete.html
    ▼
User Browser
    │
    │ renders CIPP Analyzer interface
    │ user uploads PDF
    │
    │ POST /cipp-analyzer/api/extract_pdf
    ▼
Flask App (app.py)
    │
    │ route: @app.route('/cipp-analyzer/api/extract_pdf')
    │ function: cipp_extract_pdf()
    │
    │ [Currently returns 501 - Not Implemented]
    │ [TODO: Integrate refactored PDF service]
    ▼
User Browser
    │
    │ displays extraction results
    ▼
```

### Progress Estimator Request

```
User Browser
    │
    │ GET /progress-estimator
    ▼
Flask App (app.py)
    │
    │ route: @app.route('/progress-estimator')
    │ function: progress_estimator()
    ▼
File System
    │
    │ serves: Progress Estimator/CleaningEstimateProto.html
    ▼
User Browser
    │
    │ GET /progress-estimator/script.js
    │ GET /progress-estimator/styles.css
    ▼
Flask App (app.py)
    │
    │ checks for improved versions
    │ serves: script_improved.js or script.js
    │ serves: styles_improved.css or styles.css
    ▼
User Browser
    │
    │ renders Progress Estimator
    │ all calculations happen client-side (JavaScript)
    │ no server requests needed for calculations
    ▼
Display Results
```

## Directory Structure & Responsibilities

```
PM Tools Buildout/
│
├── app.py                          ← MAIN APPLICATION ENTRY POINT
│   ├── Config class               ← Configuration management
│   ├── create_app()               ← Application factory
│   ├── register_routes()          ← URL routing
│   └── register_error_handlers()  ← Error handling
│
├── index.html                      ← Landing page (served by Flask)
│
├── shared/                         ← SHARED RESOURCES
│   └── assets/
│       ├── css/
│       │   └── common.css         ← Design system (CSS variables)
│       ├── images/
│       │   └── logo-placeholder.svg ← Company logo
│       └── js/                    ← Shared JavaScript (empty for now)
│
├── Bid-Spec Analysis for CIPP/    ← CIPP ANALYZER TOOL
│   ├── cipp_analyzer_complete.html ← Main interface (served by Flask)
│   └── refactored/                ← IMPROVED VERSION (not yet integrated)
│       ├── config.py              ← Configuration (SOLID: SRP)
│       ├── app.py                 ← Standalone Flask app
│       ├── services/
│       │   └── pdf_extractor.py   ← PDF service (SOLID: Strategy Pattern)
│       └── routes/
│           └── api.py             ← API endpoints (SOLID: SRP)
│
└── Progress Estimator/            ← PROGRESS ESTIMATOR TOOL
    ├── CleaningEstimateProto.html ← Main interface (served by Flask)
    ├── script_improved.js         ← Enhanced JavaScript (with validation)
    └── styles_improved.css        ← Enhanced CSS (with CSS variables)
```

## Component Interactions

### Modular Design

```
┌─────────────────────────────────────────────────────────┐
│                    Main Application                      │
│                       (app.py)                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │  Shared  │  │  Tool 1  │  │  Tool 2  │  ...        │
│  │  Assets  │  │  (CIPP)  │  │(Progress)│             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │              │                     │
│       │             │              │                     │
│       ▼             ▼              ▼                     │
│  ┌─────────────────────────────────────────┐           │
│  │          Independent Files               │           │
│  │  - HTML templates                        │           │
│  │  - JavaScript logic                      │           │
│  │  - CSS styles                            │           │
│  │  - API endpoints (optional)              │           │
│  └─────────────────────────────────────────┘           │
│                                                           │
└─────────────────────────────────────────────────────────┘

Benefits:
- Each tool is self-contained
- Tools can be developed independently
- Easy to add new tools
- Shared assets ensure consistent branding
```

## Data Flow Patterns

### Static Tool (Progress Estimator)

```
User Input → JavaScript Validation → Calculation → Display Results
                                    ↓
                             (No Server Request)
```

**Benefits:**
- Fast response (no network latency)
- No server load for calculations
- Works offline (after initial load)

### Server-Side Tool (CIPP Analyzer - Future)

```
User Upload PDF → Flask API → PDF Service → Extract Text → AI Analysis → Results
                      ↓            ↓             ↓              ↓
                  Validation   Strategy     Cleanup      Processing
                              Pattern
```

**Benefits:**
- Heavy processing on server
- Secure file handling
- Scalable architecture
- Multiple extraction strategies

## Deployment Architecture

### Development Environment

```
┌──────────────────────────────────────────┐
│         Developer Machine                 │
│                                           │
│  ┌────────────────────────────────┐     │
│  │  Python Virtual Environment     │     │
│  │  - Flask Development Server     │     │
│  │  - Port 5000                    │     │
│  │  - DEBUG=true                   │     │
│  │  - Hot reload enabled           │     │
│  └────────────────────────────────┘     │
│                                           │
└──────────────────────────────────────────┘
         │
         │ http://localhost:5000
         ▼
   Browser Testing
```

### Production Environment (Render)

```
┌────────────────────────────────────────────────────────┐
│                    Internet                             │
└────────────────────┬───────────────────────────────────┘
                     │ HTTPS
                     │ (SSL/TLS)
                     ▼
┌────────────────────────────────────────────────────────┐
│               Render.com Platform                       │
│                                                          │
│  ┌────────────────────────────────────────────────┐   │
│  │         Load Balancer / CDN                     │   │
│  └────────────────┬───────────────────────────────┘   │
│                   │                                     │
│  ┌────────────────▼───────────────────────────────┐   │
│  │         Gunicorn (WSGI Server)                  │   │
│  │         - Multiple Workers                       │   │
│  │         - Port binding                           │   │
│  └────────────────┬───────────────────────────────┘   │
│                   │                                     │
│  ┌────────────────▼───────────────────────────────┐   │
│  │         Flask Application                        │   │
│  │         - app.py                                 │   │
│  │         - DEBUG=false                            │   │
│  │         - LOG_LEVEL=INFO                         │   │
│  └────────────────┬───────────────────────────────┘   │
│                   │                                     │
│  ┌────────────────▼───────────────────────────────┐   │
│  │         File System                              │   │
│  │         - Static assets                          │   │
│  │         - Templates                              │   │
│  │         - Tool files                             │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└────────────────────────────────────────────────────────┘
```

## Scaling Strategy

### Current State (Single Instance)

```
Users → Render Server → Flask App (2 workers)
```

Suitable for:
- Up to 100 concurrent users
- Light to moderate load
- Development/staging
- Small team usage

### Scaled State (Future, if needed)

```
Users → Load Balancer → ┌─ Render Instance 1 (Flask + 4 workers)
                         ├─ Render Instance 2 (Flask + 4 workers)
                         └─ Render Instance 3 (Flask + 4 workers)
                                   │
                                   ▼
                              Database (if needed)
                                   │
                                   ▼
                           File Storage / CDN
```

Suitable for:
- 1000+ concurrent users
- Heavy load
- High availability requirements
- Enterprise usage

## Security Layers

```
┌────────────────────────────────────────────────────────┐
│                    Security Layers                      │
├────────────────────────────────────────────────────────┤
│                                                          │
│  Layer 1: Network Security                              │
│  ├─ HTTPS/TLS encryption (Render provides)             │
│  ├─ DDoS protection (Render provides)                   │
│  └─ Firewall (Render provides)                          │
│                                                          │
│  Layer 2: Application Security                          │
│  ├─ CORS configuration (Flask-CORS)                     │
│  ├─ Input validation (client + server)                  │
│  ├─ Error handling (no info leakage)                    │
│  └─ Environment variables (no secrets in code)          │
│                                                          │
│  Layer 3: Data Security                                 │
│  ├─ Temporary file cleanup                              │
│  ├─ No persistent storage of user data                  │
│  └─ Secure file handling                                │
│                                                          │
│  Layer 4: Code Security                                 │
│  ├─ Dependencies from requirements.txt only             │
│  ├─ Regular updates                                     │
│  └─ .gitignore prevents secret commits                  │
│                                                          │
└────────────────────────────────────────────────────────┘
```

## Adding New Tools - Integration Pattern

When adding a new tool, follow this pattern:

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Create Tool Directory                           │
│  └─ /New Tool Name/                                     │
│      ├─ index.html                                      │
│      ├─ script.js (if needed)                           │
│      └─ styles.css (if needed)                          │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Register Route in app.py                        │
│  @app.route('/new-tool-name')                           │
│  def new_tool():                                         │
│      return send_from_directory(config.NEW_TOOL_DIR,    │
│                                 'index.html')            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: Add to Landing Page (index.html)                │
│  <div class="tool-card">                                │
│    <h2>New Tool</h2>                                    │
│    <a href="/new-tool-name" class="btn">Launch</a>     │
│  </div>                                                  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: Update Health Check                             │
│  'tools': {                                              │
│    'new_tool': 'available'                              │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: Deploy                                           │
│  git add .                                               │
│  git commit -m "Added new tool"                         │
│  git push                                                │
│  └─ Render auto-deploys                                 │
└─────────────────────────────────────────────────────────┘
```

## Performance Characteristics

### Response Times (Expected)

| Endpoint | Expected Response Time | Notes |
|----------|----------------------|-------|
| `/` (Landing) | <100ms | Static HTML |
| `/health` | <50ms | JSON response |
| `/cipp-analyzer` | <200ms | HTML load |
| `/progress-estimator` | <200ms | HTML load |
| PDF Extraction | 2-10s | Depends on PDF size |
| JavaScript Calculations | <50ms | Client-side |

### Resource Usage

| Resource | Current | Scalable To |
|----------|---------|------------|
| RAM | 512 MB | 2+ GB |
| CPU | 0.5 cores | 4+ cores |
| Workers | 2 | 8+ |
| Concurrent Users | ~100 | 1000+ |

## Monitoring Points

```
┌─────────────────────────────────────────────────────────┐
│               Monitoring Dashboard                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Health Check Endpoint: /health                          │
│  ├─ Status: healthy/unhealthy                           │
│  ├─ Available tools                                      │
│  └─ Response time                                        │
│                                                           │
│  Application Logs:                                       │
│  ├─ Request logs                                         │
│  ├─ Error logs                                           │
│  └─ Performance metrics                                  │
│                                                           │
│  Uptime Monitoring:                                      │
│  ├─ UptimeRobot (external)                              │
│  ├─ Render built-in monitoring                          │
│  └─ Custom alerts                                        │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Technology Stack Summary

```
┌────────────────────────────────────────────────────────┐
│                   Technology Stack                      │
├────────────────────────────────────────────────────────┤
│                                                          │
│  Backend:                                               │
│  ├─ Python 3.11                                         │
│  ├─ Flask 3.0 (Web framework)                           │
│  ├─ Gunicorn (WSGI server)                              │
│  ├─ flask-cors (CORS handling)                          │
│  └─ PyPDF2/pdfplumber (PDF processing)                  │
│                                                          │
│  Frontend:                                              │
│  ├─ HTML5                                               │
│  ├─ CSS3 (with custom properties)                       │
│  ├─ Vanilla JavaScript (ES6+)                           │
│  └─ No frameworks (lightweight)                         │
│                                                          │
│  Infrastructure:                                        │
│  ├─ Render.com (hosting)                                │
│  ├─ Git (version control)                               │
│  ├─ GitHub/GitLab (repository)                          │
│  └─ Let's Encrypt (SSL certificates)                    │
│                                                          │
│  Development:                                           │
│  ├─ Virtual environments (venv)                         │
│  ├─ pip (package management)                            │
│  └─ git (source control)                                │
│                                                          │
└────────────────────────────────────────────────────────┘
```

---

## Summary

The PM Tools Suite uses a **modular, scalable architecture** that:

✅ Separates concerns (presentation, business logic, data)
✅ Follows SOLID principles for maintainability
✅ Supports easy addition of new tools
✅ Provides consistent branding through shared assets
✅ Scales horizontally when needed
✅ Includes comprehensive security layers
✅ Monitors health and performance
✅ Deploys easily to multiple platforms

**Key Design Decisions:**

1. **Flask over Django**: Lightweight, flexible, perfect for microservices
2. **Monorepo Structure**: All tools in one repository for simplicity
3. **Shared Assets**: Consistent branding without duplication
4. **Client-Side Calculations**: Reduces server load for simple tools
5. **Modular Routes**: Easy to add/remove tools without affecting others

For implementation details, see:
- [README.md](README.md) - Full documentation
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Detailed changes
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
