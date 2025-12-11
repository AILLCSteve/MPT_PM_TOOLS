"""
Layer 6: Output Compilation & Export

Compiles accumulated answers into user-facing formats including browser display,
Excel exports, and PDF reports. Ensures perfect page citation formatting.

CRITICAL RESPONSIBILITIES:
- Compile final analysis results
- Format for browser display (HTML with confidence badges)
- Generate Excel exports (multiple sheets, formatted)
- Create footnote compilation
- Render confidence indicators
- Preserve PDF page citations in all formats
"""

import logging
from typing import Dict, List, Any
from datetime import datetime
import re

from .models import (
    AnalysisResult,
    Answer,
    AnswerAccumulation,
    ConfidenceLevel,
    ParsedConfig
)

logger = logging.getLogger(__name__)


class OutputCompiler:
    """
    Layer 6: Compiles analysis results into multiple output formats.

    Design Principles:
    - Single Responsibility: Only handles output formatting
    - Open/Closed: Extensible for new output formats
    - Format-agnostic internal representation

    CRITICAL: Preserves PDF page citations in ALL output formats.
    """

    def __init__(self):
        """Initialize the output compiler."""
        self.footnotes_compiled = []
        self.export_metadata = {}

    def compile_results(
        self,
        accumulation: AnswerAccumulation,
        config: ParsedConfig,
        metadata: Dict[str, Any],
        started_at: datetime,
        completed_at: datetime,
        total_tokens: int
    ) -> AnalysisResult:
        """
        Compile accumulated answers into final AnalysisResult.

        Args:
            accumulation: All accumulated answers (question_id -> List[Answer])
            config: The question configuration used
            metadata: Document metadata (filename, page count, etc.)
            started_at: Analysis start time
            completed_at: Analysis completion time
            total_tokens: Total tokens used

        Returns:
            Complete AnalysisResult ready for export
        """
        logger.info("📋 Compiling final analysis results...")

        # Compile footnotes from all answers
        footnotes = self._compile_footnotes(accumulation)

        # Calculate cost estimate
        estimated_cost = total_tokens * 0.00003  # ~$0.03 per 1K tokens for GPT-4

        result = AnalysisResult(
            document_name=metadata.get('file_name', 'Unknown'),
            total_pages=metadata.get('total_pages', 0),
            pages_analyzed=metadata.get('total_pages', 0),
            questions=accumulation,
            footnotes=footnotes,
            metadata=metadata,
            started_at=started_at,
            completed_at=completed_at,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost
        )

        logger.info(
            f"✅ Compilation complete: {result.questions_answered}/{config.total_questions} questions, "
            f"{len(footnotes)} footnotes, {result.processing_time_seconds:.2f}s"
        )

        return result

    def _compile_footnotes(self, accumulation: AnswerAccumulation) -> List[str]:
        """
        Compile all unique footnotes from answers.

        Extracts all <PDF pg X> citations and creates numbered footnote list.

        Returns:
            List of footnote strings with page citations
        """
        footnotes = []
        seen_citations = set()

        # Sort by question_id for consistent ordering
        for question_id in sorted(accumulation.keys()):
            answers = accumulation[question_id]

            for answer in answers:
                # Extract all page citations from this answer
                citations = self._extract_citations(answer.text)

                for citation in citations:
                    if citation not in seen_citations:
                        footnotes.append(citation)
                        seen_citations.add(citation)

        logger.info(f"📝 Compiled {len(footnotes)} unique footnotes")
        return footnotes

    def _extract_citations(self, text: str) -> List[str]:
        """
        Extract all <PDF pg X> citations from answer text.

        Returns:
            List of citation strings (e.g., ["Information from page 5", "Data from pages 7, 8"])
        """
        citations = []

        # Pattern: <PDF pg X> or <PDF pg X, Y, Z>
        pattern = r'<PDF pg ([0-9, ]+)>'
        matches = re.finditer(pattern, text)

        for match in matches:
            pages_str = match.group(1)
            page_list = [p.strip() for p in pages_str.split(',')]

            if len(page_list) == 1:
                citation = f"Information from page {page_list[0]}"
            else:
                citation = f"Information from pages {', '.join(page_list)}"

            citations.append(citation)

        return citations

    def format_for_browser(self, result: AnalysisResult, config: ParsedConfig) -> Dict:
        """
        Format analysis result for browser display.

        Returns JSON structure with:
        - Answers grouped by section
        - Confidence badges
        - Page citations prominently displayed
        - Answer variants

        Returns:
            Dict ready to serialize to JSON for frontend
        """
        logger.info("🌐 Formatting results for browser display...")

        sections = []

        for section in config.sections:
            section_data = {
                'section_id': section.id,
                'section_name': section.name,
                'description': section.description,
                'questions': []
            }

            for question in section.questions:
                answers_list = result.questions.get(question.id, [])

                # Primary answer (highest confidence)
                primary_answer = answers_list[0] if answers_list else None

                # Variants (additional answers)
                variants = answers_list[1:] if len(answers_list) > 1 else []

                question_data = {
                    'question_id': question.id,
                    'question_text': question.text,
                    'has_answer': primary_answer is not None,
                    'primary_answer': self._format_answer_for_browser(primary_answer) if primary_answer else None,
                    'variants': [self._format_answer_for_browser(v) for v in variants],
                    'variant_count': len(variants)
                }

                section_data['questions'].append(question_data)

            sections.append(section_data)

        return {
            'document_name': result.document_name,
            'total_pages': result.total_pages,
            'questions_answered': result.questions_answered,
            'total_questions': config.total_questions,
            'average_confidence': result.average_confidence,
            'processing_time': result.processing_time_seconds,
            'sections': sections,
            'footnotes': result.footnotes,
            'metadata': {
                'started_at': result.started_at.isoformat(),
                'completed_at': result.completed_at.isoformat(),
                'total_tokens': result.total_tokens,
                'estimated_cost': f"${result.estimated_cost:.4f}"
            }
        }

    def _format_answer_for_browser(self, answer: Answer) -> Dict:
        """
        Format a single answer for browser display.

        Returns:
            Dict with answer text, pages, confidence badge, etc.
        """
        confidence_level = answer.get_confidence_level()

        # Badge color based on confidence
        badge_colors = {
            ConfidenceLevel.HIGH: '#22c55e',    # Green
            ConfidenceLevel.MEDIUM: '#eab308',  # Yellow
            ConfidenceLevel.LOW: '#ef4444'      # Red
        }

        return {
            'text': answer.text,
            'pages': answer.pages,
            'confidence': answer.confidence,
            'confidence_level': confidence_level.value,
            'confidence_badge': {
                'label': f"{int(answer.confidence * 100)}%",
                'color': badge_colors[confidence_level],
                'level': confidence_level.value
            },
            'expert': answer.expert,
            'windows': answer.windows,
            'merge_count': answer.merge_count,
            'footnote': answer.footnote  # Include footnote for browser display
        }

    def format_for_excel(self, result: AnalysisResult, config: ParsedConfig) -> Dict:
        """
        Format analysis result for Excel export.

        Creates multiple sheets:
        1. Summary - Overview statistics
        2. Answers - All questions and answers with metadata
        3. Footnotes - All page citations
        4. Variants - Alternative answers

        Returns:
            Dict with sheet data ready for openpyxl or similar
        """
        logger.info("📊 Formatting results for Excel export...")

        # Sheet 1: Summary
        summary_data = {
            'title': 'Analysis Summary',
            'rows': [
                ['Document', result.document_name],
                ['Total Pages', result.total_pages],
                ['Questions Answered', f"{result.questions_answered}/{config.total_questions}"],
                ['Average Confidence', f"{result.average_confidence:.2%}"],
                ['Processing Time', f"{result.processing_time_seconds:.2f}s"],
                ['Total Tokens', result.total_tokens],
                ['Estimated Cost', f"${result.estimated_cost:.4f}"],
                ['Started', result.started_at.strftime('%Y-%m-%d %H:%M:%S')],
                ['Completed', result.completed_at.strftime('%Y-%m-%d %H:%M:%S')]
            ]
        }

        # Sheet 2: Answers
        answers_rows = [['Section', 'Question ID', 'Question', 'Answer', 'Pages', 'Confidence', 'Expert']]

        for section in config.sections:
            for question in section.questions:
                answers_list = result.questions.get(question.id, [])
                primary_answer = answers_list[0] if answers_list else None

                if primary_answer:
                    pages_str = ', '.join(map(str, primary_answer.pages))
                    # Remove <PDF pg X> markers from Excel export text (redundant with Pages column)
                    clean_text = re.sub(r'\s*<PDF pg [0-9, ]+>', '', primary_answer.text)

                    answers_rows.append([
                        section.name,
                        question.id,
                        question.text,
                        clean_text,
                        pages_str,
                        f"{primary_answer.confidence:.2%}",
                        primary_answer.expert
                    ])
                else:
                    answers_rows.append([
                        section.name,
                        question.id,
                        question.text,
                        'NOT FOUND',
                        '',
                        '',
                        ''
                    ])

        answers_data = {
            'title': 'Answers',
            'rows': answers_rows
        }

        # Sheet 3: Footnotes
        footnotes_rows = [['#', 'Citation']]
        for i, footnote in enumerate(result.footnotes, 1):
            footnotes_rows.append([i, footnote])

        footnotes_data = {
            'title': 'Footnotes',
            'rows': footnotes_rows
        }

        # Sheet 4: Variants (if any)
        variants_rows = [['Question ID', 'Variant #', 'Answer', 'Pages', 'Confidence', 'Expert']]

        for question_id in sorted(result.questions.keys()):
            answers_list = result.questions[question_id]
            if len(answers_list) > 1:
                for i, variant in enumerate(answers_list[1:], 2):  # Start at 2 (variant 2, 3, etc.)
                    pages_str = ', '.join(map(str, variant.pages))
                    clean_text = re.sub(r'\s*<PDF pg [0-9, ]+>', '', variant.text)

                    variants_rows.append([
                        question_id,
                        i,
                        clean_text,
                        pages_str,
                        f"{variant.confidence:.2%}",
                        variant.expert
                    ])

        variants_data = {
            'title': 'Answer Variants',
            'rows': variants_rows
        }

        return {
            'sheets': [summary_data, answers_data, footnotes_data, variants_data],
            'filename': f"{result.document_name.replace('.pdf', '')}_analysis.xlsx"
        }

    def generate_text_report(self, result: AnalysisResult, config: ParsedConfig) -> str:
        """
        Generate a human-readable text report.

        Returns:
            Formatted string with complete analysis summary
        """
        lines = []

        lines.append("╔══════════════════════════════════════════════════════════════╗")
        lines.append("║          HOTDOG AI DOCUMENT ANALYSIS REPORT                  ║")
        lines.append("╚══════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"Document: {result.document_name}")
        lines.append(f"Pages: {result.total_pages}")
        lines.append(f"Analysis Date: {result.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Processing Time: {result.processing_time_seconds:.2f} seconds")
        lines.append("")
        lines.append("=" * 64)
        lines.append("")

        # Questions and answers by section
        for section in config.sections:
            lines.append(f"\n{section.name.upper()}")
            lines.append("-" * 64)

            for question in section.questions:
                lines.append(f"\n{question.id}: {question.text}")

                answers_list = result.questions.get(question.id, [])
                primary_answer = answers_list[0] if answers_list else None

                if primary_answer:
                    confidence_emoji = self._get_confidence_emoji(primary_answer.get_confidence_level())
                    pages_str = ', '.join(map(str, primary_answer.pages))

                    lines.append(f"  {confidence_emoji} Answer (Confidence: {primary_answer.confidence:.0%}):")
                    lines.append(f"  {primary_answer.text}")
                    lines.append(f"  Pages: {pages_str}")

                    if len(answers_list) > 1:
                        lines.append(f"  (+{len(answers_list) - 1} variant(s) available)")
                else:
                    lines.append("  ❌ No answer found")

                lines.append("")

        # Footer statistics
        lines.append("=" * 64)
        lines.append("")
        lines.append("STATISTICS")
        lines.append(f"  Questions Answered: {result.questions_answered}/{config.total_questions}")
        lines.append(f"  Average Confidence: {result.average_confidence:.0%}")
        lines.append(f"  Total Footnotes: {len(result.footnotes)}")
        lines.append(f"  Tokens Used: {result.total_tokens:,}")
        lines.append(f"  Estimated Cost: ${result.estimated_cost:.4f}")
        lines.append("")

        return "\n".join(lines)

    def _get_confidence_emoji(self, level: ConfidenceLevel) -> str:
        """Get emoji for confidence level."""
        emojis = {
            ConfidenceLevel.HIGH: "✅",
            ConfidenceLevel.MEDIUM: "⚠️",
            ConfidenceLevel.LOW: "❓",
            ConfidenceLevel.PENDING: "⏳"
        }
        return emojis.get(level, "❓")
