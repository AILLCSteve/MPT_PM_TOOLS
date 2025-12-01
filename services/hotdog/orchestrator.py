"""
HOTDOG AI Orchestrator
Hierarchical Orchestrated Thorough Document Oversight & Guidance

Main coordinator that orchestrates all 6 layers to perform complete document analysis.

ARCHITECTURE:
Layer 0: Document Ingestion - PDF extraction
Layer 1: Configuration Loader - Question loading
Layer 2: Expert Persona Generator - Dynamic expert creation
Layer 3: Multi-Expert Processor - Parallel AI execution
Layer 4: Smart Accumulator - Answer deduplication
Layer 5: Token Budget Manager - Token tracking
Layer 6: Output Compiler - Export formatting

CRITICAL FEATURES:
- Dynamic expert generation from section headings
- Perfect PDF page citation preservation
- Smart deduplication with information merging
- Exhaustive coverage within token limits
- Flexible question configuration
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
from openai import AsyncOpenAI

from .layers import (
    DocumentIngestionLayer,
    ConfigurationLoader,
    ExpertPersonaGenerator,
    TokenBudgetManager
)
from .multi_expert_processor import MultiExpertProcessor
from .smart_accumulator import SmartAccumulator
from .output_compiler import OutputCompiler
from .second_pass_processor import SecondPassProcessor
from .token_optimizer import TokenOptimizer
from .models import (
    AnalysisResult,
    ParsedConfig,
    ExpertPersona,
    WindowContext,
    Question,
    AnswerAccumulation
)

logger = logging.getLogger(__name__)


class HotdogOrchestrator:
    """
    Main orchestrator for HOTDOG AI document analysis.

    Coordinates all 6 layers to perform thorough, exhaustive document analysis
    with perfect page citation preservation.

    Design Principles:
    - Dependency Inversion: Depends on layer abstractions, not implementations
    - Single Responsibility: Only handles coordination, not implementation
    - Open/Closed: Extensible through layer replacement
    """

    def __init__(
        self,
        openai_api_key: str,
        config_path: Optional[str] = None,
        max_parallel_experts: int = 5,
        similarity_threshold: float = 0.75,
        progress_callback: Optional[Callable] = None,
        context_guardrails: Optional[str] = None
    ):
        """
        Initialize the HOTDOG orchestrator.

        Args:
            openai_api_key: OpenAI API key for GPT-4 calls
            config_path: Path to question configuration JSON (optional)
            max_parallel_experts: Maximum concurrent expert API calls
            similarity_threshold: Similarity threshold for answer merging (0.0-1.0)
            progress_callback: Optional callback for progress updates
                              Signature: callback(event_type: str, data: dict)
            context_guardrails: Optional global context rules for analysis
                              (e.g., "Only answer within CIPP lining context")
        """
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.config_path = config_path
        self.progress_callback = progress_callback
        self.context_guardrails = context_guardrails or ""

        # Detect model limits using TokenOptimizer
        self.model = "gpt-4o"  # Most robust available model
        model_limits = TokenOptimizer.detect_model_limits(self.model)

        # Initialize all layers with optimized token limits
        self.layer0_ingestion = DocumentIngestionLayer()
        self.layer1_config = ConfigurationLoader()
        self.layer2_experts = ExpertPersonaGenerator(
            openai_client=self.openai_client,
            model=self.model
        )
        self.layer3_processor = MultiExpertProcessor(
            openai_client=self.openai_client,
            max_parallel_experts=max_parallel_experts,
            model=self.model,
            max_completion_tokens=model_limits.recommended_completion_tokens
        )
        self.layer3_5_second_pass = SecondPassProcessor(
            openai_client=self.openai_client,
            max_parallel_experts=max_parallel_experts,
            context_guardrails=self.context_guardrails,
            model=self.model,
            max_completion_tokens=model_limits.recommended_completion_tokens
        )
        self.layer4_accumulator = SmartAccumulator(
            similarity_threshold=similarity_threshold
        )
        self.layer5_token_manager = TokenBudgetManager(
            max_prompt_tokens=model_limits.recommended_prompt_tokens,  # 75K for GPT-4o
            max_completion_tokens=model_limits.recommended_completion_tokens  # 16K for GPT-4o
        )
        self.layer6_compiler = OutputCompiler()

        # Store windows and experts for second pass
        self.cached_windows = []
        self.cached_experts = {}
        self.cached_config = None

        logger.info("🔥 HOTDOG AI Orchestrator initialized")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Prompt Budget: {model_limits.recommended_prompt_tokens:,} tokens (18.75x improvement!)")
        logger.info(f"   Completion Limit: {model_limits.recommended_completion_tokens:,} tokens")
        if self.context_guardrails:
            logger.info(f"📋 Context Guardrails: {self.context_guardrails[:100]}...")

    async def analyze_document(
        self,
        pdf_path: str,
        config_path: Optional[str] = None
    ) -> AnalysisResult:
        """
        Perform complete document analysis.

        This is the main entry point that coordinates all layers.

        Args:
            pdf_path: Path to PDF document to analyze
            config_path: Path to question configuration (overrides default)

        Returns:
            Complete AnalysisResult with all answers and metadata

        Raises:
            ValueError: If PDF or config not found
            RuntimeError: If analysis fails critically
        """
        started_at = datetime.now()
        logger.info(f"🚀 Starting HOTDOG analysis: {pdf_path}")
        self._emit_progress('analysis_started', {'pdf_path': pdf_path, 'started_at': started_at})

        try:
            # ============================================================
            # LAYER 0: DOCUMENT INGESTION
            # ============================================================
            logger.info("📄 Layer 0: Document Ingestion")
            self._emit_progress('layer_0_start', {'layer': 'Document Ingestion'})

            pages, doc_metadata = self.layer0_ingestion.extract_pdf(pdf_path)
            windows = self.layer0_ingestion.create_windows(pages, window_size=3)

            logger.info(f"  ✅ Extracted {len(pages)} pages into {len(windows)} windows")
            self._emit_progress('layer_0_complete', {
                'total_pages': len(pages),
                'total_windows': len(windows)
            })

            # Cache windows for potential second pass
            self.cached_windows = windows

            # ============================================================
            # LAYER 1: CONFIGURATION LOADING
            # ============================================================
            logger.info("⚙️  Layer 1: Configuration Loading")
            self._emit_progress('layer_1_start', {'layer': 'Configuration Loading'})

            config_file = config_path or self.config_path
            if not config_file:
                raise ValueError("No configuration file provided")

            config = self.layer1_config.load_from_json(config_file)

            logger.info(f"  ✅ Loaded {config.total_questions} questions in {config.total_sections} sections")
            self._emit_progress('layer_1_complete', {
                'total_questions': config.total_questions,
                'total_sections': config.total_sections,
                'sections': [s.name for s in config.sections]
            })

            # Cache config for potential second pass
            self.cached_config = config

            # ============================================================
            # LAYER 2: EXPERT PERSONA GENERATION
            # ============================================================
            logger.info("🤖 Layer 2: Expert Persona Generation")
            self._emit_progress('layer_2_start', {'layer': 'Expert Persona Generation'})

            experts = {}  # section_id -> ExpertPersona
            for section in config.sections:
                expert = await self.layer2_experts.generate_expert(section)
                experts[section.id] = expert
                logger.info(f"  ✅ Generated expert: {expert.name}")

            self._emit_progress('layer_2_complete', {
                'experts_generated': len(experts),
                'expert_names': [e.name for e in experts.values()]
            })

            # Cache experts for potential second pass
            self.cached_experts = experts

            # ============================================================
            # LAYERS 3, 4, 5: WINDOW PROCESSING LOOP
            # ============================================================
            logger.info(f"🔄 Processing {len(windows)} windows...")
            self._emit_progress('processing_start', {'total_windows': len(windows)})

            for window_idx, window in enumerate(windows, 1):
                logger.info(f"\n{'='*64}")
                logger.info(f"Window {window_idx}/{len(windows)}: Pages {window.page_range_str}")
                logger.info(f"{'='*64}")

                self._emit_progress('window_start', {
                    'window_num': window_idx,
                    'total_windows': len(windows),
                    'pages': window.pages
                })

                # -----------------------------------------------------
                # LAYER 5: Token Budget Check (before processing)
                # -----------------------------------------------------
                adjusted_context, within_budget = self.layer5_token_manager.check_budget_before_window(
                    window_num=window_idx,
                    context_text=window.text,
                    question_count=config.total_questions
                )

                if adjusted_context != window.text:
                    logger.warning(f"⚠️  Context truncated for token budget")
                    # Create adjusted window
                    window = WindowContext(
                        window_num=window.window_num,
                        pages=window.pages,
                        text=adjusted_context,
                        page_data=window.page_data
                    )

                # -----------------------------------------------------
                # LAYER 3: Multi-Expert Processing
                # -----------------------------------------------------
                window_result = await self.layer3_processor.process_window(
                    window=window,
                    questions=list(config.question_map.values()),
                    experts=experts
                )

                # Record actual token usage
                self.layer5_token_manager.record_usage(
                    window_num=window_idx,
                    prompt_tokens=window_result.tokens_used // 2,  # Rough split
                    completion_tokens=window_result.tokens_used // 2
                )

                # -----------------------------------------------------
                # LAYER 4: Smart Accumulation
                # -----------------------------------------------------
                accumulation_stats = self.layer4_accumulator.accumulate_window(window_result)

                # Get current accumulated answers for live display
                accumulated_so_far = self.layer4_accumulator.get_accumulated_answers()

                # Format unitary log for live display (answers found so far)
                unitary_log_markdown = self._format_live_unitary_log(
                    accumulated_so_far, config, window_idx, len(windows)
                )

                self._emit_progress('window_complete', {
                    'window_num': window_idx,
                    'answers_found': len(window_result.answers),
                    'tokens_used': window_result.tokens_used,
                    'processing_time': window_result.processing_time,
                    'accumulation_stats': accumulation_stats,
                    'unitary_log_markdown': unitary_log_markdown  # LIVE UNITARY LOG
                })

                # Progress update every 3 windows
                if window_idx % 3 == 0:
                    progress_summary = f"{window_idx}/{len(windows)} windows processed"
                    logger.info(f"\n📊 Progress: {progress_summary}")
                    logger.info(self.layer5_token_manager.get_statistics())
                    logger.info(self.layer4_accumulator.get_statistics())

                    self._emit_progress('progress_milestone', {
                        'windows_processed': window_idx,
                        'total_windows': len(windows),
                        'progress_summary': progress_summary
                    })

            # ============================================================
            # LAYER 6: OUTPUT COMPILATION
            # ============================================================
            logger.info("\n📋 Layer 6: Output Compilation")
            self._emit_progress('layer_6_start', {'layer': 'Output Compilation'})

            completed_at = datetime.now()
            accumulated_answers = self.layer4_accumulator.get_accumulated_answers()
            total_tokens = self.layer5_token_manager.total_tokens_used

            result = self.layer6_compiler.compile_results(
                accumulation=accumulated_answers,
                config=config,
                metadata=doc_metadata,
                started_at=started_at,
                completed_at=completed_at,
                total_tokens=total_tokens
            )

            logger.info(f"  ✅ Compilation complete")
            self._emit_progress('layer_6_complete', {
                'questions_answered': result.questions_answered,
                'total_questions': config.total_questions,
                'footnotes': len(result.footnotes)
            })

            # ============================================================
            # FINAL REPORT
            # ============================================================
            self._print_final_summary(result, config)
            self._emit_progress('analysis_complete', {
                'result': result,
                'processing_time': result.processing_time_seconds
            })

            return result

        except Exception as e:
            # Preserve detailed error information for debugging
            error_type = type(e).__name__
            error_msg = str(e)

            logger.error(f"❌ Analysis failed ({error_type}): {error_msg}", exc_info=True)
            self._emit_progress('analysis_failed', {'error': error_msg, 'error_type': error_type})

            # Provide helpful context based on error type
            if "JSON" in error_msg or "Unexpected token" in error_msg:
                detailed_error = (
                    f"OpenAI API returned invalid response (expected JSON, got HTML). "
                    f"This usually indicates an API authentication error. "
                    f"Original error: {error_msg}"
                )
                raise RuntimeError(detailed_error) from e
            else:
                raise RuntimeError(f"HOTDOG analysis failed ({error_type}): {error_msg}") from e

    def _print_final_summary(self, result: AnalysisResult, config: ParsedConfig):
        """Print final analysis summary."""
        logger.info("\n" + "="*64)
        logger.info("🎉 HOTDOG ANALYSIS COMPLETE")
        logger.info("="*64)
        logger.info(f"Document: {result.document_name}")
        logger.info(f"Pages: {result.total_pages}")
        logger.info(f"Questions Answered: {result.questions_answered}/{config.total_questions}")
        logger.info(f"Average Confidence: {result.average_confidence:.0%}")
        logger.info(f"Total Footnotes: {len(result.footnotes)}")
        logger.info(f"Processing Time: {result.processing_time_seconds:.2f}s")
        logger.info(f"Total Tokens: {result.total_tokens:,}")
        logger.info(f"Estimated Cost: ${result.estimated_cost:.4f}")
        logger.info("="*64)

        # Layer statistics
        logger.info("\n📊 LAYER STATISTICS")
        logger.info(self.layer3_processor.get_statistics())
        logger.info(self.layer4_accumulator.get_statistics())
        logger.info(self.layer5_token_manager.get_statistics())

        # Print accumulation report
        logger.info("\n" + self.layer4_accumulator.generate_report())

    async def run_second_pass(self, first_pass_result: AnalysisResult) -> AnalysisResult:
        """
        Run second-pass analysis on unanswered questions from first pass.

        This method uses enhanced scrutiny and creative interpretation to find
        answers to questions that were not answered in the first pass.

        Args:
            first_pass_result: Result from the first pass analysis

        Returns:
            Updated AnalysisResult with second-pass answers merged in

        Raises:
            ValueError: If cached data not available (must run first pass first)
            RuntimeError: If second pass fails critically
        """
        if not self.cached_windows or not self.cached_experts or not self.cached_config:
            raise ValueError("Second pass requires cached data from first pass. Run analyze_document() first.")

        logger.info(f"\n{'='*64}")
        logger.info(f"🔍 STARTING SECOND PASS - ENHANCED SCRUTINY")
        logger.info(f"{'='*64}")

        started_at = datetime.now()
        self._emit_progress('second_pass_started', {
            'first_pass_questions_answered': first_pass_result.questions_answered,
            'total_questions': self.cached_config.total_questions
        })

        try:
            # Identify unanswered questions
            unanswered_questions = self._identify_unanswered_questions(
                first_pass_result,
                self.cached_config
            )

            logger.info(f"📊 First Pass Results:")
            logger.info(f"   Answered: {first_pass_result.questions_answered}/{self.cached_config.total_questions}")
            logger.info(f"   Unanswered: {len(unanswered_questions)}")
            logger.info(f"   Completion Rate: {first_pass_result.questions_answered/self.cached_config.total_questions*100:.1f}%")

            if not unanswered_questions:
                logger.info("🎉 All questions answered in first pass! No second pass needed.")
                return first_pass_result

            # Run second-pass processor
            logger.info(f"\n🔍 Running second pass on {len(unanswered_questions)} unanswered questions...")
            self._emit_progress('second_pass_processing', {
                'unanswered_count': len(unanswered_questions)
            })

            second_pass_answers = await self.layer3_5_second_pass.process_unanswered_questions(
                windows=self.cached_windows,
                unanswered_questions=unanswered_questions,
                experts=self.cached_experts
            )

            logger.info(f"✅ Second pass found {len(second_pass_answers)} new answers")

            # Merge second-pass answers into accumulator
            logger.info(f"\n🔄 Merging second-pass answers into first-pass results...")
            for question_id, answer in second_pass_answers.items():
                # Add to accumulator (will handle deduplication)
                if question_id not in first_pass_result.questions:
                    first_pass_result.questions[question_id] = []
                first_pass_result.questions[question_id].append(answer)
                logger.info(f"   ✅ Added answer for {question_id}")

            # Recompile results with merged answers
            completed_at = datetime.now()
            total_tokens = (
                first_pass_result.total_tokens +
                self.layer3_5_second_pass.total_tokens_used
            )

            # Recalculate cost
            estimated_cost = total_tokens * 0.00003  # ~$0.03 per 1K tokens

            # Update result metadata
            first_pass_result.total_tokens = total_tokens
            first_pass_result.estimated_cost = estimated_cost
            first_pass_result.completed_at = completed_at

            # Recompile footnotes
            from .output_compiler import OutputCompiler
            compiler = OutputCompiler()
            first_pass_result.footnotes = compiler._compile_footnotes(first_pass_result.questions)

            # Final statistics
            logger.info(f"\n{'='*64}")
            logger.info(f"🎉 SECOND PASS COMPLETE")
            logger.info(f"{'='*64}")
            logger.info(f"Questions Answered (First Pass): {first_pass_result.questions_answered - len(second_pass_answers)}")
            logger.info(f"Questions Answered (Second Pass): {len(second_pass_answers)}")
            logger.info(f"Total Questions Answered: {first_pass_result.questions_answered}/{self.cached_config.total_questions}")
            logger.info(f"New Completion Rate: {first_pass_result.questions_answered/self.cached_config.total_questions*100:.1f}%")
            logger.info(f"Second Pass Success Rate: {len(second_pass_answers)/len(unanswered_questions)*100:.1f}%")
            logger.info(f"Total Tokens: {total_tokens:,}")
            logger.info(f"Estimated Cost: ${estimated_cost:.4f}")
            logger.info(f"{'='*64}")

            # Print second-pass statistics
            logger.info("\n📊 SECOND PASS STATISTICS")
            logger.info(self.layer3_5_second_pass.get_statistics())

            self._emit_progress('second_pass_complete', {
                'second_pass_answers_found': len(second_pass_answers),
                'total_questions_answered': first_pass_result.questions_answered,
                'completion_rate': first_pass_result.questions_answered/self.cached_config.total_questions,
                'total_tokens': total_tokens,
                'estimated_cost': estimated_cost
            })

            return first_pass_result

        except Exception as e:
            logger.error(f"❌ Second pass failed: {str(e)}", exc_info=True)
            self._emit_progress('second_pass_failed', {'error': str(e)})
            raise RuntimeError(f"Second pass analysis failed: {str(e)}") from e

    def _identify_unanswered_questions(
        self,
        result: AnalysisResult,
        config: ParsedConfig
    ) -> List[Question]:
        """
        Identify questions that were not answered in the first pass.

        Args:
            result: First pass analysis result
            config: Question configuration

        Returns:
            List of Question objects that have no answers
        """
        unanswered = []

        for question_id, question in config.question_map.items():
            # Check if this question has any answers
            if question_id not in result.questions or not result.questions[question_id]:
                unanswered.append(question)

        return unanswered

    def _emit_progress(self, event_type: str, data: dict):
        """Emit progress event to callback if provided."""
        if self.progress_callback:
            try:
                self.progress_callback(event_type, data)
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def _format_live_unitary_log(
        self,
        accumulated_answers: AnswerAccumulation,
        config: ParsedConfig,
        current_window: int,
        total_windows: int
    ) -> str:
        """
        Format accumulated answers as markdown for live unitary log display.

        Returns markdown-formatted string with:
        - All questions and answers found so far
        - Full citations with PDF page numbers
        - Section grouping
        - Progress indicator
        """
        lines = []
        lines.append(f"# 📊 Live Analysis Progress: Window {current_window}/{total_windows}\n")

        total_answered = 0
        total_questions = config.total_questions

        # Group answers by section
        for section in config.sections:
            section_lines = []
            section_answered = 0

            for question in section.questions:
                if question.id in accumulated_answers and accumulated_answers[question.id]:
                    # Get best answer (highest confidence)
                    best_answer = accumulated_answers[question.id][0]

                    section_lines.append(f"**Q{question.id}:** {question.text}")
                    section_lines.append(f"**Answer:** {best_answer.text}")
                    section_lines.append(f"*Confidence: {best_answer.confidence:.0%}, Expert: {best_answer.expert}*\n")

                    section_answered += 1
                    total_answered += 1

            # Only include section if it has answers
            if section_lines:
                lines.append(f"## {section.name} ({section_answered}/{len(section.questions)} answered)\n")
                lines.extend(section_lines)
                lines.append("")

        lines.append(f"\n---\n**Total Progress: {total_answered}/{total_questions} questions answered ({total_answered/total_questions*100:.1f}%)**")

        return "\n".join(lines)

    def get_browser_output(self, result: AnalysisResult, config: ParsedConfig) -> dict:
        """
        Get formatted output for browser display.

        Args:
            result: Analysis result
            config: Question configuration

        Returns:
            Dict ready to serialize to JSON for frontend
        """
        return self.layer6_compiler.format_for_browser(result, config)

    def get_excel_output(self, result: AnalysisResult, config: ParsedConfig) -> dict:
        """
        Get formatted output for Excel export.

        Args:
            result: Analysis result
            config: Question configuration

        Returns:
            Dict with sheet data for Excel generation
        """
        return self.layer6_compiler.format_for_excel(result, config)

    def get_text_report(self, result: AnalysisResult, config: ParsedConfig) -> str:
        """
        Get human-readable text report.

        Args:
            result: Analysis result
            config: Question configuration

        Returns:
            Formatted text report
        """
        return self.layer6_compiler.generate_text_report(result, config)


# =============================================================================
# CONVENIENCE FUNCTION FOR SIMPLE USAGE
# =============================================================================

async def analyze_pdf_simple(
    pdf_path: str,
    config_path: str,
    openai_api_key: str
) -> AnalysisResult:
    """
    Simplified interface for analyzing a PDF document.

    Example usage:
        import asyncio
        from services.hotdog import analyze_pdf_simple

        async def main():
            result = await analyze_pdf_simple(
                pdf_path="document.pdf",
                config_path="questions.json",
                openai_api_key="sk-..."
            )
            print(f"Analyzed {result.total_pages} pages")
            print(f"Answered {result.questions_answered} questions")

        asyncio.run(main())

    Args:
        pdf_path: Path to PDF document
        config_path: Path to question configuration JSON
        openai_api_key: OpenAI API key

    Returns:
        Complete AnalysisResult
    """
    orchestrator = HotdogOrchestrator(
        openai_api_key=openai_api_key,
        config_path=config_path
    )

    result = await orchestrator.analyze_document(pdf_path)
    return result
