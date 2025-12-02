"""
PDF text extraction service following Single Responsibility Principle.
Handles all PDF text extraction logic with multiple library fallbacks.
Enhanced with page number preservation for CIPP analysis.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
import re

logger = logging.getLogger(__name__)


class PDFExtractionStrategy(ABC):
    """Abstract base class for PDF extraction strategies (Strategy Pattern)."""

    @abstractmethod
    def extract_text_with_pages(self, pdf_path: str) -> List[Tuple[int, str]]:
        """
        Extract text from PDF file with page numbers preserved.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of tuples (page_number, page_text)

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

    def extract_text_with_pages(self, pdf_path: str) -> List[Tuple[int, str]]:
        import PyPDF2

        pages = []
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages.append((page_num, page_text.strip()))

        logger.info(f"{self.name} extracted {len(pages)} pages from PDF")
        return pages


class PDFPlumberStrategy(PDFExtractionStrategy):
    """PDF extraction using pdfplumber library (preferred for layout preservation)."""

    @property
    def name(self) -> str:
        return "pdfplumber"

    def extract_text_with_pages(self, pdf_path: str) -> List[Tuple[int, str]]:
        import pdfplumber

        pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages.append((page_num, page_text.strip()))

        logger.info(f"{self.name} extracted {len(pages)} pages from PDF")
        return pages


class PDFMinerStrategy(PDFExtractionStrategy):
    """PDF extraction using pdfminer library."""

    @property
    def name(self) -> str:
        return "pdfminer"

    def extract_text_with_pages(self, pdf_path: str) -> List[Tuple[int, str]]:
        from pdfminer.high_level import extract_text

        # pdfminer doesn't provide per-page extraction easily,
        # so we extract all and split by page markers if present
        text = extract_text(pdf_path)

        # Try to split by common page markers
        page_pattern = r'--- PAGE (\d+) ---'
        matches = list(re.finditer(page_pattern, text))

        if matches:
            pages = []
            for i, match in enumerate(matches):
                page_num = int(match.group(1))
                start = match.end()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
                page_text = text[start:end].strip()
                if page_text:
                    pages.append((page_num, page_text))
        else:
            # No page markers, treat as single page
            pages = [(1, text.strip())] if text.strip() else []

        logger.info(f"{self.name} extracted {len(pages)} pages from PDF")
        return pages


class PDFExtractorService:
    """
    Service for extracting text from PDF files with page number preservation.
    Uses strategy pattern with fallback mechanism.
    """

    def __init__(self):
        self.strategies = self._initialize_strategies()

    def _initialize_strategies(self) -> List[PDFExtractionStrategy]:
        """Initialize available PDF extraction strategies based on installed libraries."""
        strategies = []

        # Try to import and register each strategy (in order of preference)
        try:
            import pdfplumber
            strategies.append(PDFPlumberStrategy())
            logger.debug("pdfplumber strategy available")
        except ImportError:
            logger.debug("pdfplumber not available")

        try:
            import PyPDF2
            strategies.append(PyPDF2Strategy())
            logger.debug("PyPDF2 strategy available")
        except ImportError:
            logger.debug("PyPDF2 not available")

        try:
            import pdfminer
            strategies.append(PDFMinerStrategy())
            logger.debug("pdfminer strategy available")
        except ImportError:
            logger.debug("pdfminer not available")

        if not strategies:
            raise ImportError("No PDF processing library available. Install PyPDF2, pdfplumber, or pdfminer.six")

        logger.info(f"Initialized PDF extractor with strategies: {[s.name for s in strategies]}")
        return strategies

    def extract_text_with_pages(self, pdf_path: str, min_length: int = 50) -> List[Tuple[int, str]]:
        """
        Extract text from PDF using the best available method, preserving page numbers.

        Args:
            pdf_path: Path to PDF file
            min_length: Minimum acceptable text length per page

        Returns:
            List of tuples (page_number, cleaned_page_text)

        Raises:
            Exception: If all extraction methods fail
        """
        logger.info(f"Extracting text from: {pdf_path}")

        last_error = None
        for strategy in self.strategies:
            try:
                pages = strategy.extract_text_with_pages(pdf_path)
                if pages and len(pages) > 0:
                    # Clean each page's text
                    cleaned_pages = [
                        (page_num, self._clean_text(text))
                        for page_num, text in pages
                        if len(text.strip()) >= min_length
                    ]

                    if cleaned_pages:
                        logger.info(f"Successfully extracted {len(cleaned_pages)} pages using {strategy.name}")
                        return cleaned_pages
            except Exception as e:
                last_error = e
                logger.warning(f"Strategy {strategy.name} failed: {e}")
                continue

        error_message = f"All PDF extraction methods failed. Last error: {last_error}"
        logger.error(error_message)
        raise Exception(error_message)

    def extract_text_combined(self, pdf_path: str, min_length: int = 50) -> str:
        """
        Extract text from PDF and combine all pages with page markers.

        Args:
            pdf_path: Path to PDF file
            min_length: Minimum acceptable text length per page

        Returns:
            Combined text with <PDF pg #> markers

        Raises:
            Exception: If all extraction methods fail
        """
        pages = self.extract_text_with_pages(pdf_path, min_length)

        combined_text = ""
        for page_num, page_text in pages:
            combined_text += f"\n\n<PDF pg {page_num}>\n{page_text}"

        return combined_text.strip()

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

        # Remove excessive whitespace within lines
        lines = []
        for line in text.split('\n'):
            cleaned_line = ' '.join(line.split())
            if cleaned_line:
                lines.append(cleaned_line)

        cleaned = '\n'.join(lines)

        # Remove excessive newlines (but preserve paragraph breaks)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        return cleaned.strip()

    def get_available_libraries(self) -> List[str]:
        """Return list of available PDF extraction library names."""
        return [strategy.name for strategy in self.strategies]
