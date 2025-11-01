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
from flask import Flask, render_template, send_from_directory, jsonify
from flask_cors import CORS

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
            }
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
        For now, returns a placeholder. Implement actual extraction logic.
        """
        from flask import request
        # TODO: Import and use the refactored PDF extraction service
        # from services.pdf_extractor import PDFExtractorService
        return jsonify({
            'error': 'PDF extraction service not yet integrated. Use refactored version in /Bid-Spec Analysis for CIPP/refactored/'
        }), 501

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
