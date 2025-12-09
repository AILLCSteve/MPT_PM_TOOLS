"""
Token Budget Optimizer
Optimizes token usage based on ACTUAL OpenAI API limits (not just context window).

CRITICAL: There are MULTIPLE token limits to consider:

1. CONTEXT WINDOW (total capacity):
   - gpt-4: 8,192 tokens
   - gpt-4-32k: 32,768 tokens
   - gpt-4-turbo: 128,000 tokens
   - gpt-4o: 128,000 tokens
   - gpt-4o-mini: 128,000 tokens

2. max_tokens API PARAMETER (per-request completion limit):
   - gpt-4: max_tokens up to 8,192 (but limited by context)
   - gpt-4-turbo: max_tokens up to 4,096 (API enforced!)
   - gpt-4o: max_tokens up to 16,384 (API enforced!)
   - gpt-4o-mini: max_tokens up to 16,384

3. PRACTICAL INPUT LIMITS (prompt tokens):
   - Context Window - max_tokens = max input
   - gpt-4o: 128K - 16K = 112K max input
   - But we use less to avoid errors

4. RATE LIMITS (varies by tier - TPM and RPM):
   Tier 1: 200K TPM, 500 RPM
   Tier 2: 2M TPM, 5K RPM
   Tier 3: 10M TPM, 10K RPM
   Tier 4: 80M TPM, 20K RPM
   Tier 5: 300M TPM, 40K RPM

CONSERVATIVE STRATEGY (to avoid hitting ANY limit):
- Use 60% of context window for prompts (not 75%)
- Use conservative max_tokens values
- Account for parallel processing (5 concurrent calls)
- Stay at 50% of typical Tier 2 rate limits for safety
"""

import logging
from typing import Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelLimits:
    """
    ACTUAL token limits for a specific model.

    These account for ALL limits: context window, API parameters, and rate limits.
    """
    context_window: int  # Total tokens (prompt + completion)
    max_completion_tokens_api: int  # API enforced max_tokens parameter
    max_prompt_tokens: int  # Practical input limit (context - completion)
    recommended_prompt_tokens: int  # Safe limit for parallel processing (60% of max)
    recommended_completion_tokens: int  # Safe completion limit


class TokenOptimizer:
    """
    Optimizes token usage based on model capabilities.

    Automatically detects model from model string and sets appropriate limits.
    """

    # Model configurations - ACTUAL LIMITS (not theoretical)
    MODEL_CONFIGS = {
        'gpt-4': ModelLimits(
            context_window=8192,
            max_completion_tokens_api=8192,  # API allows up to context limit
            max_prompt_tokens=6144,  # Leave room for completion
            recommended_prompt_tokens=4000,  # Conservative: 50% of max
            recommended_completion_tokens=2000  # Conservative completion
        ),
        'gpt-4-32k': ModelLimits(
            context_window=32768,
            max_completion_tokens_api=32768,  # API allows up to context limit
            max_prompt_tokens=24576,  # 75% of context
            recommended_prompt_tokens=16000,  # Conservative: 50% of context
            recommended_completion_tokens=4000  # Conservative completion
        ),
        'gpt-4-turbo': ModelLimits(
            context_window=128000,
            max_completion_tokens_api=4096,  # API ENFORCED LIMIT (not 128K!)
            max_prompt_tokens=123904,  # 128K - 4K
            recommended_prompt_tokens=90000,  # 60% of max prompt, 5 parallel = 450K TPM
            recommended_completion_tokens=4096  # Use full API limit
        ),
        'gpt-4o': ModelLimits(
            context_window=128000,
            max_completion_tokens_api=16384,  # API ENFORCED LIMIT (much better than turbo)
            max_prompt_tokens=111616,  # 128K - 16K
            recommended_prompt_tokens=75000,  # 60% of max prompt, 5 parallel = 375K TPM
            recommended_completion_tokens=16384  # Use full API limit
        ),
        'gpt-4o-mini': ModelLimits(
            context_window=128000,
            max_completion_tokens_api=16384,  # API ENFORCED LIMIT
            max_prompt_tokens=111616,  # 128K - 16K
            recommended_prompt_tokens=75000,  # 60% of max prompt
            recommended_completion_tokens=16384  # Use full API limit
        ),
    }

    @classmethod
    def detect_model_limits(cls, model_name: str = 'gpt-4') -> ModelLimits:
        """
        Detect model limits from model name.

        Args:
            model_name: OpenAI model identifier (e.g., "gpt-4-turbo-preview")

        Returns:
            ModelLimits configuration for the detected model
        """
        # Normalize model name
        model_lower = model_name.lower()

        # Check for specific models
        if 'gpt-4o-mini' in model_lower:
            limits = cls.MODEL_CONFIGS['gpt-4o-mini']
            logger.info(f"🔍 Detected model: GPT-4o-mini (128K context)")
        elif 'gpt-4o' in model_lower:
            limits = cls.MODEL_CONFIGS['gpt-4o']
            logger.info(f"🔍 Detected model: GPT-4o (128K context)")
        elif 'turbo' in model_lower or '1106' in model_lower or '0125' in model_lower:
            limits = cls.MODEL_CONFIGS['gpt-4-turbo']
            logger.info(f"🔍 Detected model: GPT-4 Turbo (128K context)")
        elif '32k' in model_lower:
            limits = cls.MODEL_CONFIGS['gpt-4-32k']
            logger.info(f"🔍 Detected model: GPT-4-32k (32K context)")
        else:
            limits = cls.MODEL_CONFIGS['gpt-4']
            logger.info(f"🔍 Detected model: GPT-4 (8K context)")

        logger.info(f"📊 Token Budget Configuration:")
        logger.info(f"   Context Window: {limits.context_window:,} tokens")
        logger.info(f"   Max Completion (API): {limits.max_completion_tokens_api:,} tokens")
        logger.info(f"   Max Prompt (Practical): {limits.max_prompt_tokens:,} tokens")
        logger.info(f"   Recommended Prompt/Request: {limits.recommended_prompt_tokens:,} tokens (60% of max)")
        logger.info(f"   Recommended Completion: {limits.recommended_completion_tokens:,} tokens")
        logger.info(f"   Parallel Processing (5x): ~{limits.recommended_prompt_tokens * 5:,} TPM")
        logger.info(f"   ⚠️  This avoids hitting API max_tokens limits!")

        return limits

    @classmethod
    def calculate_optimal_window_size(
        cls,
        model_name: str,
        avg_chars_per_page: int = 2000,
        chars_per_token: float = 4.0
    ) -> Tuple[int, int]:
        """
        Calculate optimal window size based on model limits.

        Args:
            model_name: OpenAI model identifier
            avg_chars_per_page: Average characters per PDF page
            chars_per_token: Approximate characters per token (English: ~4)

        Returns:
            Tuple of (optimal_window_size_pages, estimated_tokens_per_window)
        """
        limits = cls.detect_model_limits(model_name)

        # Calculate how many pages fit in recommended prompt budget
        tokens_per_page = avg_chars_per_page / chars_per_token
        max_pages = int(limits.recommended_prompt_tokens / tokens_per_page)

        # Conservative: use 70% of max to leave room for questions + instructions
        optimal_pages = int(max_pages * 0.7)

        # Minimum 3 pages, maximum 20 pages per window
        optimal_pages = max(3, min(20, optimal_pages))

        estimated_tokens = int(optimal_pages * tokens_per_page)

        logger.info(f"📐 Optimal Window Calculation:")
        logger.info(f"   Recommended: {optimal_pages} pages per window")
        logger.info(f"   Estimated: {estimated_tokens:,} tokens per window")
        logger.info(f"   Headroom: {limits.recommended_prompt_tokens - estimated_tokens:,} tokens for questions/instructions")

        return (optimal_pages, estimated_tokens)

    @classmethod
    def get_enhanced_prompt_budget(cls, model_name: str) -> Dict[str, int]:
        """
        Get token budgets for enhanced, detailed prompts.

        Returns budgets for different prompt components.

        Args:
            model_name: OpenAI model identifier

        Returns:
            Dictionary with token budgets for prompt components
        """
        limits = cls.detect_model_limits(model_name)

        # Allocate tokens across prompt components
        budget = {
            'system_prompt': int(limits.recommended_prompt_tokens * 0.15),  # 15% for system instructions
            'context_text': int(limits.recommended_prompt_tokens * 0.70),  # 70% for document context
            'questions': int(limits.recommended_prompt_tokens * 0.10),  # 10% for questions
            'examples': int(limits.recommended_prompt_tokens * 0.05),  # 5% for few-shot examples
            'total': limits.recommended_prompt_tokens
        }

        logger.info(f"💰 Enhanced Prompt Budget Allocation:")
        for component, tokens in budget.items():
            logger.info(f"   {component}: {tokens:,} tokens")

        return budget

    @classmethod
    def estimate_completion_tokens(cls, model_name: str, num_questions: int) -> int:
        """
        Estimate required completion tokens for a given number of questions.

        Args:
            model_name: OpenAI model identifier
            num_questions: Number of questions to answer

        Returns:
            Estimated completion tokens needed
        """
        limits = cls.detect_model_limits(model_name)

        # Estimate: ~100 tokens per question answer (conservative)
        estimated = num_questions * 100

        # Cap at max completion limit
        estimated = min(estimated, limits.max_completion_tokens)

        logger.info(f"📝 Completion Estimate: {estimated:,} tokens for {num_questions} questions")

        return estimated
