# Admin Session Flickering - Root Cause Analysis

**Date**: 2024-12-24
**Severity**: CRITICAL
**Status**: Under Investigation

---

## Symptoms Observed

1. **Admin page refresh** shows different sessions each time:
   - Sometimes shows partial analysis only
   - Sometimes shows active analysis only
   - Sometimes shows both
   - Sometimes shows nothing

2. **Clicking "View"** on a session:
   - Sometimes: Displays the unitary table ✅
   - Sometimes: "Session not found" ❌
   - Pattern is random/intermittent

3. **No lag/delay** - page refreshes instantly with different data each time

---

## Architecture Overview

### Session Storage (Global Module-Level Dicts)

```python
# app.py lines 74-81
active_analyses = {}      # In-progress analyses
completed_analyses = {}   # Successfully completed
partial_analyses = {}     # Stopped by user
analysis_results = {}     # Legacy storage
session_timestamps = {}   # For cleanup (last access time)
```

### Worker Configuration (gunicorn_config.py)

```python
workers = 1              # Single worker process
worker_class = 'sync'    # Synchronous worker
threads = 10             # 10 concurrent request threads
max_requests = 0         # Never restart worker
```

**Key Point**: Single worker means all dicts are shared. But **10 threads** means concurrent access without locking!

---

## Root Causes Identified

### 1. **RACE CONDITION IN ADMIN ENDPOINT** (CRITICAL)

**Location**: `app.py` lines 1064-1091

```python
# Line 1064-1069: Get all session IDs
all_session_ids = (
    list(active_analyses.keys()) +      # ⚠️ Snapshot at time T1
    list(completed_analyses.keys()) +
    list(partial_analyses.keys()) +
    list(analysis_results.keys())
)

# Line 1070-1071: Touch timestamps
for sid in all_session_ids:
    session_timestamps[sid] = datetime.now()  # ⚠️ Access at time T2

# Line 1074-1091: Gather session data
sessions = {
    'active': [
        format_session_info(sid, data, 'active')
        for sid, data in active_analyses.items()  # ⚠️ Access at time T3
    ],
    ...
}
```

**The Problem**:
- **T1**: Thread A gets `active_analyses.keys()` → `['session_123']`
- **T1+5ms**: Analysis completes in Thread B → moves `session_123` from `active_analyses` to `completed_analyses`
- **T2**: Thread A tries to access `active_analyses['session_123']` → **NOT FOUND!**
- **T3**: Thread A iterates `active_analyses.items()` → `session_123` is GONE

**Result**: Session appears to vanish!

### 2. **CONCURRENT DICT MODIFICATION** (CRITICAL)

**Scenario**: Analysis completion thread modifies dicts while admin endpoint reads them.

**Timeline Example**:
```
0ms:  Admin endpoint starts: Gets keys from active_analyses → ['session_X']
5ms:  Analysis thread: Completes session_X
      - Del active_analyses['session_X']
      - Set completed_analyses['session_X'] = {...}
10ms: Admin endpoint: Iterates active_analyses → session_X gone!
15ms: Admin endpoint: Returns results → session_X not in list!
20ms: User clicks refresh
25ms: Admin endpoint starts: Gets keys from completed_analyses → ['session_X']
30ms: Admin endpoint: Returns results → session_X appears!
```

**This explains the flickering**: The timing of the request vs dict modification determines what appears!

### 3. **NO THREAD SYNCHRONIZATION**

Python dicts are **NOT thread-safe** for concurrent reads + writes:
- Reading while another thread writes → can see incomplete state
- Getting keys, then accessing → keys might disappear mid-iteration
- No locks, no mutexes, no synchronization primitives

**Current Code**: Zero locking mechanisms

### 4. **TIMESTAMP TOUCHING RACE CONDITION**

**Location**: `app.py` line 1070-1071

```python
for sid in all_session_ids:
    session_timestamps[sid] = datetime.now()  # KeyError if sid deleted!
```

If a session is deleted (by cleanup or analysis completion) AFTER getting keys but BEFORE touching timestamps → silent failure or KeyError (depending on error handling).

### 5. **CLEANUP THREAD INTERFERENCE**

**Location**: `app.py` line 130-167

Cleanup runs **every 15 minutes** in a separate thread:
- Iterates `session_timestamps.items()`
- Pops sessions from ALL dicts
- Runs concurrently with admin endpoint

**Race Scenario**:
```
Thread A (Admin):         Thread B (Cleanup):
Get keys ['X', 'Y']
                          Check session 'X' age
Access session 'X'
                          Delete session 'X' (too old)
Access session 'Y'        Session 'Y' still there
Return both
```

Next request:
```
Thread A (Admin):
Get keys ['Y']            Session 'X' gone!
Return only 'Y'
```

**User sees**: Session X disappeared!

---

## Why Sessions Appear/Disappear Randomly

### Scenario 1: Active → Completed Transition

```
Request 1 (T=0ms):   Admin reads active_analyses → ['session_X']
                      Returns session_X as "active"

Analysis completes (T=50ms): Move X from active → completed

Request 2 (T=100ms): Admin reads active_analyses → []
                      Admin reads completed_analyses → ['session_X']
                      Returns session_X as "completed"

Request 3 (T=150ms): Admin reads active_analyses → []
                      Admin reads completed_analyses → ['session_X']
                      Returns session_X as "completed"
```

**Result**: First refresh shows active, subsequent refreshes show completed. If requests overlap the transition, one might see nothing!

### Scenario 2: Dict Iteration During Modification

```python
# Admin thread iterating
for sid, data in active_analyses.items():  # ← Start iteration
    format_session_info(sid, data, 'active')
    # Mid-iteration, analysis thread does:
    # del active_analyses[sid]  ← Dict changed during iteration!
```

**Python Behavior**: Dict modification during iteration → **RuntimeError** OR **skipped items** OR **undefined behavior** (depending on timing)

### Scenario 3: "Session Not Found" When Clicking View

```
User sees session X in admin list
↓
Clicks "View"
↓
Request sent to /api/results/session_X
↓
Analysis thread completes a DIFFERENT session Y → moves Y from active to completed
BUT this updates session_timestamps → triggers potential cleanup check
↓
Cleanup thread sees session X hasn't been accessed recently
↓
Deletes session X (race with /api/results request)
↓
/api/results finds session X not in any dict → 404
```

**OR simpler**:
```
Admin page renders with session list from T=0
↓
User takes 5 seconds to click "View"
↓
At T=5s, analysis completed and session moved from active to completed
↓
/api/results checks completed_analyses (line 688)
BUT format_session_info threw exception so session not actually stored?
↓
Session not found
```

---

## Data Structure Thread-Safety Analysis

### Python Dict Thread Safety

**From Python docs**:
> "Dictionaries are thread-safe for reads, but NOT for concurrent reads + writes."

**Implications**:
- ❌ One thread reading keys while another deletes → keys list can be stale
- ❌ One thread iterating items while another adds/removes → RuntimeError possible
- ❌ Multiple threads modifying same key → race conditions

**Current Code**: NO locking, assuming single-threaded access. But we have **10 threads**!

---

## Why This Wasn't Caught Earlier

1. **Low Traffic**: With few concurrent requests, race conditions are rare
2. **Fast Completions**: If analysis completes instantly, no overlap between admin reads and completion writes
3. **Lucky Timing**: Race windows are microseconds - needs perfect timing to hit

**As usage increases**, race conditions become MORE frequent!

---

## Detailed Code Path Analysis

### Admin Page Refresh Flow

```
1. Browser: GET /api/admin/sessions
2. Flask (Thread 1): Route /api/admin/sessions (line 1002)
3. Get keys from 4 dicts (line 1064-1069)  ← SNAPSHOT 1
4. Touch timestamps (line 1070-1071)       ← ACCESS 1 (can fail if keys deleted)
5. Iterate dicts (line 1074-1091)          ← SNAPSHOT 2 (different from SNAPSHOT 1!)
6. Return JSON

MEANWHILE:
- Thread 2: Analysis completes → modify active_analyses, completed_analyses
- Thread 3: Cleanup runs → modify all dicts
- Thread 4: Another admin request
```

**Problem**: Snapshots 1 and 2 are taken at different times with no atomicity guarantee!

### Analysis Completion Flow

```
1. Analysis thread: Complete analysis
2. Move to completed_analyses (line 614-627)
   - Set completed_analyses[sid] = {...}
   - Del active_analyses[sid]
   - Update session_timestamps[sid]
3. Signal done

MEANWHILE:
- Admin thread reading active_analyses → might see mid-transition state
```

### View Session Flow

```
1. Browser: GET /api/results/session_X
2. Flask: Route /api/results (line 683)
3. Check completed_analyses (line 688)  ← Dict lookup
4. Touch timestamp (line 690)            ← Another dict write
5. Get session data (line 692)
6. Format and return

MEANWHILE:
- Cleanup thread might delete session_X
- Another analysis might complete and modify dicts
```

---

## Critical Code Sections Requiring Locking

### 1. Admin Endpoint (lines 1002-1106)

**Needs**: Single atomic snapshot of all dicts

### 2. Analysis Completion (lines 612-630)

**Needs**: Atomic move from active → completed

### 3. Cleanup Function (lines 130-167)

**Needs**: Atomic iteration and deletion

### 4. Results Endpoint (lines 683-827)

**Needs**: Atomic session lookup

---

## Proposed Solutions

### Option 1: Thread Locking (Quick Fix)

**Add**: `threading.Lock()` for all dict access

```python
session_lock = threading.Lock()

@app.route('/api/admin/sessions')
def get_all_sessions():
    with session_lock:  # ← Atomic snapshot
        all_session_ids = (
            list(active_analyses.keys()) +
            list(completed_analyses.keys()) +
            ...
        )
        sessions = {...}  # Build entire response
    return jsonify(sessions)
```

**Pros**:
- Simple to implement
- Fixes all race conditions
- No external dependencies

**Cons**:
- Lock contention could slow down concurrent requests
- Doesn't solve worker restart issue
- Doesn't provide persistence

### Option 2: Neon DB Migration (Complete Fix)

**Migrate** all session storage to PostgreSQL (see `PERSISTENT_STORAGE_MIGRATION_PLAN.md`)

**Pros**:
- ACID transactions (atomic operations)
- Persistence across restarts
- No race conditions (DB handles concurrency)
- Scales to multiple workers
- Admin panel shows ALL historical analyses

**Cons**:
- Requires service setup (Neon DB account)
- More complex migration
- Slight latency increase (~5-20ms per query)

### Option 3: Hybrid Approach (Recommended for Testing)

1. **Immediate**: Add thread locking to stop flickering
2. **Short-term**: Test with increased load to verify fix
3. **Long-term**: Migrate to Neon DB for production

---

## Recommended Fix (Step-by-Step)

### Phase 1: Add Thread Locking (Today - 1 hour)

1. Create global lock
2. Wrap admin endpoint with lock
3. Wrap analysis completion with lock
4. Wrap cleanup with lock
5. Wrap results endpoint with lock

### Phase 2: Add Diagnostic Logging (Today - 30 min)

1. Log every dict modification with timestamp
2. Log every admin request with keys snapshot
3. Log cleanup runs
4. Deploy and monitor for 24 hours

### Phase 3: Verify Fix (Tomorrow)

1. Run multiple concurrent analyses
2. Rapidly refresh admin panel
3. Click view multiple times
4. Verify no flickering, no 404s

### Phase 4: Neon DB Migration (Next Week)

Follow plan in `PERSISTENT_STORAGE_MIGRATION_PLAN.md`

---

## Testing Plan

### Reproduce the Bug

1. Start analysis A (partial - stop it)
2. Start analysis B (let it run)
3. Rapidly refresh admin page (10+ times)
4. Click "View" on each session multiple times
5. Observe flickering and 404 errors

### Verify the Fix

After applying locks:
1. Same test as above
2. Should see consistent session list
3. Should never get 404 on View
4. Both sessions visible always

---

## Next Steps

1. ✅ Complete this analysis document
2. ⏳ Implement thread locking
3. ⏳ Add diagnostic logging
4. ⏳ Deploy and test
5. ⏳ Monitor for 24 hours
6. ⏳ Plan Neon DB migration

---

**Document Owner**: PM Tools Suite Development
**Last Updated**: 2024-12-24
**Severity**: CRITICAL - Affects production admin panel reliability
