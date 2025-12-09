# PM Tools Suite - Service Structure Reference
**Updated**: 2025-12-08

This document clarifies the location and purpose of all services, tools, and utilities in the production codebase.

---

## Production Services (`services/`)

### Core Python Modules

| File | Purpose | Used By | Lines |
|------|---------|---------|-------|
| `document_extractor.py` | Multi-format document extraction (PDF, DOCX, RTF) with strategy pattern | app.py, hotdog/layers.py | 425 |
| `pdf_extractor.py` | PDF-specific extraction strategies (PyMuPDF, PyPDF2, pdfplumber, pdfminer) | document_extractor.py | 252 |
| `excel_dashboard.py` | Executive Excel dashboard generation with openpyxl and charts | app.py (line 381) | 351 |

### HOTDOG AI Orchestration (`services/hotdog/`)

Complete 7-layer AI analysis system:

| File | Layer | Purpose | Lines |
|------|-------|---------|-------|
| `orchestrator.py` | Coordinator | Central orchestration of all layers | 696 |
| `models.py` | Data Models | DDD entities and value objects | 304 |
| `layers.py` | 0, 1, 2, 6 | Document ingestion, config loading, expert generation, output compilation | 612 |
| `multi_expert_processor.py` | Layer 3 | Parallel expert question answering | 431 |
| `smart_accumulator.py` | Layer 4 | Smart answer deduplication and merging | 369 |
| `second_pass_processor.py` | Layer 5 | Gap filling and confidence boosting | 488 |
| `token_optimizer.py` | Utility | Token budget management | 277 |
| `output_compiler.py` | Layer 6 | Final compilation and formatting | 453 |

### Visual Project Summary (`services/cipp_dashboard/`)

Dashboard service for CIPP project visualization:

| File | Purpose | Used By | Lines |
|------|---------|---------|-------|
| `dash_app.py` | Dash/Plotly interactive dashboard | app.py (line 450+) | 1,520 |
| `data_processor.py` | Excel data processing and table generation | dash_app.py | 331 |
| `excel_generator_v2.py` | Multi-approach Excel export (native charts, enhanced, Plotly) | dash_app.py | 329 |

**Subdirectories:**
- `uploads/` - User-uploaded Excel files (runtime)
- `outputs/` - Generated dashboard Excel files (runtime)

---

## Static HTML Tools (Served from `legacy/apps/`)

These are **frontend-only applications** (HTML/CSS/JS), not Python services.

### Progress Estimator

**Location**: `legacy/apps/progress-estimator/`

**Files**:
- `CIPPEstimator_Comprehensive.html` - Main production estimator
- `CIPPEstimator_Unified.html` - Unified timeline mode
- `ProgEstimator.html` - Original estimator
- `ProgEstimator_branded.html` - Branded version
- `script.js`, `script_improved.js` - JavaScript logic
- `styles.css`, `styles_improved.css` - Styling

**Served by**: `app.py` route `/progress-estimator` (line 443)

**How it works**:
1. User clicks "Launch Estimator" on landing page
2. Flask serves static HTML from legacy folder
3. All calculations run client-side in JavaScript
4. No backend processing required

### CIPP Analyzer (Legacy HTML Version)

**Location**: `legacy/services/bid-spec-analysis-v1/`

**Files**:
- `cipp_analyzer_clean.html` - Standalone HTML analyzer
- `cipp_analyzer_complete.html` - Complete version
- `cipp_analyzer_branded.html` - Branded version

**Served by**: `app.py` route `/cipp-analyzer` (line 438)

**Note**: This is the OLD standalone HTML version. The production HOTDOG AI analyzer is the `/api/analyze` endpoint, not this HTML file.

---

## Configuration (`config/`)

| File | Purpose | Format |
|------|---------|--------|
| `cipp_questions_default.json` | Default question set for HOTDOG analysis | JSON (sections → questions) |
| `model_config.json` | OpenAI model configuration and token budgets | JSON (model specs, optimization strategy) |

---

## Shared Assets (`shared/`)

Branding assets and common resources:
- **Served by**: `app.py` route `/shared/<path:filename>` (line 74)
- **Contains**: Images, CSS, branding materials
- **Structure**: `shared/assets/images/`, `shared/assets/css/`

---

## Why Progress Estimator is in Legacy

The Progress Estimator is a **standalone client-side application** built with vanilla HTML/CSS/JS. It doesn't use:
- Python backend processing
- Database storage
- Server-side calculations
- AI/ML models

It was moved to `legacy/apps/` because:
1. It's not a Python service module
2. It's a complete self-contained frontend app
3. Flask only needs to serve it as a static file
4. Keeping it separate from `services/` maintains clean architecture

---

## Services Directory Structure (Clean)

```
services/
├── __init__.py                    # Package initialization
├── document_extractor.py          # Multi-format extraction
├── pdf_extractor.py               # PDF extraction strategies
├── excel_dashboard.py             # Excel generation (HOTDOG results)
├── hotdog/                        # HOTDOG AI orchestration
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── models.py
│   ├── layers.py
│   ├── multi_expert_processor.py
│   ├── smart_accumulator.py
│   ├── second_pass_processor.py
│   ├── token_optimizer.py
│   └── output_compiler.py
└── cipp_dashboard/                # Visual project summary
    ├── __init__.py
    ├── dash_app.py
    ├── data_processor.py
    ├── excel_generator_v2.py
    ├── uploads/
    └── outputs/
```

**Total**: 4 top-level utilities + 2 service directories (hotdog, cipp_dashboard)

---

## Removed Redundancies

### Before Cleanup
- ❌ `services/excel_dashboard_generator.py` (415 lines) - Duplicate Excel generator

### After Cleanup
- ✅ Moved to `legacy/services/excel_dashboard_generator.py`
- ✅ Production uses single Excel generator: `excel_dashboard.py`
- ✅ No duplicate functionality in `services/`

---

## Quick Reference: Where to Find Things

| Need to... | Look in... |
|------------|-----------|
| Add HOTDOG AI functionality | `services/hotdog/orchestrator.py` |
| Modify document extraction | `services/document_extractor.py` |
| Change Excel dashboard formatting | `services/excel_dashboard.py` |
| Update visual project summary | `services/cipp_dashboard/dash_app.py` |
| Modify progress estimator logic | `legacy/apps/progress-estimator/script.js` |
| Change question sets | `config/cipp_questions_default.json` |
| Update AI model configuration | `config/model_config.json` |
| Add Flask routes | `app.py` |

---

## Testing Checklist

After any changes to services:

- [ ] Verify imports: `python -c "from services.hotdog import HotdogOrchestrator"`
- [ ] Check Excel generation: Test `/api/export/excel-dashboard/<session_id>`
- [ ] Test document extraction: Upload a PDF via `/api/upload`
- [ ] Verify HOTDOG analysis: Run full analysis via `/api/analyze`
- [ ] Check visual dashboard: Access `/cipp-dashboard/`
- [ ] Test progress estimator: Load `/progress-estimator`

---

**Maintained by**: AI LLC Development Team
**Last Cleanup**: 2025-12-08
**Status**: ✅ Production-ready, no redundancies
