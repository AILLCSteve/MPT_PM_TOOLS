"""
Layer 3.5: Second-Pass Specialized Processor
Hierarchical Orchestrated Thorough Document Oversight & Guidance - Enhanced Scrutiny

Processes unanswered questions from the first pass using specialized AI agents
with enhanced creativity and scrutiny.

CRITICAL FEATURES:
- Targets only unanswered questions
- Enhanced AI prompts for difficult-to-find information
- Multiple search strategies (creative interpretation, context expansion)
- Same 3-page window architecture
- Appends results to same output format
- Maintains page citation standards
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from openai import AsyncOpenAI

from .models import (
    Answer,
    Question,
    WindowContext,
    WindowResult,
    ExpertPersona,
    ConfidenceLevel
)

logger = logging.getLogger(__name__)


class SecondPassProcessor:
    """
    Specialized processor for second-pass analysis of unanswered questions.

    Uses enhanced AI prompts with:
    - Creative interpretation of questions
    - Broader context awareness
    - Multiple search strategies
    - Lower confidence thresholds (capture tentative answers)

    Design Principles:
    - Single Responsibility: Only handles second-pass processing
    - Open/Closed: Extensible for additional pass strategies
    - Dependency Inversion: Depends on abstractions (OpenAI client)
    """

    def __init__(
        self,
        openai_client: AsyncOpenAI,
        max_parallel_experts: int = 5,
        context_guardrails: Optional[str] = None,
        model: str = "gpt-4o",
        max_completion_tokens: int = 16384
    ):
        """
        Initialize the second-pass processor.

        Args:
            openai_client: OpenAI async client for API calls
            max_parallel_experts: Maximum concurrent API calls
            context_guardrails: Global context rules (e.g., "Only CIPP lining context")
            model: OpenAI model to use (default: gpt-4o)
            max_completion_tokens: Maximum tokens for completion
        """
        self.openai_client = openai_client
        self.max_parallel_experts = max_parallel_experts
        self.context_guardrails = context_guardrails or ""
        self.model = model
        self.max_completion_tokens = max_completion_tokens

        # Statistics
        self.total_questions_targeted = 0
        self.total_answers_found = 0
        self.total_api_calls = 0
        self.total_tokens_used = 0

        logger.info("🔍 Second-Pass Processor initialized")
        logger.info(f"   Model: {model}")
        logger.info(f"   Max completion tokens: {max_completion_tokens:,}")
        if self.context_guardrails:
            logger.info(f"📋 Context Guardrails Active: {self.context_guardrails[:100]}...")

    async def process_unanswered_questions(
        self,
        windows: List[WindowContext],
        unanswered_questions: List[Question],
        experts: Dict[str, ExpertPersona]
    ) -> Dict[str, Answer]:
        """
        Process unanswered questions using enhanced scrutiny.

        Args:
            windows: All 3-page windows from the document
            unanswered_questions: Questions without answers from first pass
            experts: Expert personas mapped by section_id

        Returns:
            Dictionary of newly found answers (question_id -> Answer)
        """
        logger.info(f"\n{'='*64}")
        logger.info(f"🔍 SECOND PASS: Enhanced Scrutiny")
        logger.info(f"{'='*64}")
        logger.info(f"Targeting {len(unanswered_questions)} unanswered questions")

        self.total_questions_targeted = len(unanswered_questions)
        all_new_answers = {}

        # Process each window with unanswered questions
        for window_idx, window in enumerate(windows, 1):
            logger.info(f"\n🔎 Second Pass - Window {window_idx}/{len(windows)}: Pages {window.page_range_str}")

            window_result = await self._process_window_enhanced(
                window=window,
                questions=unanswered_questions,
                experts=experts
            )

            # Merge new answers
            for question_id, answer in window_result.answers.items():
                if question_id not in all_new_answers:
                    all_new_answers[question_id] = answer
                    logger.info(f"  ✅ Found answer for {question_id}!")
                else:
                    # Merge with existing answer from earlier window
                    all_new_answers[question_id].merge_with(answer)

            # Progress update
            if window_idx % 3 == 0:
                logger.info(f"\n📊 Second Pass Progress: {window_idx}/{len(windows)} windows")
                logger.info(f"   New answers found: {len(all_new_answers)}")

        self.total_answers_found = len(all_new_answers)

        logger.info(f"\n🎉 Second Pass Complete!")
        logger.info(f"   Questions targeted: {self.total_questions_targeted}")
        logger.info(f"   New answers found: {self.total_answers_found}")
        logger.info(f"   Success rate: {self.total_answers_found/self.total_questions_targeted*100:.1f}%")

        return all_new_answers

    async def _process_window_enhanced(
        self,
        window: WindowContext,
        questions: List[Question],
        experts: Dict[str, ExpertPersona]
    ) -> WindowResult:
        """
        Process a single window with enhanced scrutiny for difficult questions.

        Uses specialized prompts that encourage:
        - Creative interpretation
        - Inference from context
        - Partial answer extraction
        - Lower confidence thresholds

        Args:
            window: 3-page window to analyze
            questions: Unanswered questions to target
            experts: Expert personas by section

        Returns:
            WindowResult with any newly found answers
        """
        started_at = datetime.now()
        answers = {}
        total_tokens = 0

        # Group questions by section for expert assignment
        questions_by_section = {}
        for question in questions:
            if question.section_id not in questions_by_section:
                questions_by_section[question.section_id] = []
            questions_by_section[question.section_id].append(question)

        # Create tasks for parallel processing (respecting max_parallel limit)
        tasks = []
        for section_id, section_questions in questions_by_section.items():
            expert = experts.get(section_id)
            if not expert:
                logger.warning(f"No expert for section {section_id}, skipping")
                continue

            task = self._query_expert_enhanced(
                window=window,
                questions=section_questions,
                expert=expert
            )
            tasks.append(task)

        # Execute in parallel with concurrency limit
        semaphore = asyncio.Semaphore(self.max_parallel_experts)

        async def bounded_query(task):
            async with semaphore:
                return await task

        results = await asyncio.gather(*[bounded_query(t) for t in tasks], return_exceptions=True)

        # Collect answers from all expert calls
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Expert call failed: {result}")
                continue

            if result:
                expert_answers, tokens = result
                answers.update(expert_answers)
                total_tokens += tokens
                self.total_api_calls += 1

        completed_at = datetime.now()
        processing_time = (completed_at - started_at).total_seconds()

        return WindowResult(
            window_num=window.window_num,
            pages=window.pages,
            answers=answers,
            tokens_used=total_tokens,
            processing_time=processing_time,
            expert_count=len(questions_by_section)
        )

    async def _query_expert_enhanced(
        self,
        window: WindowContext,
        questions: List[Question],
        expert: ExpertPersona
    ) -> Optional[tuple[Dict[str, Answer], int]]:
        """
        Query an expert with enhanced second-pass prompts.

        Enhanced prompts include:
        - Explicit instruction to find difficult-to-locate information
        - Permission to make reasonable inferences
        - Context guardrails if provided
        - Lower confidence threshold guidance

        Returns:
            Tuple of (answers_dict, tokens_used) or None if call fails
        """
        try:
            # Build enhanced system prompt
            enhanced_system_prompt = self._build_enhanced_system_prompt(expert)

            # Build user prompt with questions
            user_prompt = self._build_enhanced_user_prompt(window, questions)

            # Call OpenAI with enhanced parameters for second pass
            try:
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": enhanced_system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,  # Higher temperature for creativity and inference
                    max_tokens=self.max_completion_tokens  # Use full API limit for thorough answers
                )
            except Exception as api_error:
                logger.error(f"OpenAI API call failed in second pass: {type(api_error).__name__}: {str(api_error)}")
                raise

            # Parse response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API in second pass")

            tokens_used = response.usage.total_tokens

            self.total_tokens_used += tokens_used

            # Extract answers from response
            answers = self._parse_expert_response_enhanced(
                response_text=content,
                questions=questions,
                expert=expert,
                window=window
            )

            return (answers, tokens_used)

        except Exception as e:
            logger.error(f"Enhanced expert query failed for {expert.name}: {e}")
            return None

    def _build_enhanced_system_prompt(self, expert: ExpertPersona) -> str:
        """
        Build enhanced system prompt for second-pass analysis.

        Adds instructions for:
        - Creative interpretation
        - Inference from context
        - Partial answer acceptance
        - Context guardrails
        """
        base_prompt = expert.system_prompt

        enhancement = """

🔍 SECOND PASS - ENHANCED SCRUTINY MODE 🔍

You are now in SECOND PASS mode. These questions were not answered in the first pass,
meaning they are likely:
- Hidden in technical sections
- Implied rather than explicitly stated
- Require inference from multiple locations
- May have partial information available

ENHANCED INSTRUCTIONS:
1. **Be Creative**: Look for implied answers, reasonable inferences, context clues
2. **Partial Answers OK**: Even incomplete information is valuable - mark confidence accordingly
3. **Broader Context**: Consider the entire document context, not just exact matches
4. **Lower Threshold**: Include answers even with confidence as low as 0.3 if there's ANY supporting evidence
5. **Multiple Strategies**:
   - Check synonyms and related terms
   - Look at surrounding context
   - Consider document structure (headers, tables, specifications)
   - Check for implicit references

"""

        if self.context_guardrails:
            enhancement += f"""
📋 CONTEXT GUARDRAILS (MANDATORY):
{self.context_guardrails}

**All answers MUST be interpreted within this context.** If information doesn't fit these
guardrails, mark it as "Not found" rather than providing out-of-context answers.

"""

        enhancement += """
CRITICAL: Still maintain PDF page citations <PDF pg X> for ALL answers, even partial ones.
"""

        return base_prompt + enhancement

    def _build_enhanced_user_prompt(self, window: WindowContext, questions: List[Question]) -> str:
        """Build user prompt for enhanced second-pass analysis."""
        # Truncate window text if too long
        truncated_text = window.text[:8000]

        prompt = f"""Analyze the following document section (Pages {window.page_range_str}) with ENHANCED SCRUTINY.

These questions were UNANSWERED in the first pass. Use creative interpretation and inference.

DOCUMENT SECTION:
{truncated_text}

QUESTIONS TO ANSWER:
"""

        for i, question in enumerate(questions, 1):
            prompt += f"\n{i}. [{question.id}] {question.text}"

        prompt += """

RESPONSE FORMAT (JSON):
{
  "answers": [
    {
      "question_id": "Q1",
      "answer": "Your answer with <PDF pg X> citation",
      "pages": [5, 7],
      "confidence": 0.45,
      "reasoning": "Brief explanation of how you found this (especially for inferred answers)"
    }
  ]
}

Remember:
- Include answers even if confidence is low (≥0.3)
- Explain your reasoning for inferred/implied answers
- ALWAYS include <PDF pg X> citations
- Use context guardrails if provided
"""

        return prompt

    def _parse_expert_response_enhanced(
        self,
        response_text: str,
        questions: List[Question],
        expert: ExpertPersona,
        window: WindowContext
    ) -> Dict[str, Answer]:
        """
        Parse expert response and extract answers.

        Enhanced parsing handles:
        - Reasoning field (optional)
        - Lower confidence thresholds
        - Partial answers
        """
        answers = {}

        try:
            import json

            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                logger.warning(f"No JSON found in expert response for {expert.name}")
                return answers

            json_str = response_text[json_start:json_end]

            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse second-pass response as JSON: {e}")
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
                logger.warning(f"Skipping malformed response from {expert.name}")
                return answers

            # Parse each answer
            for answer_data in data.get('answers', []):
                question_id = answer_data.get('question_id')
                answer_text = answer_data.get('answer', '')
                pages = answer_data.get('pages', [])
                confidence = answer_data.get('confidence', 0.3)
                reasoning = answer_data.get('reasoning', '')

                # Validation
                if not question_id or not answer_text:
                    continue

                # Skip "not found" answers
                if 'not found' in answer_text.lower() or 'not yet found' in answer_text.lower():
                    continue

                # Ensure page citation in text
                if '<PDF pg' not in answer_text:
                    if pages:
                        pages_str = ', '.join(map(str, pages))
                        answer_text += f" <PDF pg {pages_str}>"
                    else:
                        # Try to extract from window
                        pages = window.pages
                        pages_str = ', '.join(map(str, pages))
                        answer_text += f" <PDF pg {pages_str}>"

                # Create Answer object
                try:
                    answer = Answer(
                        question_id=question_id,
                        text=answer_text,
                        pages=pages if pages else window.pages,
                        confidence=confidence,
                        expert=expert.name + " (Second Pass)",
                        window=window.window_num
                    )

                    # Add reasoning to metadata if available
                    if reasoning:
                        logger.info(f"  {question_id}: {reasoning}")

                    answers[question_id] = answer

                except ValueError as e:
                    logger.warning(f"Failed to create answer for {question_id}: {e}")
                    continue

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Response text: {response_text[:500]}...")
        except Exception as e:
            logger.error(f"Answer parsing failed: {e}")

        return answers

    def get_statistics(self) -> str:
        """Get formatted statistics for second pass."""
        if self.total_questions_targeted == 0:
            return "Second Pass: Not run"

        success_rate = (self.total_answers_found / self.total_questions_targeted * 100) if self.total_questions_targeted > 0 else 0

        stats = f"""
Second Pass Statistics:
  Questions Targeted: {self.total_questions_targeted}
  New Answers Found: {self.total_answers_found}
  Success Rate: {success_rate:.1f}%
  API Calls: {self.total_api_calls}
  Tokens Used: {self.total_tokens_used:,}
"""
        return stats
