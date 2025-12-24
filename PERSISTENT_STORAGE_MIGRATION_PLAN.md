# Persistent Storage Migration Plan
**Date Created**: 2024-12-24
**Status**: Planning Phase
**Priority**: HIGH - Critical bug affecting production users

---

## Executive Summary

**Problem**: In-memory dict storage (`completed_analyses`, `partial_analyses`, `analysis_results`) loses all data when Gunicorn workers restart (every 1000 requests). Users experience 404 errors when trying to access completed analyses or export results.

**Root Cause**: Worker restarts clear all in-memory Python dicts. As traffic increased, workers restart more frequently, making the issue more visible.

**Solution**: Migrate to **Neon DB** (serverless PostgreSQL) for persistent storage of session data, analysis results, and metadata.

**Timeline**:
- Immediate (Today): Fix frontend button states + disable worker restarts
- Short-term (This Week): Deploy Neon DB migration
- Long-term (Ongoing): Admin dashboard for permanent analysis archive

---

## Why Neon DB Instead of Redis?

### Redis Evaluation
**Pros:**
- Fast in-memory storage
- Simple key-value structure
- Native Python support (`redis-py`)

**Cons:**
- ❌ **Requires External Service Registration**: Upstash, Redis Cloud, or Render Redis add-on
- No relational queries (would need to serialize/deserialize entire result objects)
- No built-in admin interface
- Requires separate caching layer migration

**Verdict**: Redis requires service registration, per user requirement → Switch to Neon DB

### Neon DB Selection
**Pros:**
- ✅ **Serverless PostgreSQL** - No server management
- ✅ **Generous Free Tier** - 3 GB storage, 512 MB compute
- ✅ **Native Render Integration** - Environment variable injection
- ✅ **Relational Structure** - Proper data modeling with foreign keys
- ✅ **SQL Queries** - Rich querying for admin dashboard
- ✅ **Auto-scaling** - Scales to zero when not in use
- ✅ **Admin Interface** - Built-in SQL editor and table viewer
- ✅ **Backup/Restore** - Point-in-time recovery built-in
- ✅ **Fast Connection Pooling** - Works with SQLAlchemy/psycopg2

**Cons:**
- Requires service registration (acceptable per user: "If it does, change to Neon")
- Slightly more complex setup than in-memory dicts

**Verdict**: Ideal solution for this use case

---

## Service Registration Requirements

### Neon DB Setup (One-Time, 5 minutes)
1. **Create Free Account**: https://neon.tech/
   - Sign up with GitHub/Google/Email
   - No credit card required for free tier

2. **Create Database**:
   - Project name: `pm-tools-suite`
   - Region: `us-east-1` (or closest to Render deployment)
   - Database name: `pmtools_production`

3. **Get Connection String**:
   - Neon provides: `postgresql://user:password@host/dbname?sslmode=require`
   - Copy to Render environment variable: `DATABASE_URL`

4. **Done!** No ongoing management needed.

---

## Database Schema Design

### Table 1: `sessions`
**Purpose**: Track all analysis sessions (active, completed, partial, failed)

```sql
CREATE TABLE sessions (
    session_id VARCHAR(64) PRIMARY KEY,
    status VARCHAR(20) NOT NULL,  -- 'active', 'completed', 'partial', 'failed'
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    pdf_filename VARCHAR(255),
    pdf_path TEXT,
    config_path TEXT,
    user_email VARCHAR(255),  -- For future auth integration
    processing_time_seconds FLOAT,
    total_tokens INTEGER,
    estimated_cost_usd NUMERIC(10, 4),
    questions_answered INTEGER,
    total_questions INTEGER,
    average_confidence NUMERIC(3, 2),
    error_message TEXT
);

CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_created_at ON sessions(created_at DESC);
```

### Table 2: `analysis_results`
**Purpose**: Store complete analysis results (JSON blob for flexibility)

```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    result_data JSONB NOT NULL,  -- Full HOTDOG output (browser_output format)
    legacy_result_data JSONB,    -- Transformed legacy format
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_analysis_results_session ON analysis_results(session_id);
```

### Table 3: `accumulated_answers`
**Purpose**: Store individual answers for granular querying and admin dashboard

```sql
CREATE TABLE accumulated_answers (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    question_id VARCHAR(50) NOT NULL,
    section_id VARCHAR(50) NOT NULL,
    section_name VARCHAR(255),
    question_text TEXT NOT NULL,
    answer_text TEXT,
    pages INTEGER[],  -- PostgreSQL array for page numbers
    confidence NUMERIC(3, 2),
    footnote TEXT,
    has_answer BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_answers_session ON accumulated_answers(session_id);
CREATE INDEX idx_answers_section ON accumulated_answers(section_id);
CREATE INDEX idx_answers_has_answer ON accumulated_answers(has_answer);
```

### Table 4: `session_events`
**Purpose**: Store polling events for debugging and replay (optional, can be trimmed)

```sql
CREATE TABLE session_events (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_session ON session_events(session_id);
CREATE INDEX idx_events_created_at ON session_events(created_at DESC);

-- Auto-cleanup old events (keep last 7 days)
CREATE OR REPLACE FUNCTION cleanup_old_events()
RETURNS void AS $$
BEGIN
    DELETE FROM session_events WHERE created_at < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;
```

---

## Migration Steps

### Phase 1: Immediate Fixes (Today - 30 minutes)

**1.1 Fix Frontend Button States** ✅
- File: `analyzer_rebuild.html` line 654
- Add button state updates after `displayResults()`
- Prevents user from clicking Stop/Export when analysis already complete

**1.2 Disable Worker Restarts (Temporary)** ✅
- File: `gunicorn_config.py` line 20
- Change: `max_requests = 0`  (was 1000)
- Prevents dict clearing until DB migration complete

**1.3 Fix Stop Button Logic** ✅
- Verify stop button checks all session dicts
- Ensure proper error handling

### Phase 2: Neon DB Setup (This Week - 1 hour)

**2.1 Create Neon DB Account & Project**
- Sign up at https://neon.tech/
- Create project: `pm-tools-suite`
- Create database: `pmtools_production`
- Copy connection string

**2.2 Add to Render Environment**
```bash
# Render Dashboard → Environment Variables
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
```

**2.3 Install Dependencies**
```bash
# requirements.txt
psycopg2-binary==2.9.9  # PostgreSQL adapter
SQLAlchemy==2.0.23      # ORM (optional but recommended)
```

**2.4 Create Database Schema**
```python
# migrations/init_db.py
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Execute schema SQL from above
cur.execute(open('migrations/schema.sql').read())
conn.commit()
```

### Phase 3: Code Migration (This Week - 4 hours)

**3.1 Create Database Service Layer**
```python
# services/database.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

class SessionDatabase:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')

    def get_connection(self):
        return psycopg2.connect(self.db_url, cursor_factory=RealDictCursor)

    def create_session(self, session_id, pdf_filename, pdf_path, config_path):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sessions (session_id, status, pdf_filename, pdf_path, config_path)
                    VALUES (%s, 'active', %s, %s, %s)
                """, (session_id, pdf_filename, pdf_path, config_path))
                conn.commit()

    def update_session_status(self, session_id, status, **kwargs):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                set_clauses = ['status = %s', 'updated_at = NOW()']
                values = [status]

                if 'error_message' in kwargs:
                    set_clauses.append('error_message = %s')
                    values.append(kwargs['error_message'])

                if status == 'completed':
                    set_clauses.append('completed_at = NOW()')
                    for key in ['processing_time_seconds', 'total_tokens', 'estimated_cost_usd',
                                'questions_answered', 'total_questions', 'average_confidence']:
                        if key in kwargs:
                            set_clauses.append(f'{key} = %s')
                            values.append(kwargs[key])

                values.append(session_id)
                sql = f"UPDATE sessions SET {', '.join(set_clauses)} WHERE session_id = %s"
                cur.execute(sql, values)
                conn.commit()

    def store_analysis_result(self, session_id, result_data, legacy_result_data):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO analysis_results (session_id, result_data, legacy_result_data)
                    VALUES (%s, %s, %s)
                """, (session_id, json.dumps(result_data), json.dumps(legacy_result_data)))
                conn.commit()

    def get_session(self, session_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
                return cur.fetchone()

    def get_analysis_result(self, session_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT result_data, legacy_result_data
                    FROM analysis_results
                    WHERE session_id = %s
                """, (session_id,))
                row = cur.fetchone()
                if row:
                    return {
                        'result': row['result_data'],
                        'legacy_result': row['legacy_result_data']
                    }
                return None

    def get_all_sessions(self, status=None, limit=100):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                if status:
                    cur.execute("""
                        SELECT * FROM sessions
                        WHERE status = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (status, limit))
                else:
                    cur.execute("""
                        SELECT * FROM sessions
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (limit,))
                return cur.fetchall()

    def store_answers(self, session_id, answers_dict):
        """Store individual answers for granular querying"""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                for question_id, answer in answers_dict.items():
                    cur.execute("""
                        INSERT INTO accumulated_answers
                        (session_id, question_id, section_id, section_name, question_text,
                         answer_text, pages, confidence, footnote, has_answer)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        session_id,
                        question_id,
                        answer.get('section_id', ''),
                        answer.get('section_name', ''),
                        answer.get('question_text', ''),
                        answer.get('answer_text'),
                        answer.get('pages', []),
                        answer.get('confidence'),
                        answer.get('footnote'),
                        answer.get('has_answer', False)
                    ))
                conn.commit()
```

**3.2 Update app.py to Use Database**
```python
# app.py (changes)
from services.database import SessionDatabase

# Initialize database (replaces in-memory dicts)
db = SessionDatabase()

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    # ... existing code ...

    # Create session in DB
    db.create_session(session_id, file.filename, pdf_path, config_path)

    def run_analysis():
        try:
            # ... existing code ...

            # On completion: store in database instead of dict
            db.update_session_status(
                session_id,
                'completed',
                processing_time_seconds=result.processing_time_seconds,
                total_tokens=result.total_tokens,
                estimated_cost_usd=float(result.estimated_cost),
                questions_answered=result.questions_answered,
                total_questions=parsed_config.total_questions,
                average_confidence=float(result.average_confidence)
            )

            db.store_analysis_result(session_id, browser_output, legacy_result)

            # Optionally store individual answers for admin dashboard
            # db.store_answers(session_id, orchestrator.layer4_accumulator.get_accumulated_answers())

        except Exception as e:
            db.update_session_status(session_id, 'failed', error_message=str(e))

@app.route('/api/results/<session_id>', methods=['GET'])
def get_results(session_id):
    # Check database instead of dicts
    session = db.get_session(session_id)
    if not session:
        return jsonify({'success': False, 'error': 'Session not found'}), 404

    result_data = db.get_analysis_result(session_id)
    if not result_data:
        return jsonify({'success': False, 'error': 'Results not found'}), 404

    return jsonify({
        'success': True,
        'result': result_data['legacy_result'],
        'statistics': {
            'processing_time': session['processing_time_seconds'],
            'total_tokens': session['total_tokens'],
            'estimated_cost': f"${session['estimated_cost_usd']:.4f}",
            'questions_answered': session['questions_answered'],
            'total_questions': session['total_questions'],
            'average_confidence': f"{session['average_confidence']:.0%}"
        }
    })
```

**3.3 Backwards Compatibility Layer**
```python
# Keep in-memory dicts for active sessions only (short-lived)
# Use DB for completed/partial/failed (persistent)

active_analyses = {}  # Still in-memory (transient, cleared on restart is OK)

# All completed/partial/failed go to DB immediately
```

### Phase 4: Admin Dashboard (This Week - 3 hours)

**4.1 Create Admin Routes**
```python
# app.py
@app.route('/api/admin/analyses', methods=['GET'])
def get_all_analyses():
    """Admin endpoint: Get all analyses with pagination"""
    status = request.args.get('status')  # 'completed', 'partial', 'failed', or None for all
    limit = int(request.args.get('limit', 100))
    offset = int(request.args.get('offset', 0))

    sessions = db.get_all_sessions(status=status, limit=limit, offset=offset)

    return jsonify({
        'success': True,
        'sessions': sessions,
        'total': len(sessions)
    })

@app.route('/api/admin/analysis/<session_id>', methods=['GET'])
def get_analysis_detail(session_id):
    """Admin endpoint: Get detailed analysis with full results"""
    session = db.get_session(session_id)
    if not session:
        return jsonify({'success': False, 'error': 'Session not found'}), 404

    result_data = db.get_analysis_result(session_id)

    return jsonify({
        'success': True,
        'session': session,
        'result': result_data['result'] if result_data else None
    })
```

**4.2 Build Admin Frontend**
```html
<!-- admin_sessions.html - Enhanced Version -->
<script>
async function loadAnalyses(status = null) {
    const url = status
        ? `/api/admin/analyses?status=${status}`
        : '/api/admin/analyses';

    const resp = await fetch(url);
    const data = await resp.json();

    displayAnalysesTable(data.sessions);
}

async function viewAnalysis(sessionId) {
    const resp = await fetch(`/api/admin/analysis/${sessionId}`);
    const data = await resp.json();

    // Display full analysis results in modal
    showAnalysisModal(data);
}

function displayAnalysesTable(sessions) {
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Session ID</th>
                    <th>Created</th>
                    <th>Status</th>
                    <th>PDF File</th>
                    <th>Questions Answered</th>
                    <th>Processing Time</th>
                    <th>Cost</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    sessions.forEach(s => {
        html += `
            <tr>
                <td>${s.session_id}</td>
                <td>${new Date(s.created_at).toLocaleString()}</td>
                <td><span class="status-${s.status}">${s.status}</span></td>
                <td>${s.pdf_filename || 'N/A'}</td>
                <td>${s.questions_answered || 'N/A'}/${s.total_questions || 'N/A'}</td>
                <td>${s.processing_time_seconds?.toFixed(2) || 'N/A'}s</td>
                <td>$${s.estimated_cost_usd?.toFixed(4) || 'N/A'}</td>
                <td>
                    <button onclick="viewAnalysis('${s.session_id}')">View</button>
                    <button onclick="exportAnalysis('${s.session_id}')">Export</button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    document.getElementById('analysesTable').innerHTML = html;
}
</script>
```

---

## Testing Plan

### Unit Tests
```python
# tests/test_database.py
import pytest
from services.database import SessionDatabase

@pytest.fixture
def db():
    return SessionDatabase()

def test_create_session(db):
    session_id = "test_session_123"
    db.create_session(session_id, "test.pdf", "/tmp/test.pdf", "/config/test.json")

    session = db.get_session(session_id)
    assert session['session_id'] == session_id
    assert session['status'] == 'active'

def test_store_and_retrieve_result(db):
    session_id = "test_session_456"
    result_data = {"sections": []}
    legacy_data = {"sections": []}

    db.create_session(session_id, "test.pdf", "/tmp/test.pdf", "/config/test.json")
    db.store_analysis_result(session_id, result_data, legacy_data)

    retrieved = db.get_analysis_result(session_id)
    assert retrieved is not None
    assert retrieved['result'] == result_data
```

### Integration Tests
1. Run full analysis → Verify DB storage
2. Restart Gunicorn worker → Verify data persists
3. Fetch results from DB → Verify correct format
4. Admin dashboard → Verify all sessions visible

---

## Rollback Plan

If migration fails, rollback steps:

1. **Revert code changes**: `git revert <migration-commit>`
2. **Re-enable in-memory dicts**: Remove DB service layer
3. **Set `max_requests = 0`**: Keep workers alive
4. **Monitor**: Watch for memory leaks

---

## Performance Considerations

### Database Connection Pooling
```python
# services/database.py
from psycopg2 import pool

class SessionDatabase:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            cls._pool = pool.SimpleConnectionPool(
                1, 20,  # min=1, max=20 connections
                os.getenv('DATABASE_URL')
            )
        return cls._pool

    def get_connection(self):
        return self.get_pool().getconn()
```

### Query Optimization
- Index on `session_id`, `status`, `created_at`
- JSONB indexing for frequent queries
- Limit result sets (pagination)

### Expected Performance
- DB query latency: 5-20ms (Neon serverless)
- In-memory dict latency: <1ms
- **Acceptable tradeoff** for persistence guarantee

---

## Cost Analysis

### Neon DB Free Tier
- **Storage**: 3 GB (sufficient for ~10,000 analyses)
- **Compute**: 0.5 GB RAM (auto-scales to zero when idle)
- **Cost**: $0/month

### Estimated Growth
- Average analysis result: 300 KB (JSON)
- 1000 analyses/month = 300 MB/month
- **Runway**: 10 months before hitting free tier limit

### Paid Tier (If Needed)
- $19/month for 10 GB storage + 1 GB compute
- Still significantly cheaper than worker restart issues

---

## Success Criteria

✅ **No 404 errors on results fetch**
✅ **Results persist across worker restarts**
✅ **Admin dashboard shows all historical analyses**
✅ **Export functionality works 100% of time**
✅ **No performance degradation (<50ms added latency)**
✅ **Database auto-cleanup prevents storage bloat**

---

## Timeline Summary

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Immediate Fixes | 30 min | Button states fixed, worker restarts disabled |
| Phase 2: Neon DB Setup | 1 hour | Database provisioned, schema created |
| Phase 3: Code Migration | 4 hours | Database service layer, app.py integration |
| Phase 4: Admin Dashboard | 3 hours | Full admin UI with historical analysis viewing |
| Testing & Deployment | 2 hours | Tests passing, deployed to production |
| **TOTAL** | **~1 day** | Persistent storage fully operational |

---

## Next Steps (Immediate Action Items)

1. ✅ Fix frontend button states (analyzer_rebuild.html line 654)
2. ✅ Fix stop button logic (verify all dict checks)
3. ✅ Disable worker restarts (gunicorn_config.py line 20)
4. ⏳ Create Neon DB account and database
5. ⏳ Implement database service layer
6. ⏳ Migrate app.py to use database
7. ⏳ Build out admin dashboard
8. ⏳ Deploy and test

---

**Document Owner**: PM Tools Suite Development Team
**Last Updated**: 2024-12-24
**Review Date**: After Phase 3 completion
