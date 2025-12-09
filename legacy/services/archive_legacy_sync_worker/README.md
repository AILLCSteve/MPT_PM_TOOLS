# Legacy Sync Worker Implementation Archive

**Archived Date:** 2025-12-01
**Reason:** Fundamental architectural incompatibility with SSE streaming

## What's Here

This directory contains the **non-functional** implementation that used Gunicorn sync workers:

- `app.py` - Flask backend with SSE endpoints (sync worker version)
- `gunicorn_config.py` - Sync worker configuration (workers=1, worker_class='sync')
- `cipp_analyzer_branded.html` - Frontend with accumulated debug logging attempts

## Why It Failed

**Root Cause:** Sync workers + blocking `asyncio.run_until_complete()` = frozen worker thread

### Timeline of Failure:
1. SSE connection opens → generator yields "connected" → waits on `queue.get()`
2. Analysis POST arrives → **BLOCKS ENTIRE WORKER** running 10+ minute orchestrator
3. Progress events successfully queue in memory
4. **SSE generator cannot run to dequeue/send events** (worker thread is blocked!)
5. Analysis completes → worker unblocks → SSE connection already timed out

### The Architectural Mismatch:
- **HOTDOG Architecture:** Multi-agent parallel processing, long-running AI calls, real-time streaming
- **Sync Workers:** Sequential request handling, blocking I/O, no concurrency within worker
- **Result:** Events queue but never get sent; frontend shows only initial connection message

## Issues Encountered During Debugging

1. ✅ **SOLVED:** `NameError: AnswerAccumulation not defined` - Missing import in orchestrator.py
2. ✅ **SOLVED:** Event name mismatches - Backend sent `layer_0_complete`, frontend expected `document_ingested`
3. ✅ **SOLVED:** Multi-worker queue isolation - Reduced from 2 workers to 1 worker
4. ❌ **UNSOLVABLE WITH SYNC WORKERS:** SSE generator frozen during blocking analysis

## What Was Learned

- Sync workers are fundamentally incompatible with SSE streaming during long-running operations
- In-memory queues don't work across multiple worker **processes** (separate memory spaces)
- `asyncio.run_until_complete()` blocks the entire sync worker thread, preventing concurrent operations
- **Async workers (gevent/eventlet) were the correct choice from day 1** for this architecture

## Replacement Implementation

See root directory for new implementation using:
- **Gevent async workers** - Cooperative multitasking within single worker
- **Simplified SSE streaming** - Clean implementation without accumulated debug code
- **Proper concurrent handling** - SSE generator can yield while analysis runs

---

**Do not use this code.** It is kept only as reference for design workflows and to understand what not to do.
