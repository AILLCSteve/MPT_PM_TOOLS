# Repository Cleanup Inventory
Generated: 2025-12-08

## Repository Structure Analysis

### LIVE PRODUCTION CODE (Deployed on Render)
| Path | Type | Purpose | Notes |
|------|------|---------|-------|
| `app.py` | Entrypoint | Main Flask application | **LIVE** - Referenced in render.yaml |
| `gunicorn_config.py` | Config | Production server config | **LIVE** - Used by Render deployment |
| `render.yaml` | Config | Render deployment config | **LIVE** - Defines production service |
| `requirements.txt` | Config | Python dependencies | **LIVE** - Required for deployment |
| `services/hotdog/` | Service | HOTDOG AI document analysis | **LIVE** - Imported by app.py |
| `services/cipp_dashboard/` | Service | CIPP dashboard service | **LIVE** - Active service |
| `services/*.py` | Utilities | PDF/Excel/document extractors | **LIVE** - Shared utilities |
| `config/` | Config | JSON configs for AI models, questions | **LIVE** - Runtime configuration |
| `shared/` | Shared | Branding assets (5.8M) | **LIVE** - Branding resources |

### LEGACY/OBSOLETE CODE (Candidates for archival)
| Path | Type | Status | Reason |
|------|------|--------|--------|
| `app_legacy_gevent.py` | Legacy App | Superseded | Old gevent-based version, replaced by threading in app.py |
| `app_test_sse.py` | Test File | Obsolete | Testing artifact, not used in production |
| `archive_complete_legacy_analysis/` | Archive (226M!) | Legacy | Already marked as archive, contains old CIPP analysis |
| `archive_legacy_sync_worker/` | Archive | Legacy | Already marked as archive, old sync worker |
| `ssREFINEMENT/` | Experiment | Duplicate | Contains duplicate code (app.py, data_processor.py, etc.) - appears to be a refinement branch |
| `brand_cipp_analyzer.py` | Script | One-off | Branding utility script, one-time use |
| `fix_cipp_branding.py` | Script | One-off | Fix script, one-time use |
| `Bid-Spec Analysis for CIPP/` | Legacy (226M!) | Superseded | Old CIPP analysis folder, superseded by services/cipp_dashboard |

### DOCUMENTATION (Scattered - needs consolidation)
| Path | Type | Status | Notes |
|------|------|--------|-------|
| `README.md` | Core Docs | **Keep** | Main project documentation |
| `ARCHITECTURE.md` | Core Docs | **Keep** | Architecture documentation |
| `claude.md` | Engineering Guide | **Keep** | Engineering playbook (from system context) |
| `DEPLOYMENT.md` | Core Docs | **Keep** | Deployment instructions |
| `QUICK_START.md` | Core Docs | **Keep** | Quick start guide |
| `digestsynopsisSUMMARY.md` | Generated | **Keep** | Generated codebase digest |
| `PROJECT_SUMMARY.md` | Session Docs | Archive | Project summary |
| `DEPLOYMENT_READY.md` | Session Docs | Archive | Deployment readiness checklist |
| `COMPLETE_REBUILD_SPEC.md` | Session Docs | Archive | Rebuild specification |
| `HOTDOG_*.md` (3 files) | Session Docs | Archive | HOTDOG implementation session docs |
| `IMPLEMENTATION_SUMMARY_*.md` | Session Docs | Archive | Implementation summaries |
| `SESSION_*.md` (4 files) | Session Docs | Archive | Session completion summaries |
| `WORKFLOW_AUDIT_*.md` | Session Docs | Archive | Workflow audit |
| `VISUALIZATION_FIX_SUMMARY.md` | Session Docs | Archive | Fix summary |
| `NEXUS_INTEGRATION_ANALYSIS.md` | Research Docs | Archive | Integration analysis |
| `EXCEL_DASHBOARD_RESEARCH.md` | Research Docs | Archive | Research notes |
| `REWRITE_REQUIREMENTS.md` | Session Docs | Archive | Rewrite requirements |
| `shared/BRANDING_README.md` | Feature Docs | **Keep in place** | Branding guide for shared/ folder |

### STATIC ASSETS & OUTPUT
| Path | Type | Status | Notes |
|------|------|--------|-------|
| `Progress Estimator/` | Static HTML | Legacy | Old HTML/CSS/JS estimator tools (269K) |
| `images/` | Assets | **Keep** | Image assets (15M) |
| `Logs and Spec Output/` | Runtime Output | **Keep** | Runtime logs and spec outputs |
| `services/cipp_dashboard/uploads/` | Runtime | **Keep** | User uploads (runtime) |
| `services/cipp_dashboard/outputs/` | Runtime | **Keep** | Generated outputs (runtime) |
| `services/cipp_dashboard/RefactoringCodebaseIdeas/` | Notes | Archive | Refactoring notes/ideas |

### TOOLING & INFRASTRUCTURE
| Path | Type | Status | Notes |
|------|------|--------|-------|
| `.claude/` | IDE Config | **Keep** | Claude Code configuration |
| `venv/` | Python Env | **Keep** | Virtual environment (gitignored, 67M) |
| `__pycache__/` | Build Artifacts | **Keep** | Python bytecode cache (gitignored) |

## Size Analysis
- **Largest directories**:
  - `Bid-Spec Analysis for CIPP/` - 226M (LEGACY)
  - `archive_complete_legacy_analysis/` - 226M (ALREADY ARCHIVED)
  - `venv/` - 67M (gitignored)
  - `images/` - 15M (live assets)
  - `shared/` - 5.8M (live branding)

## Classification Summary
- ✅ **Live Production**: 8 core files/folders
- 🗄️ **Legacy/Archive Candidates**: 8 folders/files (~450M+)
- 📄 **Documentation to Consolidate**: 20+ markdown files
- 🏗️ **Static/Output**: 4 folders
- ⚙️ **Infrastructure**: 3 folders (keep as-is)

## Key Findings
1. **Duplicate Archive Folders**: `archive_*` folders already exist but `Bid-Spec Analysis for CIPP/` and `ssREFINEMENT/` should join them
2. **Documentation Explosion**: 20+ markdown files scattered in root, should consolidate into `docs/` folder
3. **Session Documentation**: Multiple session summaries and implementation docs should be archived
4. **Large Legacy Folders**: 450M+ of legacy code that can be safely archived
5. **Clear Production Entrypoint**: `app.py` + `render.yaml` clearly define what's live
