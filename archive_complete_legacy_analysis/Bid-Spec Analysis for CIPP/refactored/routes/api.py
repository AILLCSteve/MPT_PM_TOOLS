"""
API routes for CIPP Analyzer.
Handles PDF extraction endpoints following Clean Code principles.
"""

import base64
import logging
import os
import tempfile
from flask import Blueprint, request, jsonify
from services.pdf_extractor import PDFExtractorService
from config import Config

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')


class PDFExtractionRequest:
    """Value object for PDF extraction request data."""

    def __init__(self, pdf_data: str):
        self.pdf_data = pdf_data

    @classmethod
    def from_json(cls, data: dict):
        """
        Create request object from JSON data.

        Args:
            data: JSON request data

        Returns:
            PDFExtractionRequest instance

        Raises:
            ValueError: If required fields are missing
        """
        if not data or 'pdf_data' not in data:
            raise ValueError('No PDF data provided')
        return cls(data['pdf_data'])

    def decode_pdf_bytes(self) -> bytes:
        """
        Decode base64 PDF data to bytes.

        Returns:
            Decoded PDF bytes

        Raises:
            ValueError: If base64 decoding fails
        """
        try:
            return base64.b64decode(self.pdf_data)
        except Exception as e:
            raise ValueError(f'Invalid base64 data: {e}')


class TemporaryPDFFile:
    """Context manager for temporary PDF files."""

    def __init__(self, pdf_bytes: bytes):
        self.pdf_bytes = pdf_bytes
        self.temp_file = None
        self.temp_path = None

    def __enter__(self) -> str:
        """Create temporary PDF file and return its path."""
        self.temp_file = tempfile.NamedTemporaryFile(
            suffix=Config.PDF_TEMP_SUFFIX,
            delete=False
        )
        self.temp_file.write(self.pdf_bytes)
        self.temp_file.close()
        self.temp_path = self.temp_file.name
        return self.temp_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up temporary file."""
        if self.temp_path and os.path.exists(self.temp_path):
            try:
                os.unlink(self.temp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {self.temp_path}: {e}")


# Initialize PDF extractor service
pdf_extractor = PDFExtractorService()


@api_bp.route('/extract_pdf', methods=['POST'])
def extract_pdf():
    """
    API endpoint to extract text from PDF.

    Expected JSON payload:
        {
            "pdf_data": "base64_encoded_pdf_content"
        }

    Returns:
        JSON response with extracted text or error message
    """
    try:
        # Parse and validate request
        request_data = PDFExtractionRequest.from_json(request.get_json())
        pdf_bytes = request_data.decode_pdf_bytes()

        # Extract text from PDF using temporary file
        with TemporaryPDFFile(pdf_bytes) as temp_path:
            extracted_text = pdf_extractor.extract_text(
                temp_path,
                min_length=Config.MIN_TEXT_LENGTH
            )

            if not extracted_text:
                return jsonify({'error': 'No readable text found in PDF'}), 400

            logger.info(f"Successfully extracted {len(extracted_text)} characters")

            return jsonify({
                'success': True,
                'text': extracted_text,
                'length': len(extracted_text),
                'method': pdf_extractor.get_available_libraries()[0]
            })

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        logger.error(f"PDF extraction error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify service status."""
    import sys

    return jsonify({
        'status': 'healthy',
        'available_libraries': pdf_extractor.get_available_libraries(),
        'libraries_status': {
            'PyPDF2': 'PyPDF2' in sys.modules,
            'pdfplumber': 'pdfplumber' in sys.modules,
            'pdfminer': 'pdfminer' in sys.modules
        }
    })
