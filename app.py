"""
PM Tools Suite - Clean Rebuild
HOTDOG AI Document Analysis with Real-Time SSE Progress

Architecture: Threading-based (simple, proven, works)
"""
# CRITICAL: Gevent monkey patching MUST be first (before any other imports)
# This makes socket/queue work with gevent workers
# thread=False prevents conflicts with threading.Thread in analysis
try:
    from gevent import monkey
    monkey.patch_all(thread=False, select=False)
    GEVENT_PATCHED = True
except ImportError:
    # Gevent not installed (development mode) - continue without patching
    GEVENT_PATCHED = False

import os
import sys
import logging
import threading
import queue
import json
import tempfile
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # CRITICAL: Must be called before any os.getenv() usage

from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import HOTDOG orchestrator
from services.hotdog import HotdogOrchestrator
# Excel dashboard import moved to lazy load (only when endpoint is called)
# This prevents app crash if openpyxl isn't installed
import asyncio

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Diagnostic: Log Python and gevent environment
logger.info(f"🐍 Python {sys.version.split()[0]} at {sys.executable}")
if GEVENT_PATCHED:
    try:
        import gevent
        logger.info(f"✅ gevent {gevent.__version__} installed and patched (thread=False)")
    except:
        logger.warning(f"⚠️ Gevent patch attempted but module import failed")
else:
    logger.warning(f"⚠️ gevent NOT installed - SSE will not work with sync workers!")

# Configuration
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    BASE_DIR = Path(__file__).parent

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Global state
progress_queues = {}  # session_id -> Queue for SSE progress (legacy)
session_events = {}  # session_id -> [events] for polling (NEW)
analysis_threads = {}  # session_id -> Thread for cancellation
analysis_results = {}  # session_id -> result data (legacy, kept for backward compatibility)
active_analyses = {}  # session_id -> {'orchestrator': HotdogOrchestrator, 'config_path': str, 'pdf_path': str, 'status': 'running'} (in-progress)
completed_analyses = {}  # session_id -> {'orchestrator': ..., 'result': ..., 'config_path': ..., 'completed_at': datetime, 'status': 'completed'}
partial_analyses = {}  # session_id -> {'orchestrator': ..., 'config_path': ..., 'stopped_at': datetime, 'status': 'stopped'}
session_timestamps = {}  # session_id -> last_access_time (for cleanup)

# Authentication - Load from environment variables
def load_authorized_users():
    """Load authorized users from environment variables for security."""
    users = {}

    # User 1
    user1_email = os.getenv('AUTH_USER1_EMAIL')
    user1_password = os.getenv('AUTH_USER1_PASSWORD')
    user1_name = os.getenv('AUTH_USER1_NAME', 'User 1')

    if user1_email and user1_password:
        users[user1_email.lower()] = {  # Lowercase for case-insensitive matching
            'password_hash': hashlib.sha256(user1_password.encode()).hexdigest(),
            'name': user1_name
        }

    # User 2
    user2_email = os.getenv('AUTH_USER2_EMAIL')
    user2_password = os.getenv('AUTH_USER2_PASSWORD')
    user2_name = os.getenv('AUTH_USER2_NAME', 'User 2')

    if user2_email and user2_password:
        users[user2_email.lower()] = {  # Lowercase for case-insensitive matching
            'password_hash': hashlib.sha256(user2_password.encode()).hexdigest(),
            'name': user2_name
        }

    if not users:
        print("WARNING: No authorized users configured. Set AUTH_USER*_EMAIL and AUTH_USER*_PASSWORD environment variables.")

    return users

AUTHORIZED_USERS = load_authorized_users()
active_sessions = {}

# Log loaded users on startup
logger.info("="*60)
logger.info("AUTHORIZED USERS LOADED:")
for email, data in AUTHORIZED_USERS.items():
    logger.info(f"  User: {email} | Name: {data.get('name', 'N/A')}")
logger.info("="*60)


# ============================================================================
# SESSION CLEANUP (Memory Management)
# ============================================================================

def cleanup_expired_sessions():
    """
    Remove sessions older than 1 hour to prevent memory exhaustion.
    Reschedules itself every 15 minutes using threading.Timer.
    """
    try:
        cutoff = datetime.now() - timedelta(hours=1)
        expired = [
            sid for sid, ts in session_timestamps.items()
            if ts < cutoff
        ]

        for sid in expired:
            progress_queues.pop(sid, None)
            session_events.pop(sid, None)
            analysis_threads.pop(sid, None)
            analysis_results.pop(sid, None)
            active_analyses.pop(sid, None)
            completed_analyses.pop(sid, None)  # NEW: Clean up completed
            partial_analyses.pop(sid, None)  # NEW: Clean up partial
            session_timestamps.pop(sid, None)
            logger.info(f"✅ Cleaned up expired session: {sid}")

        if expired:
            logger.info(f"🧹 Cleaned up {len(expired)} expired sessions")

    except Exception as e:
        logger.error(f"❌ Session cleanup failed: {e}")

    # Reschedule cleanup in 15 minutes (900 seconds)
    timer = threading.Timer(900, cleanup_expired_sessions)
    timer.daemon = True
    timer.start()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _transform_to_legacy_format(hotdog_output: dict) -> dict:
    """
    Transform HOTDOG's modern output format to legacy frontend format.

    This backwards-compatibility layer ensures the old frontend can display
    HOTDOG's results without requiring a complete frontend rewrite.

    HOTDOG Format:
        {
            "sections": [{
                "questions": [{
                    "question_text": "...",
                    "primary_answer": {"text": "...", "pages": [1,2,3]}
                }]
            }]
        }

    Legacy Format:
        {
            "sections": [{
                "questions": [{
                    "question": "...",
                    "answer": "...",
                    "page_citations": [1,2,3]
                }]
            }]
        }
    """
    legacy_sections = []

    for section in hotdog_output.get('sections', []):
        legacy_section = {
            'section_name': section.get('section_name', ''),
            'section_id': section.get('section_id', ''),
            'description': section.get('description', ''),
            'questions': []
        }

        for q in section.get('questions', []):
            legacy_question = {
                'question_id': q.get('question_id', ''),
                'question': q.get('question_text', ''),  # Transform: question_text → question
            }

            # Transform: primary_answer{text, pages, footnote} → answer, page_citations, footnote
            primary_answer = q.get('primary_answer')
            # Check if answer exists: either has_answer=True OR primary_answer is not None
            has_answer = q.get('has_answer', primary_answer is not None)
            if primary_answer and has_answer:
                legacy_question['answer'] = primary_answer.get('text', '')
                legacy_question['page_citations'] = primary_answer.get('pages', [])
                legacy_question['confidence'] = primary_answer.get('confidence', 0.0)
                legacy_question['footnote'] = primary_answer.get('footnote', '')  # Include footnote
            else:
                legacy_question['answer'] = None
                legacy_question['page_citations'] = []
                legacy_question['confidence'] = 0.0
                legacy_question['footnote'] = None

            legacy_section['questions'].append(legacy_question)

        legacy_sections.append(legacy_section)

    return {
        'sections': legacy_sections,
        'document_name': hotdog_output.get('document_name', ''),
        'total_pages': hotdog_output.get('total_pages', 0),
        'questions_answered': hotdog_output.get('questions_answered', 0),
        'total_questions': hotdog_output.get('total_questions', 0),
        'metadata': hotdog_output.get('metadata', {})
    }


# ============================================================================
# BASIC ROUTES
# ============================================================================

@app.route('/')
def index():
    return send_from_directory(Config.BASE_DIR, 'index.html')

@app.route('/shared/<path:filename>')
def serve_shared_assets(filename):
    """Serve shared assets (images, CSS, etc.)"""
    return send_from_directory(Config.BASE_DIR / 'shared', filename)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'PM Tools Suite',
        'version': '2.0.0-clean'
    })


# ============================================================================
# AUTHENTICATION
# ============================================================================

@app.route('/api/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')

    # Simple debug logging
    user_agent = request.headers.get('User-Agent', 'Unknown')
    logger.info(f"Auth attempt - Username (raw): '{data.get('username', '')}' length={len(data.get('username', ''))}")
    logger.info(f"Auth attempt - Username (normalized): '{username}' length={len(username)}")
    logger.info(f"Auth attempt - Password length: {len(password)}")
    logger.info(f"Auth attempt - User agent: {user_agent[:50]}")
    logger.info(f"Loaded users in dict: {list(AUTHORIZED_USERS.keys())}")

    if username not in AUTHORIZED_USERS:
        logger.warning(f"User not found: {username}")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    expected_hash = AUTHORIZED_USERS[username]['password_hash']

    if password_hash != expected_hash:
        logger.warning(f"Password mismatch for {username}")
        logger.warning(f"  Received hash: {password_hash[:20]}...")
        logger.warning(f"  Expected hash: {expected_hash[:20]}...")
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)

    active_sessions[token] = {
        'username': username,
        'name': AUTHORIZED_USERS[username]['name'],
        'expires_at': expires_at
    }

    return jsonify({
        'success': True,
        'token': token,
        'user': {'email': username, 'name': AUTHORIZED_USERS[username]['name']}
    })

@app.route('/api/verify-session', methods=['POST'])
def verify_session():
    data = request.get_json()
    token = data.get('token', '')

    if token not in active_sessions:
        return jsonify({'valid': False}), 401

    session = active_sessions[token]
    if datetime.now() > session['expires_at']:
        del active_sessions[token]
        return jsonify({'valid': False}), 401

    return jsonify({'valid': True, 'user': {'email': session['username'], 'name': session['name']}})


# ============================================================================
# API KEY
# ============================================================================

@app.route('/api/config/apikey', methods=['GET'])
def get_api_key():
    api_key = os.getenv('OPENAI_API_KEY', '')
    if not api_key:
        return jsonify({'success': False, 'error': 'API key not configured'}), 500

    return jsonify({
        'success': True,
        'key': api_key,
        'masked': api_key[:10] + '...' + api_key[-4:]
    })


@app.route('/api/health/sse', methods=['GET'])
def sse_health():
    """Diagnostic endpoint for SSE environment status"""
    import platform

    # Check gevent installation and version
    try:
        import gevent
        gevent_version = gevent.__version__
        gevent_installed = True
    except ImportError:
        gevent_version = None
        gevent_installed = False

    # Check gunicorn worker availability
    try:
        from gunicorn.workers.ggevent import GeventWorker
        gevent_worker_available = True
    except ImportError:
        gevent_worker_available = False

    return jsonify({
        'python_version': platform.python_version(),
        'python_executable': sys.executable,
        'gevent_installed': gevent_installed,
        'gevent_version': gevent_version,
        'gevent_patched': GEVENT_PATCHED,
        'gevent_worker_available': gevent_worker_available,
        'server_software': os.environ.get('SERVER_SOFTWARE', 'unknown'),
        'active_sessions': len(progress_queues),
        'active_analyses': len(active_analyses)
    })


# ============================================================================
# FILE UPLOAD
# ============================================================================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload PDF file, save to temp, return filepath"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'Only PDF files supported'}), 400

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as temp_file:
        temp_path = temp_file.name
        file.save(temp_path)

    logger.info(f"File uploaded: {file.filename} -> {temp_path}")

    return jsonify({
        'success': True,
        'filepath': temp_path,
        'filename': file.filename
    })


# ============================================================================
# SSE PROGRESS STREAM (SIMPLE - Like Test That Worked!)
# ============================================================================

@app.route('/api/progress/<session_id>')
def progress_stream(session_id):
    """SSE endpoint for real-time progress updates"""

    def generate():
        import time

        # Create or get queue (atomic to prevent race condition)
        progress_queues.setdefault(session_id, queue.Queue(maxsize=1000))
        q = progress_queues[session_id]

        # DIAGNOSTIC: Log SSE connection with timestamp
        start_time = time.time()
        logger.info(f"🔵 SSE connection opened: {session_id} at {datetime.now().isoformat()}")

        # Send connection event
        yield f"data: {json.dumps({'event': 'connected', 'session_id': session_id})}\n\n"
        logger.info(f"📤 Sent 'connected' event to client: {session_id}")

        # DIAGNOSTIC: Immediate test yield (should appear instantly in browser if no buffering)
        time.sleep(0.5)
        test_timestamp = time.time()
        yield f"data: {json.dumps({'event': 'diagnostic_test', 'message': 'Immediate yield test', 'timestamp': test_timestamp})}\n\n"
        logger.info(f"📤 Sent diagnostic test event: {session_id} (delta: {test_timestamp - start_time:.2f}s)")

        # Stream events
        while True:
            try:
                # Get next event (15 second timeout for keepalive)
                event_type, data = q.get(timeout=15)
                logger.info(f"📡 SSE sending: {event_type} at {datetime.now().isoformat()}")  # Changed to INFO

                # Check for done/error signals
                if event_type == 'done':
                    logger.info(f"✅ SSE sending 'done' event: {session_id}")
                    yield f"data: {json.dumps({'event': 'done'})}\n\n"
                    break

                if event_type == 'error':
                    logger.info(f"❌ SSE sending 'error' event: {session_id}")
                    yield f"data: {json.dumps({'event': 'error', 'error': data})}\n\n"
                    break

                # Send progress event
                yield f"data: {json.dumps({'event': event_type, **data})}\n\n"

            except queue.Empty:
                # Send keepalive
                logger.info(f"💓 SSE keepalive: {session_id} at {datetime.now().isoformat()}")  # Changed to INFO
                yield ": keepalive\n\n"

        # Cleanup
        if session_id in progress_queues:
            del progress_queues[session_id]

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


# ============================================================================
# POLLING ENDPOINT (NEW - Primary Progress Method)
# ============================================================================

@app.route('/api/events/<session_id>')
def get_events(session_id):
    """Get new events since last poll (replaces SSE streaming)"""
    last_index = int(request.args.get('last_index', 0))

    # Get events for this session
    events = session_events.get(session_id, [])

    # Return only new events since last_index
    new_events = events[last_index:]

    logger.info(f"📡 Polling: session={session_id}, last_index={last_index}, new_events={len(new_events)}, total={len(events)}")

    return jsonify({
        'success': True,
        'events': new_events,
        'last_index': len(events),  # Next index to request
        'total_events': len(events)
    })


# ============================================================================
# HOTDOG ANALYSIS (NON-BLOCKING with Threading)
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Start HOTDOG AI analysis in background thread"""

    # Get request data
    data = request.json
    pdf_path = data.get('pdf_path')
    context_guardrails = data.get('context_guardrails', '')
    enabled_sections = data.get('enabled_sections', None)  # NEW: Optional list of enabled section IDs
    session_id = data.get('session_id', f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # Track session timestamp for cleanup
    session_timestamps[session_id] = datetime.now()

    # Validate
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'success': False, 'error': 'PDF file not found'}), 404

    # Get API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        return jsonify({'success': False, 'error': 'API key not configured'}), 500

    # Create progress queue for this session (atomic to prevent race condition)
    progress_queues.setdefault(session_id, queue.Queue(maxsize=1000))
    progress_q = progress_queues[session_id]

    # Create event list for polling (NEW)
    session_events.setdefault(session_id, [])

    # Define progress callback - stores events for BOTH SSE (legacy) and polling (NEW)
    def progress_callback(event_type: str, event_data: dict):
        # Store in list for polling (NEW - primary method)
        event_obj = {'event': event_type, **event_data, 'timestamp': datetime.now().isoformat()}
        session_events[session_id].append(event_obj)
        logger.info(f"📥 Event stored: {event_type} (total: {len(session_events[session_id])})")

        # Also queue for SSE (legacy compatibility)
        try:
            progress_q.put_nowait((event_type, event_data))
        except queue.Full:
            logger.warning(f"Progress queue full, dropping SSE event: {event_type}")

    # Define analysis function to run in thread
    def run_analysis():
        try:
            logger.info(f"Starting analysis in thread: {session_id}")
            if enabled_sections:
                logger.info(f"Enabled sections: {enabled_sections}")

            # Get config path
            config_path = str(Config.BASE_DIR / 'config' / 'cipp_questions_default.json')

            # Initialize orchestrator
            orchestrator = HotdogOrchestrator(
                openai_api_key=openai_key,
                config_path=config_path,
                context_guardrails=context_guardrails,
                progress_callback=progress_callback
            )

            # Store in active_analyses IMMEDIATELY (for partial results)
            active_analyses[session_id] = {
                'orchestrator': orchestrator,
                'config_path': config_path,
                'pdf_path': pdf_path
            }
            logger.info(f"Orchestrator stored in active_analyses: {session_id}")

            # Run analysis (blocking in THIS thread, not main Flask thread)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    orchestrator.analyze_document(pdf_path, config_path, enabled_sections)
                )

                # Move to completed results
                analysis_results[session_id] = {
                    'result': result,
                    'orchestrator': orchestrator,
                    'config_path': config_path
                }

                # Format result for browser and store in session_events for polling
                from services.hotdog.layers import ConfigurationLoader
                config_loader = ConfigurationLoader()
                parsed_config = config_loader.load_from_json(config_path)
                browser_output = orchestrator.get_browser_output(result, parsed_config)
                legacy_result = _transform_to_legacy_format(browser_output)

                # Store full result in session_events so frontend can access via polling
                progress_callback('results_ready', {
                    'result': legacy_result,
                    'statistics': {
                        'processing_time': result.processing_time_seconds,
                        'total_tokens': result.total_tokens,
                        'estimated_cost': f"${result.estimated_cost:.4f}",
                        'questions_answered': result.questions_answered,
                        'total_questions': parsed_config.total_questions,
                        'average_confidence': f"{result.average_confidence:.0%}"
                    }
                })

                # Move from active to completed (preserve session data)
                if session_id in active_analyses:
                    completed_analyses[session_id] = {
                        'result': result,
                        'orchestrator': orchestrator,
                        'config_path': config_path,
                        'pdf_path': pdf_path,
                        'completed_at': datetime.now(),
                        'status': 'completed'
                    }
                    del active_analyses[session_id]
                    logger.info(f"✅ Session moved to completed_analyses: {session_id}")

                # Signal done
                progress_q.put(('done', {}))

                logger.info(f"Analysis complete: {session_id}")

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            error_msg = str(e)
            progress_q.put(('error', error_msg))

            # Handle stopped vs failed analyses differently
            if 'stopped by user' in error_msg.lower():
                # Move stopped analysis to partial_analyses (preserve partial data)
                if session_id in active_analyses:
                    partial_analyses[session_id] = {
                        'orchestrator': active_analyses[session_id]['orchestrator'],
                        'config_path': active_analyses[session_id]['config_path'],
                        'pdf_path': active_analyses[session_id].get('pdf_path', ''),
                        'stopped_at': datetime.now(),
                        'status': 'stopped',
                        'error': error_msg
                    }
                    del active_analyses[session_id]
                    logger.info(f"✅ Session moved to partial_analyses: {session_id}")
            else:
                # Clean up failed analysis on actual errors
                if session_id in active_analyses:
                    del active_analyses[session_id]
                    logger.info(f"Session cleaned up due to error: {session_id}")

    # Start analysis thread
    thread = threading.Thread(target=run_analysis, daemon=True)
    analysis_threads[session_id] = thread
    thread.start()

    logger.info(f"Analysis thread started: {session_id}")

    # Return immediately (don't wait for analysis)
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Analysis started in background'
    })


# ============================================================================
# GET RESULTS
# ============================================================================

@app.route('/api/results/<session_id>', methods=['GET'])
def get_results(session_id):
    """Get analysis results (supports completed, partial, and in-progress analyses)"""

    # Check completed_analyses first (NEW - primary storage)
    if session_id in completed_analyses:
        session_data = completed_analyses[session_id]
        result = session_data['result']
        orchestrator = session_data['orchestrator']

        # Get browser-formatted output
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(session_data['config_path'])

        browser_output = orchestrator.get_browser_output(result, parsed_config)
        legacy_result = _transform_to_legacy_format(browser_output)

        return jsonify({
            'success': True,
            'result': legacy_result,
            'statistics': {
                'processing_time': result.processing_time_seconds,
                'total_tokens': result.total_tokens,
                'estimated_cost': f"${result.estimated_cost:.4f}",
                'questions_answered': result.questions_answered,
                'total_questions': parsed_config.total_questions,
                'average_confidence': f"{result.average_confidence:.0%}"
            }
        })

    # Check legacy analysis_results (LEGACY - kept for backward compatibility)
    elif session_id in analysis_results:
        session_data = analysis_results[session_id]
        result = session_data['result']
        orchestrator = session_data['orchestrator']

        # Get browser-formatted output
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(session_data['config_path'])

        browser_output = orchestrator.get_browser_output(result, parsed_config)

        # ========================================================================
        # BACKWARDS COMPATIBILITY LAYER
        # Transform HOTDOG's modern structure to legacy frontend structure
        # ========================================================================
        legacy_result = _transform_to_legacy_format(browser_output)

        return jsonify({
            'success': True,
            'result': legacy_result,
            'statistics': {
                'processing_time': result.processing_time_seconds,
                'total_tokens': result.total_tokens,
                'estimated_cost': f"${result.estimated_cost:.4f}",
                'questions_answered': result.questions_answered,
                'total_questions': parsed_config.total_questions,
                'average_confidence': f"{result.average_confidence:.0%}"
            }
        })

    # Check partial_analyses (stopped by user)
    elif session_id in partial_analyses:
        logger.info(f"Fetching results for partial analysis: {session_id}")
        session_data = partial_analyses[session_id]
        orchestrator = session_data['orchestrator']
        config_path = session_data['config_path']

        # Get accumulated answers so far
        accumulated_answers = orchestrator.layer4_accumulator.get_accumulated_answers()

        # Load config
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(config_path)

        # Build partial browser output
        partial_browser_output = orchestrator._build_partial_browser_output(
            accumulated_answers,
            parsed_config
        )

        # Transform to legacy format
        legacy_result = _transform_to_legacy_format(partial_browser_output)

        return jsonify({
            'success': True,
            'result': legacy_result,
            'partial': True,  # Flag indicating partial results
            'statistics': {
                'processing_time': 0,  # Not yet available
                'total_tokens': orchestrator.layer5_token_manager.total_tokens_used,
                'estimated_cost': 'Stopped',
                'questions_answered': len([a for answers in accumulated_answers.values() for a in answers]),
                'total_questions': parsed_config.total_questions,
                'average_confidence': 'Partial'
            }
        })

    # Check if analysis is active (in-progress - return partial results)
    elif session_id in active_analyses:
        logger.info(f"Fetching partial results for active analysis: {session_id}")

        session_data = active_analyses[session_id]
        orchestrator = session_data['orchestrator']
        config_path = session_data['config_path']

        # Get accumulated answers so far
        accumulated_answers = orchestrator.layer4_accumulator.get_accumulated_answers()

        # Load config
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(config_path)

        # Build partial browser output
        partial_browser_output = orchestrator._build_partial_browser_output(
            accumulated_answers,
            parsed_config
        )

        # Transform to legacy format
        legacy_result = _transform_to_legacy_format(partial_browser_output)

        return jsonify({
            'success': True,
            'result': legacy_result,
            'partial': True,  # Flag indicating partial results
            'statistics': {
                'processing_time': 0,  # Not yet available
                'total_tokens': orchestrator.layer5_token_manager.total_tokens_used,
                'estimated_cost': 'In progress',
                'questions_answered': len([a for answers in accumulated_answers.values() for a in answers]),
                'total_questions': parsed_config.total_questions,
                'average_confidence': 'In progress'
            }
        })

    else:
        return jsonify({'success': False, 'error': 'Session not found'}), 404


# ============================================================================
# EXCEL DASHBOARD EXPORT
# ============================================================================

@app.route('/api/export/excel-dashboard/<session_id>', methods=['GET'])
def export_excel_dashboard(session_id):
    """Generate executive Excel dashboard with charts (supports partial results)"""

    browser_output = None
    is_partial = False

    # Check completed_analyses first (NEW - primary storage)
    if session_id in completed_analyses:
        logger.info(f"Exporting completed analysis: {session_id}")
        session_data = completed_analyses[session_id]
        result = session_data['result']
        orchestrator = session_data['orchestrator']
        config_path = session_data['config_path']

        # Get complete browser-formatted output
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(config_path)
        browser_output = orchestrator.get_browser_output(result, parsed_config)
        is_partial = False

    # Check legacy analysis_results (LEGACY - backward compatibility)
    elif session_id in analysis_results:
        logger.info(f"Exporting completed analysis (legacy): {session_id}")
        session_data = analysis_results[session_id]
        result = session_data['result']
        orchestrator = session_data['orchestrator']
        config_path = session_data['config_path']

        # Get complete browser-formatted output
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(config_path)
        browser_output = orchestrator.get_browser_output(result, parsed_config)
        is_partial = False

    # Check partial_analyses (stopped by user)
    elif session_id in partial_analyses:
        logger.info(f"Exporting partial analysis: {session_id}")
        session_data = partial_analyses[session_id]
        orchestrator = session_data['orchestrator']
        config_path = session_data['config_path']

        # Get accumulated answers so far
        accumulated_answers = orchestrator.layer4_accumulator.get_accumulated_answers()

        # Load config
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(config_path)

        # Build partial browser output
        browser_output = orchestrator._build_partial_browser_output(
            accumulated_answers,
            parsed_config
        )
        is_partial = True

    # Check active analyses (in-progress)
    elif session_id in active_analyses:
        logger.info(f"Exporting partial/stopped analysis: {session_id}")
        session_data = active_analyses[session_id]
        orchestrator = session_data['orchestrator']
        config_path = session_data['config_path']

        # Get accumulated answers so far
        accumulated_answers = orchestrator.layer4_accumulator.get_accumulated_answers()

        # Load config
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(config_path)

        # Build partial browser output
        browser_output = orchestrator._build_partial_browser_output(
            accumulated_answers,
            parsed_config
        )
        is_partial = True

    else:
        return jsonify({'success': False, 'error': 'Session not found'}), 404

    try:
        # Lazy import to prevent app crash if openpyxl not installed
        from services.excel_dashboard import ExcelDashboardGenerator

        # Generate Excel dashboard (now works with both complete and partial)
        generator = ExcelDashboardGenerator(browser_output, is_partial=is_partial)
        excel_file = generator.generate()

        # Use different filename for partial exports
        filename = 'CIPP_Executive_Dashboard_PARTIAL.xlsx' if is_partial else 'CIPP_Executive_Dashboard.xlsx'

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.error(f"Excel export failed: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# STOP ANALYSIS
# ============================================================================

@app.route('/api/stop/<session_id>', methods=['POST'])
def stop_analysis(session_id):
    """Stop ongoing analysis"""
    logger.info(f"Stop requested for: {session_id}")

    # Check if analysis is active (check active_analyses AND analysis_threads)
    found = False

    if session_id in active_analyses:
        # Set stop flag on orchestrator
        orchestrator = active_analyses[session_id]['orchestrator']
        orchestrator.stop_requested = True
        logger.info(f"Stop flag set on orchestrator: {session_id}")
        found = True

    if session_id in analysis_threads:
        logger.info(f"Found in analysis_threads: {session_id}")
        found = True

    if found:
        # Send error event to close SSE gracefully
        if session_id in progress_queues:
            try:
                progress_queues[session_id].put_nowait(('error', 'Analysis stopped by user'))
                logger.info(f"Stop event queued for SSE: {session_id}")
            except:
                pass  # Queue might be full

        return jsonify({'success': True, 'message': 'Stop signal sent'})

    # Check completed analyses (NEW - primary storage)
    if session_id in completed_analyses:
        logger.info(f"Analysis already complete: {session_id}")
        return jsonify({'success': True, 'message': 'Analysis already complete'})

    # Check legacy completed analyses
    if session_id in analysis_results:
        logger.info(f"Analysis already complete (legacy): {session_id}")
        return jsonify({'success': True, 'message': 'Analysis already complete'})

    # Check partial analyses
    if session_id in partial_analyses:
        logger.info(f"Analysis already stopped: {session_id}")
        return jsonify({'success': True, 'message': 'Analysis already stopped'})

    logger.warning(f"Session not found: {session_id}")
    logger.info(f"Active analyses: {list(active_analyses.keys())}")
    logger.info(f"Analysis threads: {list(analysis_threads.keys())}")
    return jsonify({'success': False, 'error': 'Session not found'}), 404


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/admin/sessions', methods=['GET'])
def get_all_sessions():
    """Admin endpoint: Get all active, completed, and partial analyses"""
    from datetime import datetime

    # DIAGNOSTIC LOGGING
    logger.info("="*60)
    logger.info("ADMIN SESSIONS REQUEST")
    logger.info(f"Active analyses keys: {list(active_analyses.keys())}")
    logger.info(f"Completed analyses keys: {list(completed_analyses.keys())}")
    logger.info(f"Partial analyses keys: {list(partial_analyses.keys())}")
    logger.info(f"Legacy results keys: {list(analysis_results.keys())}")
    logger.info(f"Session timestamps keys: {list(session_timestamps.keys())}")
    logger.info("="*60)

    def format_session_info(session_id, session_data, status):
        """Helper to format session data for admin view"""
        try:
            info = {
                'session_id': session_id,
                'status': status,
                'pdf_path': session_data.get('pdf_path', 'N/A'),
                'config_path': session_data.get('config_path', 'N/A'),
            }

            # Add timestamp if available
            if 'completed_at' in session_data:
                info['completed_at'] = session_data['completed_at'].isoformat()
            if 'stopped_at' in session_data:
                info['stopped_at'] = session_data['stopped_at'].isoformat()
            if 'started_at' in session_data:
                info['started_at'] = session_data['started_at'].isoformat()

            # Add result statistics if available (with error handling)
            if 'result' in session_data:
                result = session_data['result']
                # Check if result has the expected attributes (it's a dataclass)
                info['questions_answered'] = getattr(result, 'questions_answered', 'N/A')
                info['total_pages'] = getattr(result, 'total_pages', 'N/A')
                info['total_tokens'] = getattr(result, 'total_tokens', 'N/A')
                info['processing_time'] = getattr(result, 'processing_time_seconds', 'N/A')

            return info
        except Exception as e:
            # Log the error but still return basic info
            logger.error(f"Error formatting session {session_id}: {e}", exc_info=True)
            return {
                'session_id': session_id,
                'status': f'error_{status}',
                'pdf_path': 'Error formatting',
                'config_path': 'Error formatting',
                'error': str(e)
            }

    # Gather all sessions
    sessions = {
        'active': [
            format_session_info(sid, data, 'active')
            for sid, data in active_analyses.items()
        ],
        'completed': [
            format_session_info(sid, data, 'completed')
            for sid, data in completed_analyses.items()
        ],
        'partial': [
            format_session_info(sid, data, 'partial')
            for sid, data in partial_analyses.items()
        ],
        'legacy': [
            format_session_info(sid, data, 'legacy_completed')
            for sid, data in analysis_results.items()
        ]
    }

    # Summary counts
    summary = {
        'total_sessions': sum(len(v) for v in sessions.values()),
        'active_count': len(sessions['active']),
        'completed_count': len(sessions['completed']),
        'partial_count': len(sessions['partial']),
        'legacy_count': len(sessions['legacy'])
    }

    return jsonify({
        'success': True,
        'summary': summary,
        'sessions': sessions
    })


# ============================================================================
# CIPP ANALYZER FRONTEND
# ============================================================================

@app.route('/cipp-analyzer')
def cipp_analyzer():
    """Serve CIPP Analyzer application (REBUILT for HOTDOG AI)"""
    return send_from_directory(Config.BASE_DIR, 'analyzer_rebuild.html')

@app.route('/admin/sessions')
def admin_sessions():
    """Serve admin session monitoring page"""
    return send_from_directory(Config.BASE_DIR, 'admin_sessions.html')

@app.route('/api/config/questions', methods=['GET'])
def get_question_config():
    """Load question configuration from JSON file"""
    try:
        config_path = Config.BASE_DIR / 'config' / 'cipp_questions_default.json'

        if not config_path.exists():
            return jsonify({
                'success': False,
                'error': 'Question configuration file not found'
            }), 404

        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        # Transform to frontend format
        sections = config_data.get('sections', [])
        total_questions = sum(len(section.get('questions', [])) for section in sections)

        return jsonify({
            'success': True,
            'config': {
                'sections': sections,
                'totalQuestions': total_questions
            }
        })

    except Exception as e:
        logger.error(f'Failed to load question config: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/progress-estimator')
def progress_estimator():
    """Serve CIPP Production Estimator (Comprehensive - All Penalties/Boosts/Pipe Sizes)"""
    return send_from_directory(Config.BASE_DIR / 'legacy' / 'apps' / 'progress-estimator', 'CIPPEstimator_Comprehensive.html')


# ============================================================================
# OPENAI API PROXY (for Progress Estimator AI Insights)
# ============================================================================

@app.route('/api/openai/chat', methods=['POST'])
def openai_chat_proxy():
    """
    Proxy endpoint for OpenAI API calls
    Securely uses server-side OPENAI_API_KEY from environment
    """
    import requests

    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OPENAI_API_KEY not configured in environment")
        return jsonify({
            'success': False,
            'error': 'OpenAI API key not configured on server. Contact administrator.'
        }), 500

    try:
        # Get request data from frontend
        data = request.get_json()

        # Validate required fields
        if 'messages' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: messages'
            }), 400

        # Prepare OpenAI API request
        openai_request = {
            'model': data.get('model', 'gpt-4'),
            'messages': data['messages'],
            'temperature': data.get('temperature', 0.7),
            'max_tokens': data.get('max_tokens', 600)
        }

        logger.info(f"Proxying OpenAI request: model={openai_request['model']}, messages={len(openai_request['messages'])}")

        # Call OpenAI API
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            json=openai_request,
            timeout=30
        )

        # Check response status
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': f'OpenAI API returned {response.status_code}',
                'details': response.text
            }), response.status_code

        # Return successful response
        result = response.json()
        logger.info(f"OpenAI response received: {result['choices'][0]['finish_reason']}")

        return jsonify({
            'success': True,
            'data': result
        })

    except requests.exceptions.Timeout:
        logger.error("OpenAI API request timed out")
        return jsonify({
            'success': False,
            'error': 'Request timed out. Please try again.'
        }), 504

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenAI API request failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to connect to OpenAI API',
            'details': str(e)
        }), 503

    except Exception as e:
        logger.error(f"Unexpected error in OpenAI proxy: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'details': str(e)
        }), 500


# ============================================================================
# VISUAL PROJECT SUMMARY (DASH APP INTEGRATION)
# ============================================================================

# Import and initialize Dash app
try:
    from services.cipp_dashboard.dash_app import create_dash_app
    dash_app = create_dash_app(app)
    logger.info("Visual Project Summary (Dash) integrated successfully")
except ImportError as e:
    logger.warning(f"Visual Project Summary not available: {e}")
    dash_app = None


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_sessions': len(active_analyses),
        'completed_sessions': len(analysis_results)
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({'error': 'Internal Server Error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler - return JSON instead of HTML"""
    logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'An unexpected error occurred. Please try again.'
    }), 500


# ============================================================================
# MAIN
# ============================================================================

# Start session cleanup scheduler
cleanup_expired_sessions()
logger.info("🧹 Session cleanup scheduler started (15-minute intervals)")

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("PM Tools Suite - Clean Rebuild")
    logger.info("="*60)

    # Get port and debug from environment (Render compatibility)
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    logger.info(f"Starting server on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
else:
    # For gunicorn
    logger.info("PM Tools Suite loaded (gunicorn mode)")
