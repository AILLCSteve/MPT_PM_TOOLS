"""
Layer 3: Multi-Expert Processing Engine

Coordinates parallel execution of specialized AI experts to answer questions
based on document window context. Ensures perfect PDF page citation preservation.

CRITICAL RESPONSIBILITIES:
- Route questions to appropriate expert personas
- Build context-aware prompts with citation requirements
- Execute AI calls in parallel using asyncio
- Parse and validate responses
- Enforce mandatory PDF page number citations
- Handle errors gracefully without losing data
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from openai import AsyncOpenAI

from .models import (
    WindowContext,
    WindowResult,
    Question,
    Answer,
    ExpertPersona,
    ConfidenceLevel
)

logger = logging.getLogger(__name__)


class MultiExpertProcessor:
    """
    Layer 3: Routes questions to expert personas and executes parallel AI processing.

    Design Principles:
    - Single Responsibility: Only handles expert coordination and AI execution
    - Open/Closed: Extensible through expert persona injection
    - Dependency Inversion: Depends on ExpertPersona abstraction, not concrete experts

    CRITICAL: Every answer MUST include PDF page citations.
    """

    def __init__(
        self,
        openai_client: AsyncOpenAI,
        max_parallel_experts: int = 5,
        model: str = "gpt-4o",
        max_completion_tokens: int = 16384
    ):
        """
        Initialize the multi-expert processor.

        Args:
            openai_client: Async OpenAI client for API calls
            max_parallel_experts: Maximum concurrent expert calls (rate limiting)
            model: OpenAI model to use (default: gpt-4o - most robust available)
            max_completion_tokens: Maximum tokens for completion (gpt-4o limit: 16,384)
        """
        self.client = openai_client
        self.max_parallel = max_parallel_experts
        self.model = model
        self.max_completion_tokens = max_completion_tokens
        self.total_api_calls = 0
        self.total_tokens = 0

        logger.info(f"🤖 Multi-Expert Processor initialized with model: {model}")
        logger.info(f"   Max completion tokens: {max_completion_tokens:,}")

    async def process_window(
        self,
        window: WindowContext,
        questions: List[Question],
        experts: Dict[str, ExpertPersona]  # section_id -> ExpertPersona
    ) -> WindowResult:
        """
        Process a 3-page window with all expert personas in parallel.

        Args:
            window: The 3-page window context to analyze
            questions: All questions to answer
            experts: Mapping of section_id to ExpertPersona

        Returns:
            WindowResult containing all answers found in this window
        """
        start_time = datetime.now()
        logger.info(f"🔍 Processing Window {window.window_num} (Pages {window.page_range_str})")

        # Group questions by section/expert
        questions_by_expert = self._group_questions_by_expert(questions, experts)

        # Create expert processing tasks
        tasks = []
        for section_id, expert_questions in questions_by_expert.items():
            expert = experts[section_id]
            task = self._process_expert_questions(
                window=window,
                expert=expert,
                questions=expert_questions
            )
            tasks.append(task)

        # Execute all experts in parallel (with concurrency limit)
        all_answers = []
        errors = []

        # Process in batches to respect rate limits
        for i in range(0, len(tasks), self.max_parallel):
            batch = tasks[i:i + self.max_parallel]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)

            for result in batch_results:
                if isinstance(result, Exception):
                    error_msg = f"Expert processing error: {str(result)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                else:
                    answers, tokens_used = result
                    all_answers.extend(answers)
                    self.total_tokens += tokens_used

        # Compile results
        answers_dict = {answer.question_id: answer for answer in all_answers}

        processing_time = (datetime.now() - start_time).total_seconds()

        result = WindowResult(
            window_num=window.window_num,
            pages=window.pages,
            answers=answers_dict,
            tokens_used=self.total_tokens,
            processing_time=processing_time,
            expert_count=len(questions_by_expert),
            errors=errors
        )

        logger.info(f"✅ Window {window.window_num} complete: {len(answers_dict)} answers, {processing_time:.2f}s")

        return result

    def _group_questions_by_expert(
        self,
        questions: List[Question],
        experts: Dict[str, ExpertPersona]
    ) -> Dict[str, List[Question]]:
        """
        Group questions by their section (which determines the expert).

        Returns:
            Dict mapping section_id to list of questions for that expert
        """
        grouped = {}
        for question in questions:
            section_id = question.section_id
            if section_id not in grouped:
                grouped[section_id] = []
            grouped[section_id].append(question)

        return grouped

    async def _process_expert_questions(
        self,
        window: WindowContext,
        expert: ExpertPersona,
        questions: List[Question]
    ) -> Tuple[List[Answer], int]:
        """
        Process all questions for a single expert persona.

        Args:
            window: Document window context
            expert: The expert persona to use
            questions: Questions for this expert to answer

        Returns:
            Tuple of (answers, tokens_used)
        """
        logger.info(f"🤖 Expert '{expert.name}' analyzing {len(questions)} questions")

        # Build the expert prompt
        prompt = self._build_expert_prompt(window, expert, questions)

        # Log API call details for debugging
        logger.info(f"\n{'='*80}")
        logger.info(f"🔵 API CALL: Expert '{expert.name}' - Window {window.window_num}")
        logger.info(f"{'='*80}")
        logger.info(f"MODEL: {self.model}")
        logger.info(f"SYSTEM PROMPT ({len(expert.system_prompt)} chars):")
        logger.info(f"{expert.system_prompt[:500]}..." if len(expert.system_prompt) > 500 else expert.system_prompt)
        logger.info(f"\nUSER PROMPT ({len(prompt)} chars):")
        logger.info(f"{prompt[:500]}..." if len(prompt) > 500 else prompt)
        logger.info(f"{'='*80}\n")

        # Execute AI call with optimized token limits
        try:
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": expert.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,  # Lower temperature for factual extraction
                    max_tokens=self.max_completion_tokens,  # API enforced limit
                    response_format={"type": "json_object"}
                )
            except Exception as api_error:
                logger.error(f"OpenAI API call failed for expert '{expert.name}': {type(api_error).__name__}: {str(api_error)}")
                raise

            self.total_api_calls += 1

            # Parse response
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI API")

            tokens_used = response.usage.total_tokens

            # Log API response details
            logger.info(f"\n{'='*80}")
            logger.info(f"🟢 API RESPONSE: Expert '{expert.name}'")
            logger.info(f"{'='*80}")
            logger.info(f"TOKENS USED: {tokens_used} (prompt: {response.usage.prompt_tokens}, completion: {response.usage.completion_tokens})")
            logger.info(f"JSON RESPONSE ({len(content)} chars):")
            logger.info(f"{content[:1000]}..." if len(content) > 1000 else content)
            logger.info(f"{'='*80}\n")

            answers = self._parse_expert_response(
                response_content=content,
                expert=expert,
                window=window,
                questions=questions
            )

            logger.info(f"✅ Expert '{expert.name}' found {len(answers)} answers ({tokens_used} tokens)")

            return answers, tokens_used

        except Exception as e:
            logger.error(f"❌ Expert '{expert.name}' failed: {str(e)}")
            raise

    def _build_expert_prompt(
        self,
        window: WindowContext,
        expert: ExpertPersona,
        questions: List[Question]
    ) -> str:
        """
        Build the prompt for an expert to analyze a document window.

        CRITICAL: Prompt MUST enforce PDF page citation requirements.
        """
        # Format questions
        questions_text = "\n".join([
            f"{i+1}. [{q.id}] {q.text}"
            for i, q in enumerate(questions)
        ])

        # Get page numbers for citation
        page_numbers = ", ".join(map(str, window.pages))

        prompt = f"""You are analyzing a document excerpt to answer specific questions.

DOCUMENT EXCERPT (Pages {window.page_range_str}):
{window.text}

---

QUESTIONS TO ANSWER:
{questions_text}

---

CRITICAL INSTRUCTIONS:
1. Answer ONLY the questions listed above
2. Base answers ONLY on the text provided (Pages {page_numbers})
3. EVERY answer MUST include PDF page citation in format: <PDF pg X> where X is the page number
4. If information spans multiple pages, cite ALL pages: <PDF pg 5, 6, 7>
5. If you cannot find information for a question, respond with "NOT FOUND" and confidence 0.0
6. Be specific and factual - extract exact information from the text
7. Include your confidence level (0.0-1.0) for each answer

OUTPUT FORMAT (JSON):
{{
  "answers": [
    {{
      "question_id": "Q1",
      "text": "The answer text with <PDF pg X> citation included",
      "pages": [5, 6],
      "confidence": 0.85,
      "reasoning": "Brief explanation of how you found this answer"
    }}
  ]
}}

{expert.citation_strategy}

Remember: Every answer MUST have a <PDF pg X> citation. This is MANDATORY."""

        return prompt

    def _parse_expert_response(
        self,
        response_content: str,
        expert: ExpertPersona,
        window: WindowContext,
        questions: List[Question]
    ) -> List[Answer]:
        """
        Parse the expert's JSON response into validated Answer objects.

        CRITICAL: Validates that every answer has page citations.

        Raises:
            ValueError: If response is malformed or missing required citations
        """
        try:
            response_data = json.loads(response_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse expert response as JSON: {e}")
            logger.error(f"Response content: {response_content[:500]}")
            raise ValueError(f"Expert response is not valid JSON: {e}")

        answers = []

        for answer_data in response_data.get('answers', []):
            question_id = answer_data.get('question_id')
            text = answer_data.get('text', '').strip()
            pages = answer_data.get('pages', [])
            confidence = answer_data.get('confidence', 0.0)

            # Skip "NOT FOUND" responses
            if text == "NOT FOUND" or confidence == 0.0:
                logger.debug(f"Question {question_id}: No information found in this window")
                continue

            # CRITICAL VALIDATION: Ensure page citations exist
            if not pages:
                logger.warning(f"Question {question_id}: Missing page array - attempting to extract from text")
                pages = self._extract_pages_from_text(text)

                if not pages:
                    logger.error(f"Question {question_id}: FAILED - No page citations found")
                    raise ValueError(f"Answer for {question_id} missing page citations - MANDATORY")

            # Validate citation marker in text
            if '<PDF pg' not in text:
                logger.warning(f"Question {question_id}: Missing <PDF pg> marker - adding it")
                pages_str = ', '.join(map(str, pages))
                text = f"{text} <PDF pg {pages_str}>"

            # Validate pages are within window range
            valid_pages = [p for p in pages if p in window.pages]
            if not valid_pages:
                logger.warning(f"Question {question_id}: Pages {pages} not in window {window.pages}")
                valid_pages = [window.pages[0]]  # Default to first page of window

            # Create Answer object (validation happens in __post_init__)
            try:
                answer = Answer(
                    question_id=question_id,
                    text=text,
                    pages=valid_pages,
                    confidence=confidence,
                    expert=expert.name,
                    window=window.window_num
                )
                answers.append(answer)
                logger.debug(f"✅ Question {question_id}: Answer validated (pages: {valid_pages})")

            except ValueError as e:
                logger.error(f"Question {question_id}: Validation failed - {e}")
                raise

        return answers

    def _extract_pages_from_text(self, text: str) -> List[int]:
        """
        Emergency fallback: Extract page numbers from citation markers in text.

        Looks for patterns like:
        - <PDF pg 5>
        - <PDF pg 5, 6, 7>
        - <PDF pg 5-7>
        """
        pages = []

        # Pattern 1: <PDF pg 5, 6, 7>
        match = re.search(r'<PDF pg ([0-9, ]+)>', text)
        if match:
            page_str = match.group(1)
            pages = [int(p.strip()) for p in page_str.split(',')]
            return pages

        # Pattern 2: <PDF pg 5-7>
        match = re.search(r'<PDF pg (\d+)-(\d+)>', text)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            pages = list(range(start, end + 1))
            return pages

        # Pattern 3: <PDF pg 5>
        match = re.search(r'<PDF pg (\d+)>', text)
        if match:
            pages = [int(match.group(1))]
            return pages

        return pages

    def get_statistics(self) -> Dict:
        """Get processing statistics for monitoring."""
        return {
            'total_api_calls': self.total_api_calls,
            'total_tokens': self.total_tokens,
            'estimated_cost': self.total_tokens * 0.00003  # Rough estimate for GPT-4
        }
