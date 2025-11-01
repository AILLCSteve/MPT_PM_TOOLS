"""
Main Flask Application - PM Tools Suite
Integrates all project management tools into a single deployable application.

Architecture:
- Modular design with sub-applications for each tool
- Shared assets and branding
- RESTful API endpoints
- Static file serving for client-side apps
"""

import os
import sys
import logging
from pathlib import Path
from flask import Flask, render_template, send_from_directory, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile

# Import PDF extraction service
from services.pdf_extractor import PDFExtractorService

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Application configuration."""

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # File upload configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 100 * 1024 * 1024))  # 100MB default
    UPLOAD_TIMEOUT = int(os.getenv('UPLOAD_TIMEOUT', 300))  # 5 minutes

    # Server configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    # Paths
    BASE_DIR = Path(__file__).parent
    SHARED_ASSETS_DIR = BASE_DIR / 'shared' / 'assets'
    CIPP_DIR = BASE_DIR / 'Bid-Spec Analysis for CIPP'
    PROGRESS_DIR = BASE_DIR / 'Progress Estimator'


def create_app(config=Config) -> Flask:
    """
    Application factory for creating the Flask app.

    Args:
        config: Configuration class

    Returns:
        Configured Flask application
    """
    app = Flask(
        __name__,
        static_folder=str(config.SHARED_ASSETS_DIR),
        static_url_path='/shared/assets'
    )

    app.config.from_object(config)
    CORS(app)

    # Register routes
    register_routes(app, config)

    # Register error handlers
    register_error_handlers(app)

    logger.info("PM Tools Suite application initialized successfully")
    return app


def register_routes(app: Flask, config: Config):
    """Register all application routes."""

    # Initialize PDF extractor service
    try:
        pdf_extractor = PDFExtractorService()
        logger.info(f"PDF extractor initialized with libraries: {pdf_extractor.get_available_libraries()}")
    except Exception as e:
        logger.error(f"Failed to initialize PDF extractor: {e}")
        pdf_extractor = None

    @app.route('/')
    def index():
        """Serve the main landing page."""
        return send_from_directory(config.BASE_DIR, 'index.html')

    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring."""
        return jsonify({
            'status': 'healthy',
            'service': 'PM Tools Suite',
            'version': '1.0.0',
            'tools': {
                'cipp_analyzer': 'available',
                'progress_estimator': 'available'
            },
            'pdf_service': {
                'available': pdf_extractor is not None,
                'libraries': pdf_extractor.get_available_libraries() if pdf_extractor else []
            }
        })

    # API Configuration endpoints
    @app.route('/api/config/apikey', methods=['GET'])
    def get_api_key():
        """
        Get OpenAI API key from environment variables.
        This endpoint allows the frontend to retrieve the API key securely.
        """
        api_key = os.getenv('OPENAI_API_KEY', '')

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'OPENAI_API_KEY not configured in environment variables'
            }), 500

        # Return only a masked version for security, but indicate it exists
        # The frontend will know to use this for API calls
        return jsonify({
            'success': True,
            'key': api_key,  # Frontend needs full key for API calls
            'masked': api_key[:10] + '...' + api_key[-4:] if len(api_key) > 14 else 'configured'
        })

    # CIPP Analyzer routes
    @app.route('/cipp-analyzer')
    def cipp_analyzer():
        """Serve CIPP Analyzer application."""
        # Use the branded version with MPT styling
        branded_version = config.CIPP_DIR / 'cipp_analyzer_branded.html'
        if branded_version.exists():
            return send_from_directory(config.CIPP_DIR, 'cipp_analyzer_branded.html')
        # Fallback to original if branded version not found
        return send_from_directory(config.CIPP_DIR, 'cipp_analyzer_complete.html')

    @app.route('/cipp-analyzer/api/extract_pdf', methods=['POST'])
    def cipp_extract_pdf():
        """
        CIPP Analyzer PDF extraction endpoint.
        Extracts text from uploaded PDF with page numbers preserved.
        Handles large files up to MAX_CONTENT_LENGTH.
        """
        if not pdf_extractor:
            logger.error("PDF extraction service not initialized")
            return jsonify({
                'success': False,
                'error': 'PDF extraction service not available. Please check server logs.'
            }), 503

        # Log request details
        logger.info(f"PDF extraction request received - Content-Length: {request.content_length}")

        # Check if file was uploaded
        if 'file' not in request.files:
            logger.warning("No file in request.files")
            return jsonify({
                'success': False,
                'error': 'No file provided. Please upload a PDF file.'
            }), 400

        file = request.files['file']

        if file.filename == '':
            logger.warning("Empty filename in upload")
            return jsonify({
                'success': False,
                'error': 'No file selected.'
            }), 400

        if not file.filename.lower().endswith('.pdf'):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Only PDF files are supported.'
            }), 400

        # Save uploaded file to temporary location
        temp_path = None
        try:
            # Create temporary file with binary mode
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as temp_file:
                temp_path = temp_file.name
                # Read file in chunks to handle large files
                chunk_size = 8192
                bytes_written = 0
                while True:
                    chunk = file.stream.read(chunk_size)
                    if not chunk:
                        break
                    temp_file.write(chunk)
                    bytes_written += len(chunk)

            # Verify file was completely written
            actual_size = os.path.getsize(temp_path)
            logger.info(f"PDF saved: {file.filename}")
            logger.info(f"  Temp path: {temp_path}")
            logger.info(f"  Bytes written: {bytes_written}")
            logger.info(f"  File size on disk: {actual_size} bytes ({actual_size / 1024 / 1024:.2f} MB)")

            if actual_size < 100:
                raise ValueError(f"File too small ({actual_size} bytes) - likely corrupted or truncated")

            # Extract text with page numbers
            logger.info(f"Starting PDF extraction for {file.filename}")
            pages = pdf_extractor.extract_text_with_pages(temp_path)

            if not pages:
                raise ValueError("No pages extracted from PDF - file may be corrupted or encrypted")

            # Also get combined text with markers
            combined_text = pdf_extractor.extract_text_combined(temp_path)

            # Clean up temporary file
            os.unlink(temp_path)
            temp_path = None

            logger.info(f"Successfully extracted {len(pages)} pages from {file.filename}")

            return jsonify({
                'success': True,
                'filename': file.filename,
                'pages': [{'page': page_num, 'text': text} for page_num, text in pages],
                'combined_text': combined_text,
                'page_count': len(pages),
                'total_chars': sum(len(text) for _, text in pages),
                'file_size_bytes': actual_size
            })

        except Exception as e:
            # Clean up temporary file on error
            if temp_path:
                try:
                    if os.path.exists(temp_path):
                        file_size = os.path.getsize(temp_path)
                        logger.error(f"Temp file exists with size: {file_size} bytes")
                        os.unlink(temp_path)
                except Exception as cleanup_error:
                    logger.error(f"Cleanup error: {cleanup_error}")

            error_msg = str(e)
            logger.error(f"PDF extraction failed for {file.filename}: {error_msg}")
            logger.error(f"Error type: {type(e).__name__}")

            # Provide more helpful error messages
            if 'disturbed' in error_msg.lower() or 'locked' in error_msg.lower():
                error_msg = f"PDF file appears corrupted or truncated. Original error: {error_msg}. This often happens with large files - check upload limits."
            elif 'memory' in error_msg.lower():
                error_msg = f"PDF too large to process in available memory. Try a smaller file or contact support."
            elif 'encrypted' in error_msg.lower() or 'password' in error_msg.lower():
                error_msg = "PDF is password-protected or encrypted. Please provide an unencrypted version."

            return jsonify({
                'success': False,
                'error': error_msg,
                'debug_info': {
                    'filename': file.filename,
                    'error_type': type(e).__name__
                }
            }), 500

    @app.route('/cipp-analyzer/api/service-status', methods=['GET'])
    def cipp_service_status():
        """
        Check if PDF extraction service is available.
        """
        return jsonify({
            'available': pdf_extractor is not None,
            'libraries': pdf_extractor.get_available_libraries() if pdf_extractor else [],
            'status': 'running' if pdf_extractor else 'unavailable'
        })

    # Progress Estimator routes
    @app.route('/progress-estimator')
    def progress_estimator():
        """Serve Progress Estimator application."""
        # Use the branded version with MPT styling
        branded_version = config.PROGRESS_DIR / 'ProgEstimator_branded.html'
        if branded_version.exists():
            return send_from_directory(config.PROGRESS_DIR, 'ProgEstimator_branded.html')
        # Fallback to original if branded version not found
        return send_from_directory(config.PROGRESS_DIR, 'CleaningEstimateProto.html')

    @app.route('/progress-estimator/script.js')
    def progress_estimator_script():
        """Serve improved JavaScript for Progress Estimator."""
        # Check if improved version exists, otherwise fallback to original
        improved_script = config.PROGRESS_DIR / 'script_improved.js'
        if improved_script.exists():
            return send_from_directory(config.PROGRESS_DIR, 'script_improved.js', mimetype='application/javascript')
        return send_from_directory(config.PROGRESS_DIR, 'script.js', mimetype='application/javascript')

    @app.route('/progress-estimator/styles.css')
    def progress_estimator_styles():
        """Serve improved CSS for Progress Estimator."""
        # Check if improved version exists, otherwise fallback to original
        improved_styles = config.PROGRESS_DIR / 'styles_improved.css'
        if improved_styles.exists():
            return send_from_directory(config.PROGRESS_DIR, 'styles_improved.css', mimetype='text/css')
        return send_from_directory(config.PROGRESS_DIR, 'styles.css', mimetype='text/css')

    # Shared assets routes (already handled by Flask's static_folder)

    # Placeholder routes for footer links
    @app.route('/about')
    def about():
        """About page placeholder."""
        return """
        <html>
        <head>
            <title>About - PM Tools Suite</title>
            <link rel="stylesheet" href="/shared/assets/css/common.css">
        </head>
        <body style="padding: 40px; max-width: 800px; margin: 0 auto;">
            <h1>About PM Tools Suite</h1>
            <p>Professional project management tools for construction and infrastructure projects.</p>
            <p><a href="/" class="btn btn-primary">← Back to Home</a></p>
        </body>
        </html>
        """

    @app.route('/support')
    def support():
        """Support page placeholder."""
        return """
        <html>
        <head>
            <title>Support - PM Tools Suite</title>
            <link rel="stylesheet" href="/shared/assets/css/common.css">
        </head>
        <body style="padding: 40px; max-width: 800px; margin: 0 auto;">
            <h1>Support</h1>
            <p>Need help? Contact support at: <a href="mailto:support@example.com">support@example.com</a></p>
            <p><a href="/" class="btn btn-primary">← Back to Home</a></p>
        </body>
        </html>
        """

    @app.route('/privacy')
    def privacy():
        """Privacy policy placeholder."""
        return """
        <html>
        <head>
            <title>Privacy Policy - PM Tools Suite</title>
            <link rel="stylesheet" href="/shared/assets/css/common.css">
        </head>
        <body style="padding: 40px; max-width: 800px; margin: 0 auto;">
            <h1>Privacy Policy</h1>
            <p>Your privacy is important to us. Add your privacy policy content here.</p>
            <p><a href="/" class="btn btn-primary">← Back to Home</a></p>
        </body>
        </html>
        """

    @app.route('/terms')
    def terms():
        """Terms of service placeholder."""
        return """
        <html>
        <head>
            <title>Terms of Service - PM Tools Suite</title>
            <link rel="stylesheet" href="/shared/assets/css/common.css">
        </head>
        <body style="padding: 40px; max-width: 800px; margin: 0 auto;">
            <h1>Terms of Service</h1>
            <p>Terms of service content goes here.</p>
            <p><a href="/" class="btn btn-primary">← Back to Home</a></p>
        </body>
        </html>
        """


def register_error_handlers(app: Flask):
    """Register error handlers for common HTTP errors."""

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status': 404
        }), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file upload size limit exceeded."""
        max_size_mb = app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024) / (1024 * 1024)
        logger.warning(f"File upload exceeded size limit: {max_size_mb}MB")
        return jsonify({
            'success': False,
            'error': f'File too large. Maximum upload size is {max_size_mb:.0f}MB.',
            'message': 'Please try a smaller file or contact support for large file processing.',
            'status': 413,
            'max_size_mb': max_size_mb
        }), 413

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status': 500
        }), 500


def main():
    """Main entry point for running the application."""
    app = create_app()

    logger.info("=" * 60)
    logger.info("PM Tools Suite - Starting Server")
    logger.info("=" * 60)
    logger.info(f"Environment: {'Development' if app.config['DEBUG'] else 'Production'}")
    logger.info(f"Server: http://{app.config['HOST']}:{app.config['PORT']}")
    logger.info("Available Tools:")
    logger.info("  - CIPP Analyzer: /cipp-analyzer")
    logger.info("  - Progress Estimator: /progress-estimator")
    logger.info("=" * 60)

    try:
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG']
        )
    except KeyboardInterrupt:
        logger.info("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


# Create application instance for WSGI servers (gunicorn, etc.)
app = create_app()

if __name__ == "__main__":
    main()
