"""
Layer 4: Smart Accumulation & Deduplication

Accumulates answers from multiple windows, performing intelligent deduplication
that preserves information while aggregating page citations.

CRITICAL RESPONSIBILITIES:
- Accumulate answers from all windows
- Detect duplicate/similar answers using semantic similarity
- Merge answers preserving ALL information
- Aggregate ALL PDF page citations across windows
- Track answer variants (different answers to the same question)
- Maintain answer quality through confidence tracking
"""

import logging
from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime
import re

from .models import (
    Answer,
    WindowResult,
    AnswerAccumulation,
    ConfidenceLevel
)

logger = logging.getLogger(__name__)


class SmartAccumulator:
    """
    Layer 4: Intelligently accumulates and deduplicates answers across windows.

    Design Principles:
    - Single Responsibility: Only handles answer accumulation and deduplication
    - Information Preservation: Never loses data, always merges
    - Semantic Understanding: Uses similarity, not exact matching

    CRITICAL: Preserves and aggregates ALL PDF page citations.
    """

    def __init__(self, similarity_threshold: float = 0.75):
        """
        Initialize the smart accumulator.

        Args:
            similarity_threshold: Minimum similarity (0.0-1.0) to consider answers duplicates
                                 Default 0.75 means 75% similar answers will be merged
        """
        self.similarity_threshold = similarity_threshold
        self.accumulation: AnswerAccumulation = defaultdict(list)  # question_id -> List[Answer]
        self.total_merges = 0
        self.total_variants = 0

    def accumulate_window(self, window_result: WindowResult) -> Dict[str, int]:
        """
        Accumulate answers from a single window into the global accumulation.

        Strategy:
        1. For each answer in the window
        2. Check if similar answer already exists for that question
        3. If similar: merge with existing answer
        4. If different: add as answer variant
        5. If first answer: add to accumulation

        Args:
            window_result: Results from processing a window

        Returns:
            Statistics dict with merge/variant counts
        """
        merges = 0
        variants = 0
        new_answers = 0

        logger.info(f"📥 Accumulating {len(window_result.answers)} answers from Window {window_result.window_num}")

        for question_id, new_answer in window_result.answers.items():
            existing_answers = self.accumulation[question_id]

            if not existing_answers:
                # First answer for this question
                self.accumulation[question_id].append(new_answer)
                new_answers += 1
                logger.debug(f"✨ {question_id}: First answer (pages: {new_answer.pages})")

            else:
                # Check similarity against all existing answers
                best_match, similarity = self._find_most_similar(new_answer, existing_answers)

                if similarity >= self.similarity_threshold:
                    # Merge with existing similar answer
                    best_match.merge_with(new_answer)
                    merges += 1
                    self.total_merges += 1
                    logger.debug(
                        f"🔄 {question_id}: Merged (similarity: {similarity:.2f}, "
                        f"pages now: {best_match.pages})"
                    )

                else:
                    # Different answer - add as variant
                    self.accumulation[question_id].append(new_answer)
                    variants += 1
                    self.total_variants += 1
                    logger.debug(
                        f"🔀 {question_id}: Added variant #{len(existing_answers) + 1} "
                        f"(similarity: {similarity:.2f}, pages: {new_answer.pages})"
                    )

        logger.info(
            f"✅ Window {window_result.window_num} accumulated: "
            f"{new_answers} new, {merges} merged, {variants} variants"
        )

        return {
            'window_num': window_result.window_num,
            'new_answers': new_answers,
            'merges': merges,
            'variants': variants
        }

    def _find_most_similar(
        self,
        new_answer: Answer,
        existing_answers: List[Answer]
    ) -> Tuple[Answer, float]:
        """
        Find the most similar answer from existing answers.

        Returns:
            Tuple of (most_similar_answer, similarity_score)
        """
        best_match = None
        best_similarity = 0.0

        for existing in existing_answers:
            similarity = self._calculate_similarity(new_answer.text, existing.text)

            if similarity > best_similarity:
                best_similarity = similarity
                best_match = existing

        return best_match, best_similarity

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate semantic similarity between two answer texts.

        Current implementation: Token-based Jaccard similarity
        Future enhancement: Use sentence embeddings for deeper semantic understanding

        Returns:
            Similarity score between 0.0 (completely different) and 1.0 (identical)
        """
        # Normalize texts for comparison
        norm1 = self._normalize_for_comparison(text1)
        norm2 = self._normalize_for_comparison(text2)

        # Exact match after normalization
        if norm1 == norm2:
            return 1.0

        # Tokenize into words
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())

        # Jaccard similarity: intersection / union
        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2

        return len(intersection) / len(union)

    def _normalize_for_comparison(self, text: str) -> str:
        """
        Normalize text for similarity comparison.

        CRITICAL: Unlike the frontend bug, we do NOT remove page numbers here!
        We only normalize for semantic comparison, preserving citation context.

        Strategy:
        - Lowercase for case-insensitive matching
        - Remove extra whitespace
        - Remove punctuation (but keep page citations intact)
        - Preserve semantic content
        """
        # Keep the <PDF pg X> markers for context, but normalize the rest
        normalized = text.lower()

        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)

        # Remove punctuation except for page citations
        # Keep angle brackets and numbers in page citations
        normalized = re.sub(r'[^\w\s<>]', ' ', normalized)

        # Clean up spacing
        normalized = ' '.join(normalized.split())

        return normalized.strip()

    def get_accumulated_answers(self) -> AnswerAccumulation:
        """
        Get all accumulated answers.

        Returns:
            Dict mapping question_id -> List[Answer] (sorted by confidence)
        """
        # Sort each question's answers by confidence (highest first)
        sorted_accumulation = {}

        for question_id, answers in self.accumulation.items():
            sorted_answers = sorted(answers, key=lambda a: a.confidence, reverse=True)
            sorted_accumulation[question_id] = sorted_answers

        return sorted_accumulation

    def get_primary_answers(self) -> Dict[str, Answer]:
        """
        Get the primary (highest confidence) answer for each question.

        Returns:
            Dict mapping question_id -> Answer (highest confidence)
        """
        primary = {}

        for question_id, answers in self.accumulation.items():
            if answers:
                # Sort by confidence and take the highest
                best_answer = max(answers, key=lambda a: a.confidence)
                primary[question_id] = best_answer

        return primary

    def get_answer_variants(self, question_id: str) -> List[Answer]:
        """
        Get all answer variants for a specific question.

        Returns:
            List of answers sorted by confidence (highest first)
        """
        answers = self.accumulation.get(question_id, [])
        return sorted(answers, key=lambda a: a.confidence, reverse=True)

    def get_statistics(self) -> Dict:
        """
        Get accumulation statistics for monitoring.

        Returns:
            Dict with detailed stats about the accumulation process
        """
        total_questions = len(self.accumulation)
        total_answers = sum(len(answers) for answers in self.accumulation.values())
        questions_with_variants = sum(1 for answers in self.accumulation.values() if len(answers) > 1)

        # Confidence distribution
        all_answers = [a for answers in self.accumulation.values() for a in answers]
        if all_answers:
            avg_confidence = sum(a.confidence for a in all_answers) / len(all_answers)
            high_confidence = sum(1 for a in all_answers if a.get_confidence_level() == ConfidenceLevel.HIGH)
            medium_confidence = sum(1 for a in all_answers if a.get_confidence_level() == ConfidenceLevel.MEDIUM)
            low_confidence = sum(1 for a in all_answers if a.get_confidence_level() == ConfidenceLevel.LOW)
        else:
            avg_confidence = 0.0
            high_confidence = medium_confidence = low_confidence = 0

        # Page citation coverage
        all_pages = set()
        for answers in self.accumulation.values():
            for answer in answers:
                all_pages.update(answer.pages)

        return {
            'total_questions': total_questions,
            'total_answers': total_answers,
            'questions_with_variants': questions_with_variants,
            'total_merges': self.total_merges,
            'total_variants': self.total_variants,
            'avg_confidence': avg_confidence,
            'confidence_distribution': {
                'high': high_confidence,
                'medium': medium_confidence,
                'low': low_confidence
            },
            'unique_pages_cited': len(all_pages),
            'page_range': f"{min(all_pages)}-{max(all_pages)}" if all_pages else "N/A"
        }

    def generate_report(self) -> str:
        """
        Generate a human-readable report of the accumulation process.

        Returns:
            Formatted string with accumulation summary
        """
        stats = self.get_statistics()

        report = f"""
╔══════════════════════════════════════════════════════════════╗
║          SMART ACCUMULATION REPORT                           ║
╚══════════════════════════════════════════════════════════════╝

Questions Analyzed: {stats['total_questions']}
Total Answers: {stats['total_answers']}
Questions with Variants: {stats['questions_with_variants']}

Accumulation Operations:
  • Merges: {stats['total_merges']}
  • Variants: {stats['total_variants']}

Confidence Distribution:
  • High (≥0.7): {stats['confidence_distribution']['high']}
  • Medium (0.4-0.7): {stats['confidence_distribution']['medium']}
  • Low (<0.4): {stats['confidence_distribution']['low']}
  • Average: {stats['avg_confidence']:.2f}

Page Citation Coverage:
  • Unique pages cited: {stats['unique_pages_cited']}
  • Page range: {stats['page_range']}

        """

        # Add variant details for questions with multiple answers
        variant_questions = [
            (qid, answers) for qid, answers in self.accumulation.items()
            if len(answers) > 1
        ]

        if variant_questions:
            report += "\nQuestions with Multiple Answers:\n"
            for qid, answers in variant_questions[:5]:  # Show first 5
                report += f"\n  {qid}: {len(answers)} variants\n"
                for i, answer in enumerate(answers, 1):
                    report += (
                        f"    #{i} - Confidence: {answer.confidence:.2f}, "
                        f"Pages: {answer.pages}, Windows: {answer.windows}\n"
                    )

            if len(variant_questions) > 5:
                report += f"\n  ... and {len(variant_questions) - 5} more\n"

        return report
