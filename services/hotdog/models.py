"""
Data models for HOTDOG AI system.

Following Clean Code principles:
- Value Objects: Immutable, defined by attributes
- Entities: Mutable, defined by identity
- Clear, meaningful names that reveal intent
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


class ConfidenceLevel(Enum):
    """Confidence classification for answers."""
    HIGH = "high"  # ≥ 0.7
    MEDIUM = "medium"  # 0.4 - 0.7
    LOW = "low"  # < 0.4
    PENDING = "pending"  # Not yet analyzed


@dataclass(frozen=True)
class PageData:
    """
    Value Object representing a single PDF page with extracted text.

    Immutable to ensure page numbers and text are never corrupted.
    """
    page_num: int  # 1-indexed for user display
    text: str
    char_count: int
    has_content: bool

    def __post_init__(self):
        """Validate page data on creation."""
        if self.page_num < 1:
            raise ValueError(f"Page number must be ≥ 1, got {self.page_num}")
        if not isinstance(self.text, str):
            raise ValueError("Page text must be a string")


@dataclass(frozen=True)
class Question:
    """
    Value Object representing a single analysis question.

    Immutable to prevent accidental modification of question text.
    """
    id: str  # e.g., "Q1", "Q28"
    text: str  # The question to answer
    section_id: str  # Which section this belongs to
    required: bool = True
    expected_type: str = "string"  # "string", "number", "date", "technical_spec"

    def __post_init__(self):
        """Validate question data."""
        if not self.id or not self.text:
            raise ValueError("Question ID and text are required")


@dataclass
class Section:
    """
    Entity representing a question section/category.

    Mutable because we may update the expert or questions list.
    """
    id: str  # e.g., "general_info", "materials"
    name: str  # e.g., "General Project Information"
    description: str
    questions: List[Question] = field(default_factory=list)
    expert_persona: Optional['ExpertPersona'] = None  # Assigned by Layer 2

    def add_question(self, question: Question):
        """Add a question to this section."""
        if question.section_id != self.id:
            raise ValueError(f"Question {question.id} belongs to section {question.section_id}, not {self.id}")
        self.questions.append(question)

    def question_count(self) -> int:
        """Get number of questions in this section."""
        return len(self.questions)


@dataclass(frozen=True)
class ExpertPersona:
    """
    Value Object representing an AI expert persona.

    Generated dynamically from section metadata, then cached.
    Immutable to ensure persona consistency across analysis.
    """
    id: str
    name: str  # e.g., "CIPP Materials & Standards Specialist"
    section_id: str
    section_name: str
    specialization: str  # 2-3 sentence description of expertise
    system_prompt: str  # Detailed instructions for this expert
    citation_strategy: str  # How to extract and include page citations
    answer_format: str  # Expected structure of responses
    created_at: datetime = field(default_factory=datetime.now)
    cache_key: Optional[str] = None

    def __post_init__(self):
        """Validate expert persona data."""
        required_fields = ['id', 'name', 'section_id', 'system_prompt']
        for field_name in required_fields:
            if not getattr(self, field_name):
                raise ValueError(f"ExpertPersona missing required field: {field_name}")


@dataclass
class Answer:
    """
    Entity representing an answer to a question.

    Mutable to allow accumulation and merging of information.
    CRITICAL: pages array is mandatory, never empty.
    """
    question_id: str
    text: str  # The answer text with <PDF pg X> citation
    pages: List[int]  # MANDATORY: PDF page numbers (never empty)
    confidence: float  # 0.0 - 1.0
    expert: str  # Which expert provided this answer
    window: int  # Which 3-page window this came from
    footnote: str = ""  # Contextual footnote with PDF page + section ref + bidding context
    windows: List[int] = field(default_factory=list)  # All windows that contributed
    merge_count: int = 0  # How many times merged
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate answer data - CRITICAL for page citations."""
        if not self.pages:
            raise ValueError(f"Answer for {self.question_id} missing page citations - this is MANDATORY")
        if not all(isinstance(p, int) and p > 0 for p in self.pages):
            raise ValueError(f"Invalid page numbers in {self.question_id}: {self.pages}")
        if '<PDF pg' not in self.text:
            raise ValueError(f"Answer text for {self.question_id} missing <PDF pg X> citation marker")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")

        # Initialize windows list if not provided
        if not self.windows and self.window:
            self.windows = [self.window]

    def get_confidence_level(self) -> ConfidenceLevel:
        """Classify confidence into High/Medium/Low."""
        if self.confidence >= 0.7:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def merge_with(self, other: 'Answer'):
        """
        Merge another answer into this one.

        Strategy:
        - Combine unique information (keep more specific)
        - Aggregate all page citations
        - Use highest confidence
        - Track merge history
        """
        if self.question_id != other.question_id:
            raise ValueError(f"Cannot merge answers for different questions: {self.question_id} vs {other.question_id}")

        # Determine which text is more specific (longer, more detail)
        if len(other.text) > len(self.text) * 1.2:
            # Other answer is significantly more detailed
            base_text = other.text
            supplemental = self.text
        else:
            base_text = self.text
            supplemental = other.text

        # Merge texts (simplified - production would use NLP)
        # For now, just use the more detailed version
        self.text = base_text

        # Aggregate page citations (remove duplicates, sort)
        all_pages = sorted(set(self.pages + other.pages))
        self.pages = all_pages

        # Update citation markers in text
        pages_str = ', '.join(map(str, all_pages))
        # Replace old citation with new aggregated one
        import re
        self.text = re.sub(r'<PDF pg [0-9, ]+>', f'<PDF pg {pages_str}>', self.text)

        # Use highest confidence
        self.confidence = max(self.confidence, other.confidence)

        # Merge footnotes (keep both if different)
        if other.footnote and other.footnote != self.footnote:
            if self.footnote:
                self.footnote = f"{self.footnote} | {other.footnote}"
            else:
                self.footnote = other.footnote

        # Track merge history
        self.windows = sorted(set(self.windows + other.windows))
        self.merge_count += 1
        self.updated_at = datetime.now()


@dataclass
class WindowContext:
    """
    Value Object representing a 3-page window for processing.

    Immutable to ensure window boundaries don't shift during processing.
    """
    window_num: int
    pages: List[int]  # e.g., [13, 14, 15]
    text: str  # Combined text from all pages in window
    page_data: List[PageData]  # Original page data for reference

    @property
    def page_range_str(self) -> str:
        """Get human-readable page range."""
        return f"{min(self.pages)}-{max(self.pages)}"


@dataclass
class WindowResult:
    """
    Result from processing a single 3-page window.

    Contains all answers found in this window.
    """
    window_num: int
    pages: List[int]
    answers: Dict[str, Answer]  # question_id -> Answer
    tokens_used: int
    processing_time: float  # seconds
    expert_count: int
    errors: List[str] = field(default_factory=list)


@dataclass
class ParsedConfig:
    """
    Parsed question configuration.

    Result of loading from JSON/DB.
    """
    name: str
    version: str
    sections: List[Section]
    section_map: Dict[str, Section]  # section_id -> Section
    question_map: Dict[str, Question]  # question_id -> Question
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_questions(self) -> int:
        """Get total number of questions across all sections."""
        return len(self.question_map)

    @property
    def total_sections(self) -> int:
        """Get total number of sections."""
        return len(self.sections)


@dataclass
class AnalysisResult:
    """
    Final result of complete document analysis.

    Contains all accumulated answers, footnotes, and metadata.
    """
    document_name: str
    total_pages: int
    pages_analyzed: int
    questions: Dict[str, List[Answer]]  # question_id -> List[Answer] (primary + variants)
    footnotes: List[str]
    metadata: Dict[str, Any]
    started_at: datetime
    completed_at: datetime
    total_tokens: int
    estimated_cost: float

    @property
    def processing_time_seconds(self) -> float:
        """Calculate total processing time."""
        delta = self.completed_at - self.started_at
        return delta.total_seconds()

    @property
    def questions_answered(self) -> int:
        """Count questions with at least one answer."""
        return len([q for q in self.questions.values() if q])

    @property
    def average_confidence(self) -> float:
        """Calculate average confidence across all primary answers."""
        confidences = []
        for answers in self.questions.values():
            if answers:
                confidences.append(answers[0].confidence)  # Primary answer

        return sum(confidences) / len(confidences) if confidences else 0.0


# Type aliases for clarity
ExpertPersonaCache = Dict[str, ExpertPersona]  # cache_key -> ExpertPersona
AnswerAccumulation = Dict[str, List[Answer]]  # question_id -> List[Answer]
