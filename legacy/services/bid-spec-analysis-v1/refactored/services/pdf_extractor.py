"""
PDF text extraction service following Single Responsibility Principle.
Handles all PDF text extraction logic with multiple library fallbacks.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class PDFExtractionStrategy(ABC):
    """Abstract base class for PDF extraction strategies (Strategy Pattern)."""

    @abstractmethod
    def extract_text(self, pdf_path: str) -> str:
        """
        Extract text from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content

        Raises:
            Exception: If extraction fails
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the extraction strategy."""
        pass


class PyPDF2Strategy(PDFExtractionStrategy):
    """PDF extraction using PyPDF2 library."""

    @property
    def name(self) -> str:
        return "PyPDF2"

    def extract_text(self, pdf_path: str) -> str:
        import PyPDF2

        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"

        logger.info(f"{self.name} extracted {len(text)} characters from {len(pdf_reader.pages)} pages")
        return text.strip()


class PDFPlumberStrategy(PDFExtractionStrategy):
    """PDF extraction using pdfplumber library."""

    @property
    def name(self) -> str:
        return "pdfplumber"

    def extract_text(self, pdf_path: str) -> str:
        import pdfplumber

        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += f"\n--- PAGE {page_num + 1} ---\n{page_text}\n"

        logger.info(f"{self.name} extracted {len(text)} characters from {len(pdf.pages)} pages")
        return text.strip()


class PDFMinerStrategy(PDFExtractionStrategy):
    """PDF extraction using pdfminer library."""

    @property
    def name(self) -> str:
        return "pdfminer"

    def extract_text(self, pdf_path: str) -> str:
        from pdfminer.high_level import extract_text

        text = extract_text(pdf_path)
        logger.info(f"{self.name} extracted {len(text)} characters")
        return text.strip()


class PDFExtractorService:
    """
    Service for extracting text from PDF files.
    Uses strategy pattern with fallback mechanism.
    """

    def __init__(self):
        self.strategies = self._initialize_strategies()

    def _initialize_strategies(self) -> list[PDFExtractionStrategy]:
        """Initialize available PDF extraction strategies based on installed libraries."""
        strategies = []

        # Try to import and register each strategy
        try:
            import pdfplumber
            strategies.append(PDFPlumberStrategy())
        except ImportError:
            logger.debug("pdfplumber not available")

        try:
            import PyPDF2
            strategies.append(PyPDF2Strategy())
        except ImportError:
            logger.debug("PyPDF2 not available")

        try:
            import pdfminer
            strategies.append(PDFMinerStrategy())
        except ImportError:
            logger.debug("pdfminer not available")

        if not strategies:
            raise ImportError("No PDF processing library available. Install PyPDF2, pdfplumber, or pdfminer.six")

        logger.info(f"Initialized PDF extractor with strategies: {[s.name for s in strategies]}")
        return strategies

    def extract_text(self, pdf_path: str, min_length: int = 50) -> str:
        """
        Extract text from PDF using the best available method.

        Args:
            pdf_path: Path to PDF file
            min_length: Minimum acceptable text length

        Returns:
            Extracted and cleaned text

        Raises:
            Exception: If all extraction methods fail
        """
        logger.info(f"Extracting text from: {pdf_path}")

        last_error = None
        for strategy in self.strategies:
            try:
                text = strategy.extract_text(pdf_path)
                if text and len(text.strip()) > min_length:
                    logger.info(f"Successfully extracted text using {strategy.name}")
                    return self._clean_text(text)
            except Exception as e:
                last_error = e
                logger.warning(f"Strategy {strategy.name} failed: {e}")
                continue

        error_message = f"All PDF extraction methods failed. Last error: {last_error}"
        logger.error(error_message)
        raise Exception(error_message)

    def _clean_text(self, text: str) -> str:
        """
        Clean and format extracted text.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        import re

        # Remove excessive whitespace within lines
        lines = []
        for line in text.split('\n'):
            cleaned_line = ' '.join(line.split())
            if cleaned_line:
                lines.append(cleaned_line)

        cleaned = '\n'.join(lines)

        # Remove excessive newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        return cleaned.strip()

    def get_available_libraries(self) -> list[str]:
        """Return list of available PDF extraction library names."""
        return [strategy.name for strategy in self.strategies]
