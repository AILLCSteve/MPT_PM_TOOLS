"""
Main Flask application for CIPP Analyzer.
Refactored following SOLID principles and Clean Code practices.
"""

import logging
from flask import Flask, render_template
from flask_cors import CORS
from routes import api_bp
from config import Config

# Configure logging
logging.basicConfig(level=Config.LOG_LEVEL, format=Config.LOG_FORMAT)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """
    Application factory pattern for creating Flask app.

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp)

    # Register routes
    @app.route('/')
    def index():
        """Serve the main application page."""
        return render_template('index.html')

    @app.route('/app')
    def full_app():
        """Serve the full CIPP analyzer application."""
        return render_template('cipp_analyzer.html')

    logger.info("CIPP Analyzer application initialized successfully")
    return app


def run_standalone():
    """Run the application as a standalone server with browser auto-open."""
    import time
    import threading
    import webbrowser

    app = create_app()

    def start_server():
        """Start Flask server in a thread."""
        logger.info(f"Starting PDF extraction service on http://{Config.HOST}:{Config.PORT}")
        app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, use_reloader=False)

    def open_browser():
        """Open default web browser after delay."""
        time.sleep(Config.BROWSER_STARTUP_DELAY)
        logger.info("Opening web browser...")
        webbrowser.open(f'http://{Config.HOST}:{Config.PORT}')

    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    print("CIPP Spec Analyzer - Starting...")
    print(f"- PDF service running on http://{Config.HOST}:{Config.PORT}")
    print("- Browser should open automatically")
    print("- Keep this window open while using the app")
    print("- Press Ctrl+C to exit")

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    run_standalone()
