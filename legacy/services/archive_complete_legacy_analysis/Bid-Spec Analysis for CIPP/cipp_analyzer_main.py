#!/usr/bin/env python3
"""
CIPP Spec Analyzer - Main Executable
Combines PDF service and web interface in a single executable
"""

import sys
import os
import time
import threading
import webbrowser
import tempfile
from pathlib import Path

# PDF extraction service imports
import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import base64

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import PDF processing libraries
try:
    import PyPDF2
    PDF_LIBRARY = "PyPDF2"
    logger.info("Using PyPDF2 for PDF processing")
except ImportError:
    try:
        import pdfplumber
        PDF_LIBRARY = "pdfplumber"
        logger.info("Using pdfplumber for PDF processing")
    except ImportError:
        try:
            from pdfminer.high_level import extract_text
            PDF_LIBRARY = "pdfminer"
            logger.info("Using pdfminer for PDF processing")
        except ImportError:
            PDF_LIBRARY = None
            logger.error("No PDF processing library found.")

# Flask app setup
app = Flask(__name__)
CORS(app)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# PDF extraction functions (copied from pdf_extractor.py)
def extract_text_pypdf2(pdf_path):
    """Extract text using PyPDF2"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\\n--- PAGE {page_num + 1} ---\\n{page_text}\\n"

        logger.info(f"PyPDF2 extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
        return text.strip()
    except Exception as e:
        logger.error(f"PyPDF2 extraction failed: {e}")
        raise

def extract_text_pdfplumber(pdf_path):
    """Extract text using pdfplumber"""
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\\n--- PAGE {page_num + 1} ---\\n{page_text}\\n"

        logger.info(f"pdfplumber extracted {len(text)} characters from {len(pdf.pages)} pages")
        return text.strip()
    except Exception as e:
        logger.error(f"pdfplumber extraction failed: {e}")
        raise

def extract_text_pdfminer(pdf_path):
    """Extract text using pdfminer"""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(pdf_path)
        logger.info(f"pdfminer extracted {len(text)} characters")
        return text.strip()
    except Exception as e:
        logger.error(f"pdfminer extraction failed: {e}")
        raise

def extract_pdf_text(pdf_path):
    """Extract text from PDF using the best available method"""
    if not PDF_LIBRARY:
        raise Exception("No PDF processing library available.")

    logger.info(f"Extracting text from: {pdf_path}")

    # Try different extraction methods
    methods = []
    if PDF_LIBRARY == "pdfplumber":
        methods = [extract_text_pdfplumber, extract_text_pypdf2, extract_text_pdfminer]
    elif PDF_LIBRARY == "PyPDF2":
        methods = [extract_text_pypdf2, extract_text_pdfplumber, extract_text_pdfminer]
    else:  # pdfminer
        methods = [extract_text_pdfminer, extract_text_pdfplumber, extract_text_pypdf2]

    last_error = None
    for method in methods:
        try:
            text = method(pdf_path)
            if text and len(text.strip()) > 50:
                logger.info(f"Successfully extracted text using {method.__name__}")
                return text
        except Exception as e:
            last_error = e
            logger.warning(f"Method {method.__name__} failed: {e}")
            continue

    raise Exception(f"All PDF extraction methods failed. Last error: {last_error}")

def clean_extracted_text(text):
    """Clean and format extracted text"""
    if not text:
        return ""

    lines = []
    for line in text.split('\\n'):
        cleaned_line = ' '.join(line.split())
        if cleaned_line:
            lines.append(cleaned_line)

    cleaned = '\\n'.join(lines)

    import re
    cleaned = re.sub(r'\\n{3,}', '\\n\\n', cleaned)
    return cleaned.strip()

# Flask routes
@app.route('/extract_pdf', methods=['POST'])
def extract_pdf_endpoint():
    """API endpoint to extract text from PDF"""
    try:
        data = request.get_json()

        if not data or 'pdf_data' not in data:
            return jsonify({'error': 'No PDF data provided'}), 400

        try:
            pdf_bytes = base64.b64decode(data['pdf_data'])
        except Exception as e:
            return jsonify({'error': f'Invalid base64 data: {e}'}), 400

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(pdf_bytes)
            temp_path = temp_file.name

        try:
            extracted_text = extract_pdf_text(temp_path)

            if not extracted_text or len(extracted_text.strip()) < 10:
                return jsonify({'error': 'No readable text found in PDF'}), 400

            cleaned_text = clean_extracted_text(extracted_text)
            logger.info(f"Successfully extracted {len(cleaned_text)} characters")

            return jsonify({
                'success': True,
                'text': cleaned_text,
                'length': len(cleaned_text),
                'method': PDF_LIBRARY
            })

        finally:
            try:
                os.unlink(temp_path)
            except:
                pass

    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'pdf_library': PDF_LIBRARY,
        'libraries_available': {
            'PyPDF2': 'PyPDF2' in sys.modules,
            'pdfplumber': 'pdfplumber' in sys.modules,
            'pdfminer': 'pdfminer' in sys.modules
        }
    })

# HTML content (embedded)
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CIPP Spec Analyzer</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 30px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        h1 { color: #333; margin-bottom: 20px; }
        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-weight: 500;
        }
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏗️ CIPP Spec Analyzer</h1>
        <div class="status success">
            ✅ PDF extraction service is running!<br>
            ✅ Application ready to use
        </div>
        <p>The CIPP Spec Analyzer executable is running successfully.</p>
        <p>This is a simplified interface. The full application will load in a moment...</p>
        <a href="#" class="btn" onclick="window.location.reload()">🔄 Refresh</a>
    </div>

    <script>
        // Auto-redirect to full application
        setTimeout(() => {
            window.location.href = '/app';
        }, 3000);
    </script>
</body>
</html>'''

@app.route('/')
def index():
    """Serve the main page"""
    return HTML_CONTENT

@app.route('/app')
def full_app():
    """Serve the full application"""
    try:
        # Try to read the full HTML file
        html_path = get_resource_path('cipp_analyzer_complete.html')
        if os.path.exists(html_path):
            with open(html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"<h1>Error: Could not find application file at {html_path}</h1>"
    except Exception as e:
        return f"<h1>Error loading application: {e}</h1>"

def start_flask_server():
    """Start the Flask server in a separate thread"""
    logger.info("Starting PDF extraction service on http://localhost:5000")
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)

def open_browser():
    """Open the default web browser"""
    time.sleep(2)  # Wait for Flask to start
    logger.info("Opening web browser...")
    webbrowser.open('http://localhost:5000')

def main():
    """Main entry point"""
    print("CIPP Spec Analyzer - Starting...")
    print("PDF extraction service: Starting on http://localhost:5000")

    if not PDF_LIBRARY:
        print("ERROR: No PDF processing library found!")
        print("Please ensure PyPDF2, pdfplumber, or pdfminer.six is available.")
        input("Press Enter to exit...")
        return

    # Start Flask server in background thread
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()

    # Start browser in background thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    print("Application started!")
    print("- PDF service running on http://localhost:5000")
    print("- Browser should open automatically")
    print("- Keep this window open while using the app")
    print("- Press Ctrl+C to exit")

    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\\nShutting down...")
        sys.exit(0)

if __name__ == "__main__":
    main()