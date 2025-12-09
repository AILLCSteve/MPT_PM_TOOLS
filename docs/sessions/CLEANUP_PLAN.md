# Repository Cleanup Plan
Generated: 2025-12-08

## Current State Summary

**Major Issues Identified:**
1. 📁 450M+ of legacy/archived code in root directory
2. 📄 20+ scattered markdown documentation files
3. 🔄 Duplicate codebases (`ssREFINEMENT/`, `Bid-Spec Analysis for CIPP/`)
4. 🗂️ Inconsistent archival structure (some folders prefixed `archive_*`, others not)
5. 📝 Session documentation and implementation notes cluttering root

**Production Critical (Must Not Break):**
- `app.py` - Main Flask entrypoint referenced in `render.yaml`
- `gunicorn_config.py` - Production server config
- `services/hotdog/` - HOTDOG AI orchestrator
- `services/cipp_dashboard/` - CIPP dashboard service
- `config/` - Runtime configuration
- `shared/` - Branding assets

---

## Proposed Target Directory Structure

```
PM Tools Buildout/
├── app.py                          # Main Flask application (UNCHANGED)
├── gunicorn_config.py              # Production config (UNCHANGED)
├── requirements.txt                # Dependencies (UNCHANGED)
├── render.yaml                     # Render deployment config (UNCHANGED)
│
├── services/                       # Live microservices (UNCHANGED)
│   ├── hotdog/                     # HOTDOG AI orchestrator
│   ├── cipp_dashboard/             # CIPP dashboard service
│   ├── document_extractor.py       # Shared utilities
│   ├── excel_dashboard.py
│   ├── excel_dashboard_generator.py
│   ├── pdf_extractor.py
│   └── __init__.py
│
├── config/                         # Runtime configuration (UNCHANGED)
│   ├── cipp_questions_default.json
│   └── model_config.json
│
├── shared/                         # Branding assets (UNCHANGED)
│   └── BRANDING_README.md
│
├── images/                         # Image assets (UNCHANGED)
│
├── docs/                           # 📂 NEW - Consolidated documentation
│   ├── README.md                   # Symlink to root README.md
│   ├── architecture/               # Architecture documentation
│   │   ├── ARCHITECTURE.md         # ← from root
│   │   ├── HOTDOG_AI_ARCHITECTURE.md
│   │   ├── HOTDOG_FLOWCHART.md
│   │   └── digestsynopsisSUMMARY.md
│   ├── deployment/                 # Deployment guides
│   │   ├── DEPLOYMENT.md           # ← from root
│   │   ├── DEPLOYMENT_READY.md
│   │   └── QUICK_START.md
│   ├── research/                   # Research and analysis docs
│   │   ├── EXCEL_DASHBOARD_RESEARCH.md
│   │   ├── NEXUS_INTEGRATION_ANALYSIS.md
│   │   └── REWRITE_REQUIREMENTS.md
│   └── sessions/                   # Session summaries and implementation notes
│       ├── COMPLETE_REBUILD_SPEC.md
│       ├── HOTDOG_IMPLEMENTATION_SUMMARY.md
│       ├── IMPLEMENTATION_SUMMARY_2025-11-30.md
│       ├── PROJECT_SUMMARY.md
│       ├── SESSION_COMPLETE_2025-11-30.md
│       ├── SESSION_COMPLETE_2025-12-01.md
│       ├── SESSION_SUMMARY.md
│       ├── SESSION_SUMMARY_BACKUP.md
│       ├── VISUALIZATION_FIX_SUMMARY.md
│       └── WORKFLOW_AUDIT_2025-12-01.md
│
├── scripts/                        # 📂 NEW - Maintenance scripts
│   ├── brand_cipp_analyzer.py      # ← from root
│   └── fix_cipp_branding.py        # ← from root
│
├── outputs/                        # 📂 NEW - Runtime outputs (consolidated)
│   ├── logs/                       # ← from "Logs and Spec Output/logs/"
│   └── spec-output/                # ← from "Logs and Spec Output/spec output/"
│
├── legacy/                         # 📂 NEW - Archived code and experiments
│   ├── LEGACY.md                   # Index of archived items
│   ├── apps/                       # Legacy applications
│   │   ├── legacy-gevent-app/
│   │   │   └── app_legacy_gevent.py
│   │   ├── sse-test/
│   │   │   └── app_test_sse.py
│   │   └── progress-estimator/     # ← from "Progress Estimator/"
│   │       └── (HTML/CSS/JS files)
│   ├── services/                   # Legacy/archived services
│   │   ├── archive-complete-legacy-analysis/  # ← from root
│   │   ├── archive-legacy-sync-worker/        # ← from root
│   │   ├── bid-spec-analysis-v1/              # ← from "Bid-Spec Analysis for CIPP/"
│   │   └── ssrefinement-experiment/           # ← from "ssREFINEMENT/"
│   └── refactoring-ideas/          # ← from services/cipp_dashboard/RefactoringCodebaseIdeas/
│
├── .claude/                        # Claude Code config (UNCHANGED)
├── venv/                           # Python virtual env (UNCHANGED, gitignored)
├── __pycache__/                    # Python cache (UNCHANGED, gitignored)
├── README.md                       # Main README (stays in root, minor update)
├── claude.md                       # Engineering playbook (UNCHANGED)
└── .gitignore                      # Git ignore rules (update if needed)
```

---

## Detailed Migration Mapping

### 1. Documentation Consolidation → `docs/`

| Current Path | New Path | Reason |
|--------------|----------|--------|
| `ARCHITECTURE.md` | `docs/architecture/ARCHITECTURE.md` | Core architecture doc |
| `HOTDOG_AI_ARCHITECTURE.md` | `docs/architecture/HOTDOG_AI_ARCHITECTURE.md` | HOTDOG architecture |
| `HOTDOG_FLOWCHART.md` | `docs/architecture/HOTDOG_FLOWCHART.md` | HOTDOG flowchart |
| `digestsynopsisSUMMARY.md` | `docs/architecture/digestsynopsisSUMMARY.md` | Generated codebase map |
| `DEPLOYMENT.md` | `docs/deployment/DEPLOYMENT.md` | Deployment guide |
| `DEPLOYMENT_READY.md` | `docs/deployment/DEPLOYMENT_READY.md` | Deployment checklist |
| `QUICK_START.md` | `docs/deployment/QUICK_START.md` | Quick start guide |
| `EXCEL_DASHBOARD_RESEARCH.md` | `docs/research/EXCEL_DASHBOARD_RESEARCH.md` | Research notes |
| `NEXUS_INTEGRATION_ANALYSIS.md` | `docs/research/NEXUS_INTEGRATION_ANALYSIS.md` | Integration analysis |
| `REWRITE_REQUIREMENTS.md` | `docs/research/REWRITE_REQUIREMENTS.md` | Requirements doc |
| `COMPLETE_REBUILD_SPEC.md` | `docs/sessions/COMPLETE_REBUILD_SPEC.md` | Rebuild spec |
| `HOTDOG_IMPLEMENTATION_SUMMARY.md` | `docs/sessions/HOTDOG_IMPLEMENTATION_SUMMARY.md` | Implementation notes |
| `IMPLEMENTATION_SUMMARY_2025-11-30.md` | `docs/sessions/IMPLEMENTATION_SUMMARY_2025-11-30.md` | Session summary |
| `PROJECT_SUMMARY.md` | `docs/sessions/PROJECT_SUMMARY.md` | Project summary |
| `SESSION_COMPLETE_2025-11-30.md` | `docs/sessions/SESSION_COMPLETE_2025-11-30.md` | Session completion |
| `SESSION_COMPLETE_2025-12-01.md` | `docs/sessions/SESSION_COMPLETE_2025-12-01.md` | Session completion |
| `SESSION_SUMMARY.md` | `docs/sessions/SESSION_SUMMARY.md` | Session summary |
| `SESSION_SUMMARY_BACKUP.md` | `docs/sessions/SESSION_SUMMARY_BACKUP.md` | Session backup |
| `VISUALIZATION_FIX_SUMMARY.md` | `docs/sessions/VISUALIZATION_FIX_SUMMARY.md` | Fix summary |
| `WORKFLOW_AUDIT_2025-12-01.md` | `docs/sessions/WORKFLOW_AUDIT_2025-12-01.md` | Workflow audit |

### 2. Scripts Consolidation → `scripts/`

| Current Path | New Path | Reason |
|--------------|----------|--------|
| `brand_cipp_analyzer.py` | `scripts/brand_cipp_analyzer.py` | One-off branding script |
| `fix_cipp_branding.py` | `scripts/fix_cipp_branding.py` | One-off fix script |

### 3. Legacy Code Archival → `legacy/`

| Current Path | New Path | Reason |
|--------------|----------|--------|
| `app_legacy_gevent.py` | `legacy/apps/legacy-gevent-app/app_legacy_gevent.py` | Superseded by threading app.py |
| `app_test_sse.py` | `legacy/apps/sse-test/app_test_sse.py` | Testing artifact |
| `Progress Estimator/` | `legacy/apps/progress-estimator/` | Old HTML-based estimator |
| `archive_complete_legacy_analysis/` | `legacy/services/archive-complete-legacy-analysis/` | Already archived, normalize path |
| `archive_legacy_sync_worker/` | `legacy/services/archive-legacy-sync-worker/` | Already archived, normalize path |
| `Bid-Spec Analysis for CIPP/` | `legacy/services/bid-spec-analysis-v1/` | Superseded by services/cipp_dashboard |
| `ssREFINEMENT/` | `legacy/services/ssrefinement-experiment/` | Experimental refinement branch |
| `services/cipp_dashboard/RefactoringCodebaseIdeas/` | `legacy/refactoring-ideas/` | Refactoring notes |

### 4. Outputs Consolidation → `outputs/`

| Current Path | New Path | Reason |
|--------------|----------|--------|
| `Logs and Spec Output/logs/` | `outputs/logs/` | Runtime logs |
| `Logs and Spec Output/spec output/` | `outputs/spec-output/` | Runtime spec outputs |

### 5. Files Staying in Root (No Change)

- `app.py` - Main entrypoint (referenced in render.yaml)
- `gunicorn_config.py` - Production config
- `requirements.txt` - Dependencies
- `render.yaml` - Render deployment config
- `README.md` - Main documentation (will be updated to reference docs/)
- `claude.md` - Engineering playbook
- `.gitignore` - Git ignore rules

---

## Expected Benefits

1. **Reduced Root Clutter**: From 30+ files to ~10 core files
2. **Clear Separation**: Live code vs legacy vs documentation vs outputs
3. **Easier Navigation**: Logical folder structure by purpose
4. **Faster Onboarding**: New developers can quickly understand the project
5. **Safer Evolution**: Legacy code is archived but accessible, not deleted
6. **Consistent Archival**: All legacy items follow same pattern under `legacy/`
7. **Size Reduction**: ~450M of legacy code clearly isolated

---

## Risk Mitigation

✅ **All changes will be on a new Git branch** (`chore/cleanup-project-20251208`)
✅ **Production code paths unchanged** (app.py, services/, config/, shared/)
✅ **No code deletion** - everything moved to `legacy/` with full Git history
✅ **Import paths validated** - no imports from legacy folders in live code
✅ **Deployment config unchanged** - render.yaml stays the same
✅ **Tests will be run** - smoke checks before finalizing

---

## Next Steps (Pending Approval)

1. ✋ **User Approval Required**: Please type `APPROVE CLEANUP` to proceed
2. Create cleanup branch: `chore/cleanup-project-20251208`
3. Execute migrations in small, logical commits
4. Update import paths (if any)
5. Update README.md with new structure
6. Create `legacy/LEGACY.md` index
7. Create `docs/README.md` with navigation
8. Run smoke tests
9. Present final changelog
