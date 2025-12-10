"""
PM Tools Suite - Clean Rebuild
HOTDOG AI Document Analysis with Real-Time SSE Progress

Architecture: Threading-based (simple, proven, works)
"""
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
progress_queues = {}  # session_id -> Queue for SSE progress
analysis_threads = {}  # session_id -> Thread for cancellation
analysis_results = {}  # session_id -> result data

# Authentication - Load from environment variables
def load_authorized_users():
    """Load authorized users from environment variables for security."""
    users = {}

    # User 1
    user1_email = os.getenv('AUTH_USER1_EMAIL')
    user1_password = os.getenv('AUTH_USER1_PASSWORD')
    user1_name = os.getenv('AUTH_USER1_NAME', 'User 1')

    if user1_email and user1_password:
        users[user1_email] = {
            'password_hash': hashlib.sha256(user1_password.encode()).hexdigest(),
            'name': user1_name
        }

    # User 2
    user2_email = os.getenv('AUTH_USER2_EMAIL')
    user2_password = os.getenv('AUTH_USER2_PASSWORD')
    user2_name = os.getenv('AUTH_USER2_NAME', 'User 2')

    if user2_email and user2_password:
        users[user2_email] = {
            'password_hash': hashlib.sha256(user2_password.encode()).hexdigest(),
            'name': user2_name
        }

    if not users:
        print("WARNING: No authorized users configured. Set AUTH_USER*_EMAIL and AUTH_USER*_PASSWORD environment variables.")

    return users

AUTHORIZED_USERS = load_authorized_users()
active_sessions = {}


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

            # Transform: primary_answer{text, pages} → answer, page_citations
            primary_answer = q.get('primary_answer')
            if primary_answer and q.get('has_answer', False):
                legacy_question['answer'] = primary_answer.get('text', '')
                legacy_question['page_citations'] = primary_answer.get('pages', [])
                legacy_question['confidence'] = primary_answer.get('confidence', 0.0)
            else:
                legacy_question['answer'] = None
                legacy_question['page_citations'] = []
                legacy_question['confidence'] = 0.0

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

    if username not in AUTHORIZED_USERS:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != AUTHORIZED_USERS[username]['password_hash']:
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
        # Create or get queue
        if session_id not in progress_queues:
            progress_queues[session_id] = queue.Queue(maxsize=100)

        q = progress_queues[session_id]

        # Send connection event
        yield f"data: {json.dumps({'event': 'connected', 'session_id': session_id})}\n\n"

        # Stream events
        while True:
            try:
                # Get next event (15 second timeout for keepalive)
                event_type, data = q.get(timeout=15)

                # Check for done/error signals
                if event_type == 'done':
                    yield f"data: {json.dumps({'event': 'done'})}\n\n"
                    break

                if event_type == 'error':
                    yield f"data: {json.dumps({'event': 'error', 'error': data})}\n\n"
                    break

                # Send progress event
                yield f"data: {json.dumps({'event': event_type, **data})}\n\n"

            except queue.Empty:
                # Send keepalive
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
# HOTDOG ANALYSIS (NON-BLOCKING with Threading)
# ============================================================================

@app.route('/api/analyze', methods=['POST'])
def analyze_document():
    """Start HOTDOG AI analysis in background thread"""

    # Get request data
    data = request.json
    pdf_path = data.get('pdf_path')
    context_guardrails = data.get('context_guardrails', '')
    session_id = data.get('session_id', f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

    # Validate
    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'success': False, 'error': 'PDF file not found'}), 404

    # Get API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        return jsonify({'success': False, 'error': 'API key not configured'}), 500

    # Create progress queue for this session
    if session_id not in progress_queues:
        progress_queues[session_id] = queue.Queue(maxsize=100)

    progress_q = progress_queues[session_id]

    # Define progress callback (SIMPLE - just queue it)
    def progress_callback(event_type: str, event_data: dict):
        try:
            progress_q.put_nowait((event_type, event_data))
        except queue.Full:
            logger.warning(f"Progress queue full, dropping event: {event_type}")

    # Define analysis function to run in thread
    def run_analysis():
        try:
            logger.info(f"Starting analysis in thread: {session_id}")

            # Get config path
            config_path = str(Config.BASE_DIR / 'config' / 'cipp_questions_default.json')

            # Initialize orchestrator
            orchestrator = HotdogOrchestrator(
                openai_api_key=openai_key,
                config_path=config_path,
                context_guardrails=context_guardrails,
                progress_callback=progress_callback
            )

            # Run analysis (blocking in THIS thread, not main Flask thread)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    orchestrator.analyze_document(pdf_path, config_path)
                )

                # Store result
                analysis_results[session_id] = {
                    'result': result,
                    'orchestrator': orchestrator,
                    'config_path': config_path
                }

                # Signal done
                progress_q.put(('done', {}))

                logger.info(f"Analysis complete: {session_id}")

            finally:
                loop.close()

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            progress_q.put(('error', str(e)))

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
    """Get analysis results after completion"""

    if session_id not in analysis_results:
        return jsonify({'success': False, 'error': 'Session not found'}), 404

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


# ============================================================================
# EXCEL DASHBOARD EXPORT
# ============================================================================

@app.route('/api/export/excel-dashboard/<session_id>', methods=['GET'])
def export_excel_dashboard(session_id):
    """Generate executive Excel dashboard with charts"""

    if session_id not in analysis_results:
        return jsonify({'success': False, 'error': 'Session not found'}), 404

    try:
        # Lazy import to prevent app crash if openpyxl not installed
        from services.excel_dashboard import ExcelDashboardGenerator

        session_data = analysis_results[session_id]
        result = session_data['result']
        orchestrator = session_data['orchestrator']

        # Get browser-formatted output
        from services.hotdog.layers import ConfigurationLoader
        config_loader = ConfigurationLoader()
        parsed_config = config_loader.load_from_json(session_data['config_path'])
        browser_output = orchestrator.get_browser_output(result, parsed_config)

        # Generate Excel dashboard
        generator = ExcelDashboardGenerator(browser_output)
        excel_file = generator.generate()

        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='CIPP_Executive_Dashboard.xlsx'
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

    if session_id in analysis_threads:
        # Note: Python threads can't be directly killed
        # We can only mark them and wait for orchestrator to check
        logger.info(f"Stop requested for: {session_id}")

        # Send error event to close SSE
        if session_id in progress_queues:
            progress_queues[session_id].put(('error', 'Analysis stopped by user'))

        return jsonify({'success': True, 'message': 'Stop signal sent'})

    return jsonify({'success': False, 'error': 'Session not found'}), 404


# ============================================================================
# CIPP ANALYZER FRONTEND
# ============================================================================

@app.route('/cipp-analyzer')
def cipp_analyzer():
    """Serve CIPP Analyzer application"""
    return send_from_directory(Config.BASE_DIR / 'legacy' / 'services' / 'bid-spec-analysis-v1', 'cipp_analyzer_clean.html')

@app.route('/progress-estimator')
def progress_estimator():
    """Serve CIPP Production Estimator (Comprehensive - All Penalties/Boosts/Pipe Sizes)"""
    return send_from_directory(Config.BASE_DIR / 'legacy' / 'apps' / 'progress-estimator', 'CIPPEstimator_Comprehensive.html')


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
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("PM Tools Suite - Clean Rebuild")
    logger.info("="*60)
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
else:
    # For gunicorn
    logger.info("PM Tools Suite loaded (gunicorn mode)")
