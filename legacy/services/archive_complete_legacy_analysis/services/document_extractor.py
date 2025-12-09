"""
Multi-format document text extraction service.
Handles PDFs, text files, Word documents, and other common formats.
Uses robust extraction methods with automatic format detection.
"""

import logging
import os
import mimetypes
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict
import re

logger = logging.getLogger(__name__)


class DocumentExtractionStrategy(ABC):
    """Abstract base class for document extraction strategies."""

    @abstractmethod
    def extract_text_with_pages(self, file_path: str) -> List[Tuple[int, str]]:
        """
        Extract text from document with page numbers preserved.

        Args:
            file_path: Path to document file

        Returns:
            List of tuples (page_number, page_text)

        Raises:
            Exception: If extraction fails
        """
        pass

    @abstractmethod
    def supports_file(self, filename: str) -> bool:
        """Check if this strategy supports the given file type."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the extraction strategy."""
        pass


class PyMuPDFStrategy(DocumentExtractionStrategy):
    """PDF extraction using PyMuPDF (fitz) - most robust PDF library."""

    @property
    def name(self) -> str:
        return "PyMuPDF"

    def supports_file(self, filename: str) -> bool:
        return filename.lower().endswith('.pdf')

    def extract_text_with_pages(self, file_path: str) -> List[Tuple[int, str]]:
        import fitz  # PyMuPDF

        pages = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text and text.strip():
                    pages.append((page_num + 1, text.strip()))
            doc.close()
        except Exception as e:
            logger.error(f"PyMuPDF extraction failed: {e}")
            raise

        logger.info(f"{self.name} extracted {len(pages)} pages from PDF")
        return pages


class PDFPlumberStrategy(DocumentExtractionStrategy):
    """Fallback PDF extraction using pdfplumber."""

    @property
    def name(self) -> str:
        return "pdfplumber"

    def supports_file(self, filename: str) -> bool:
        return filename.lower().endswith('.pdf')

    def extract_text_with_pages(self, file_path: str) -> List[Tuple[int, str]]:
        import pdfplumber

        pages = []
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages.append((page_num, page_text.strip()))

        logger.info(f"{self.name} extracted {len(pages)} pages from PDF")
        return pages


class PyPDF2Strategy(DocumentExtractionStrategy):
    """Fallback PDF extraction using PyPDF2."""

    @property
    def name(self) -> str:
        return "PyPDF2"

    def supports_file(self, filename: str) -> bool:
        return filename.lower().endswith('.pdf')

    def extract_text_with_pages(self, file_path: str) -> List[Tuple[int, str]]:
        import PyPDF2

        pages = []
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    pages.append((page_num, page_text.strip()))

        logger.info(f"{self.name} extracted {len(pages)} pages from PDF")
        return pages


class TextFileStrategy(DocumentExtractionStrategy):
    """Plain text file extraction (.txt)."""

    @property
    def name(self) -> str:
        return "TextFile"

    def supports_file(self, filename: str) -> bool:
        return filename.lower().endswith('.txt')

    def extract_text_with_pages(self, file_path: str) -> List[Tuple[int, str]]:
        """Extract text from plain text file. Treats entire file as one page."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        if text.strip():
            logger.info(f"{self.name} extracted text file (treated as 1 page)")
            return [(1, text.strip())]
        return []


class DocxStrategy(DocumentExtractionStrategy):
    """Word document extraction (.docx)."""

    @property
    def name(self) -> str:
        return "python-docx"

    def supports_file(self, filename: str) -> bool:
        return filename.lower().endswith('.docx')

    def extract_text_with_pages(self, file_path: str) -> List[Tuple[int, str]]:
        """Extract text from .docx file. Treats each section/page break as a page."""
        try:
            import docx
        except ImportError:
            raise ImportError("python-docx library not installed. Run: pip install python-docx")

        doc = docx.Document(file_path)

        # Extract all paragraphs
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)

        # Combine into single page (Word doesn't have fixed pages in .docx format)
        if paragraphs:
            combined_text = '\n\n'.join(paragraphs)
            logger.info(f"{self.name} extracted .docx document (treated as 1 page)")
            return [(1, combined_text)]

        return []


class RTFStrategy(DocumentExtractionStrategy):
    """RTF document extraction (.rtf)."""

    @property
    def name(self) -> str:
        return "striprtf"

    def supports_file(self, filename: str) -> bool:
        return filename.lower().endswith('.rtf')

    def extract_text_with_pages(self, file_path: str) -> List[Tuple[int, str]]:
        """Extract text from .rtf file."""
        try:
            from striprtf.striprtf import rtf_to_text
        except ImportError:
            raise ImportError("striprtf library not installed. Run: pip install striprtf")

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            rtf_content = f.read()

        text = rtf_to_text(rtf_content)

        if text.strip():
            logger.info(f"{self.name} extracted RTF document (treated as 1 page)")
            return [(1, text.strip())]

        return []


class DocumentExtractorService:
    """
    Service for extracting text from various document formats.
    Supports: PDF, TXT, DOCX, RTF
    Uses strategy pattern with automatic format detection and fallback.
    """

    def __init__(self):
        self.strategies = self._initialize_strategies()

    def _initialize_strategies(self) -> Dict[str, List[DocumentExtractionStrategy]]:
        """Initialize available extraction strategies organized by file type."""
        strategies = {
            'pdf': [],
            'text': [],
            'docx': [],
            'rtf': []
        }

        # PDF strategies (in order of preference)
        try:
            import fitz  # PyMuPDF
            strategies['pdf'].append(PyMuPDFStrategy())
            logger.debug("PyMuPDF strategy available")
        except ImportError:
            logger.debug("PyMuPDF not available")

        try:
            import pdfplumber
            strategies['pdf'].append(PDFPlumberStrategy())
            logger.debug("pdfplumber strategy available")
        except ImportError:
            logger.debug("pdfplumber not available")

        try:
            import PyPDF2
            strategies['pdf'].append(PyPDF2Strategy())
            logger.debug("PyPDF2 strategy available")
        except ImportError:
            logger.debug("PyPDF2 not available")

        # Text file strategy (always available)
        strategies['text'].append(TextFileStrategy())
        logger.debug("TextFile strategy available")

        # DOCX strategy
        try:
            import docx
            strategies['docx'].append(DocxStrategy())
            logger.debug("python-docx strategy available")
        except ImportError:
            logger.debug("python-docx not available")

        # RTF strategy
        try:
            from striprtf.striprtf import rtf_to_text
            strategies['rtf'].append(RTFStrategy())
            logger.debug("striprtf strategy available")
        except ImportError:
            logger.debug("striprtf not available")

        # Log available strategies
        available = []
        for file_type, strats in strategies.items():
            if strats:
                available.append(f"{file_type}: {[s.name for s in strats]}")

        logger.info(f"Initialized document extractor with strategies: {', '.join(available)}")
        return strategies

    def get_file_type(self, filename: str) -> Optional[str]:
        """Determine file type from filename."""
        ext = filename.lower().split('.')[-1]
        if ext == 'pdf':
            return 'pdf'
        elif ext == 'txt':
            return 'text'
        elif ext == 'docx':
            return 'docx'
        elif ext == 'rtf':
            return 'rtf'
        return None

    def is_supported(self, filename: str) -> bool:
        """Check if file type is supported."""
        file_type = self.get_file_type(filename)
        if not file_type:
            return False
        return file_type in self.strategies and len(self.strategies[file_type]) > 0

    def extract_text_with_pages(self, file_path: str, min_length: int = 50) -> List[Tuple[int, str]]:
        """
        Extract text from document using the best available method.

        Args:
            file_path: Path to document file
            min_length: Minimum acceptable text length per page

        Returns:
            List of tuples (page_number, cleaned_page_text)

        Raises:
            Exception: If file type unsupported or all extraction methods fail
        """
        filename = os.path.basename(file_path)
        file_type = self.get_file_type(filename)

        if not file_type:
            raise ValueError(f"Unsupported file type: {filename}. Supported: PDF, TXT, DOCX, RTF")

        if file_type not in self.strategies or not self.strategies[file_type]:
            raise ValueError(f"No extraction strategy available for {file_type.upper()} files")

        logger.info(f"Extracting text from {file_type.upper()}: {filename}")

        last_error = None
        for strategy in self.strategies[file_type]:
            try:
                pages = strategy.extract_text_with_pages(file_path)
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

        error_message = f"All extraction methods failed for {file_type.upper()}. Last error: {last_error}"
        logger.error(error_message)
        raise Exception(error_message)

    def extract_text_combined(self, file_path: str, min_length: int = 50) -> str:
        """
        Extract text and combine all pages with page markers.

        Args:
            file_path: Path to document file
            min_length: Minimum acceptable text length per page

        Returns:
            Combined text with <PDF pg #> markers (or <Page #> for other formats)

        Raises:
            Exception: If extraction fails
        """
        filename = os.path.basename(file_path)
        file_type = self.get_file_type(filename)
        pages = self.extract_text_with_pages(file_path, min_length)

        # Use appropriate marker based on file type
        page_marker = "<PDF pg {}>" if file_type == 'pdf' else "<Page {}>"

        combined_text = ""
        for page_num, page_text in pages:
            combined_text += f"\n\n{page_marker.format(page_num)}\n{page_text}"

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

    def get_available_libraries(self) -> Dict[str, List[str]]:
        """Return dictionary of available extraction libraries by file type."""
        return {
            file_type: [strategy.name for strategy in strats]
            for file_type, strats in self.strategies.items()
            if strats
        }

    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        supported = []
        if self.strategies.get('pdf'):
            supported.append('.pdf')
        if self.strategies.get('text'):
            supported.append('.txt')
        if self.strategies.get('docx'):
            supported.append('.docx')
        if self.strategies.get('rtf'):
            supported.append('.rtf')
        return supported
