# Legacy Code Archive
Last Updated: 2025-12-08

This directory contains archived, superseded, and experimental code that is no longer part of the active production system but is preserved for historical reference.

## 📋 Archive Index

### Legacy Applications (`legacy/apps/`)

| Folder | Original Path | Reason for Archival | Date Archived |
|--------|---------------|---------------------|---------------|
| `legacy-gevent-app/` | `app_legacy_gevent.py` | Superseded by threading-based `app.py` | 2025-12-08 |
| `sse-test/` | `app_test_sse.py` | Testing artifact, not used in production | 2025-12-08 |
| `progress-estimator/` | `Progress Estimator/` | Static HTML/CSS/JS estimator tools, superseded by Flask-based tools | 2025-12-08 |

**Total Size**: ~270KB

### Legacy Services (`legacy/services/`)

| Folder | Original Path | Reason for Archival | Date Archived |
|--------|---------------|---------------------|---------------|
| `archive_complete_legacy_analysis/` | `archive_complete_legacy_analysis/` | Already archived, normalized path | 2025-12-08 |
| `archive_legacy_sync_worker/` | `archive_legacy_sync_worker/` | Already archived, normalized path | 2025-12-08 |
| `bid-spec-analysis-v1/` | `Bid-Spec Analysis for CIPP/` | Version 1 of CIPP analysis, superseded by `services/cipp_dashboard/` and `services/hotdog/` | 2025-12-08 |
| `ssrefinement-experiment/` | `ssREFINEMENT/` | Experimental refinement branch with duplicate codebase, functionality merged into production | 2025-12-08 |

**Total Size**: ~450MB

#### Details: `bid-spec-analysis-v1/`
- **Original Purpose**: First version of CIPP specification analyzer
- **Key Files**:
  - `cipp_analyzer_main.py` - Main analyzer script
  - `cipp_analyzer_complete.html` - Standalone HTML interface
  - `ai_processing_architecture.md` - Architecture documentation
  - `refactored/` - Early refactoring attempt
- **Superseded By**: `services/cipp_dashboard/` and `services/hotdog/orchestrator.py`
- **Notes**: Contains valuable architectural thinking and prompt engineering that informed current implementation

#### Details: `ssrefinement-experiment/`
- **Original Purpose**: Experimental dashboard refinement with Dash/Plotly
- **Key Files**:
  - `app.py` - Flask app
  - `app_dash.py` - Dash dashboard app (43KB)
  - `excel_generator_v2.py` - Excel generation logic
  - `data_processor.py` - Data processing utilities
- **Superseded By**: `services/cipp_dashboard/dash_app.py`
- **Notes**: Successful experiment, functionality merged into production codebase

### Refactoring Ideas (`legacy/refactoring-ideas/`)

| Folder | Original Path | Reason for Archival | Date Archived |
|--------|---------------|---------------------|---------------|
| `cipp-dashboard/` | `services/cipp_dashboard/RefactoringCodebaseIdeas/` | Planning notes and refactoring ideas, not production code | 2025-12-08 |

**Total Size**: ~5KB

## 🔍 How to Use This Archive

### Viewing Archived Code
All archived code is preserved in Git history and can be accessed:
```bash
# View file as it was before archival
git log --all --full-history -- "Bid-Spec Analysis for CIPP/*"

# Restore a specific archived file to working directory (for reference)
git show HEAD~5:app_legacy_gevent.py > temp_legacy_app.py
```

### Why We Archive (Not Delete)
1. **Historical Reference**: Understanding past approaches and decisions
2. **Code Recovery**: Ability to recover specific implementations if needed
3. **Learning**: Archived experiments document what was tried and why
4. **Compliance**: Maintain complete project history

### When to Archive vs. Delete
- **Archive** (move to `legacy/`): Superseded code, experiments, old versions
- **Delete** (remove entirely): Temporary files, build artifacts, sensitive data

## ⚠️ Important Notes

- **Do NOT import** from legacy folders in production code
- **Do NOT run** archived applications without review (dependencies may be outdated)
- **Do NOT deploy** archived code to production
- If you need functionality from archived code:
  1. Review the current production implementation first
  2. Extract only the needed logic
  3. Update and test thoroughly before using

## 📚 Related Documentation

- **Architecture History**: See `docs/architecture/` for evolution of system design
- **Session Notes**: See `docs/sessions/` for implementation context and decisions
- **Current System**: See root `README.md` and `docs/deployment/QUICK_START.md`

---

*This archive is maintained as part of the PM Tools Suite repository cleanup (Dec 2025)*
