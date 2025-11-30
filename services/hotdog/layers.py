"""
HOTDOG AI Processing Layers

Implements the 6-layer architecture for document analysis:
- Layer 0: Document Ingestion
- Layer 1: Configuration Loader
- Layer 2: Expert Persona Generator
- Layer 3: Multi-Expert Processor
- Layer 4: Smart Accumulator
- Layer 5: Token Budget Manager
- Layer 6: Output Compiler

Following SOLID principles from CLAUDE.md:
- Single Responsibility: Each layer has one clear purpose
- Open/Closed: Extend through interfaces, not modification
- Dependency Inversion: Depend on abstractions
"""

import os
import json
import hashlib
import logging
import asyncio
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path

# PDF extraction
import fitz  # PyMuPDF

# OpenAI
import openai

# Local imports
from .models import (
    PageData, Question, Section, ExpertPersona,
    Answer, WindowContext, WindowResult,
    ParsedConfig, AnalysisResult, ConfidenceLevel
)

logger = logging.getLogger(__name__)


# ============================================================================
# LAYER 0: DOCUMENT INGESTION
# ============================================================================

class DocumentIngestionLayer:
    """
    Layer 0: Extract text from PDF with perfect page number preservation.

    Single Responsibility: PDF extraction only
    - Does NOT route questions
    - Does NOT call AI
    - Does NOT format output

    Returns structured PageData objects with mandatory page numbers.
    """

    def __init__(self):
        self.supported_formats = ['.pdf', '.txt', '.docx', '.rtf']

    def is_supported(self, file_path: str) -> bool:
        """Check if file format is supported."""
        ext = Path(file_path).suffix.lower()
        return ext in self.supported_formats

    def extract_pdf(self, pdf_path: str) -> Tuple[List[PageData], Dict]:
        """
        Extract text from PDF with page numbers as first-class data.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Tuple of (pages, metadata)
            - pages: List[PageData] with page_num, text, char_count
            - metadata: Dict with total_pages, file_name, etc.

        Raises:
            FileNotFoundError: If PDF doesn't exist
            ValueError: If PDF is corrupted or empty
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            pages = []
            doc = fitz.open(pdf_path)

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()

                page_data = PageData(
                    page_num=page_num + 1,  # 1-indexed for user display
                    text=text,
                    char_count=len(text),
                    has_content=len(text.strip()) > 50
                )
                pages.append(page_data)

            doc.close()

            if not pages:
                raise ValueError(f"PDF has no pages: {pdf_path}")

            metadata = {
                'total_pages': len(pages),
                'total_chars': sum(p.char_count for p in pages),
                'file_name': os.path.basename(pdf_path),
                'extraction_time': datetime.now().isoformat(),
                'blank_pages': sum(1 for p in pages if not p.has_content)
            }

            logger.info(f"✅ Extracted {len(pages)} pages from {metadata['file_name']}")
            if metadata['blank_pages'] > 0:
                logger.warning(f"⚠️  Found {metadata['blank_pages']} blank pages")

            return pages, metadata

        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {e}")
            raise ValueError(f"Failed to extract PDF: {e}")

    def create_windows(self, pages: List[PageData], window_size: int = 3) -> List[WindowContext]:
        """
        Create 3-page windows from extracted pages.

        Args:
            pages: List of PageData objects
            window_size: Number of pages per window (default 3)

        Returns:
            List of WindowContext objects
        """
        windows = []
        window_num = 1

        for i in range(0, len(pages), window_size):
            window_pages = pages[i:i + window_size]
            page_nums = [p.page_num for p in window_pages]
            combined_text = '\n\n'.join([f"=== PAGE {p.page_num} ===\n{p.text}" for p in window_pages])

            window = WindowContext(
                window_num=window_num,
                pages=page_nums,
                text=combined_text,
                page_data=window_pages
            )
            windows.append(window)
            window_num += 1

        logger.info(f"📦 Created {len(windows)} windows from {len(pages)} pages")
        return windows


# ============================================================================
# LAYER 1: CONFIGURATION LOADER
# ============================================================================

class ConfigurationLoader:
    """
    Layer 1: Load question configuration dynamically.

    Single Responsibility: Configuration loading and parsing only
    - Loads from JSON/DB/user upload
    - Parses into structured objects
    - Validates configuration
    - Does NOT generate experts
    - Does NOT process documents
    """

    def load_from_json(self, config_path: str) -> ParsedConfig:
        """
        Load configuration from JSON file.

        Expected JSON structure:
        {
          "config_name": "CIPP Analysis",
          "version": "2.0",
          "sections": [
            {
              "section_id": "general_info",
              "section_name": "General Project Information",
              "description": "...",
              "questions": [
                {"id": "Q1", "text": "What is the project name?", ...},
                ...
              ]
            },
            ...
          ]
        }

        Args:
            config_path: Path to JSON configuration file

        Returns:
            ParsedConfig object with sections and questions

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            sections = []
            all_questions = []

            for section_data in config_data.get('sections', []):
                section = Section(
                    id=section_data['section_id'],
                    name=section_data['section_name'],
                    description=section_data.get('description', ''),
                    questions=[]
                )

                for q_data in section_data.get('questions', []):
                    question = Question(
                        id=q_data['id'],
                        text=q_data['text'],
                        section_id=section.id,
                        required=q_data.get('required', True),
                        expected_type=q_data.get('expected_answer_type', 'string')
                    )
                    section.add_question(question)
                    all_questions.append(question)

                sections.append(section)

            # Create lookup maps
            section_map = {s.id: s for s in sections}
            question_map = {q.id: q for q in all_questions}

            parsed_config = ParsedConfig(
                name=config_data.get('config_name', 'Unknown'),
                version=config_data.get('version', '1.0'),
                sections=sections,
                section_map=section_map,
                question_map=question_map,
                metadata={
                    'loaded_at': datetime.now().isoformat(),
                    'source': config_path
                }
            )

            logger.info(f"✅ Loaded config: {parsed_config.name} v{parsed_config.version}")
            logger.info(f"   {parsed_config.total_sections} sections, {parsed_config.total_questions} questions")

            return parsed_config

        except Exception as e:
            logger.error(f"❌ Failed to load config: {e}")
            raise ValueError(f"Invalid configuration: {e}")

    def create_default_cipp_config(self) -> ParsedConfig:
        """
        Create default CIPP analysis configuration (hardcoded fallback).

        This is used if no JSON config is available.
        """
        sections = [
            Section(
                id="general_info",
                name="General Project Information",
                description="Project metadata, owner, contract details",
                questions=[]
            ),
            Section(
                id="materials",
                name="Materials & Equipment Specifications",
                description="Pipe materials, resins, liners, ASTM standards",
                questions=[]
            ),
            # Add other sections as needed...
        ]

        # Add sample questions (simplified - full list would be loaded from JSON)
        sections[0].add_question(Question(
            id="Q1",
            text="What is the project name?",
            section_id="general_info"
        ))

        section_map = {s.id: s for s in sections}
        question_map = {}
        for section in sections:
            for question in section.questions:
                question_map[question.id] = question

        return ParsedConfig(
            name="CIPP Bid Specification Analysis (Default)",
            version="1.0",
            sections=sections,
            section_map=section_map,
            question_map=question_map,
            metadata={'source': 'default'}
        )


# ============================================================================
# LAYER 2: EXPERT PERSONA GENERATOR
# ============================================================================

class ExpertPersonaGenerator:
    """
    Layer 2: Generate AI expert personas dynamically from section metadata.

    Single Responsibility: Expert persona creation only
    - Generates specialized prompts for each section
    - Caches experts for reuse
    - Does NOT process documents
    - Does NOT route questions

    Key Innovation: Uses AI to create AI experts (meta-prompting)
    """

    def __init__(self, openai_client, cache_store=None):
        """
        Initialize expert generator.

        Args:
            openai_client: OpenAI API client
            cache_store: Optional cache (dict or Redis client)
        """
        self.client = openai_client
        self.cache = cache_store or {}  # In-memory dict fallback

    def generate_expert(self, section: Section) -> ExpertPersona:
        """
        Generate or retrieve cached expert persona for a section.

        Uses AI to create a specialized expert based on:
        - Section name
        - Section description
        - Sample questions

        Args:
            section: Section object with metadata

        Returns:
            ExpertPersona with system prompt and strategies
        """
        # Check cache first
        cache_key = self._make_cache_key(section.name)

        if cache_key in self.cache:
            logger.info(f"💾 Expert cache HIT: {section.name}")
            return self.cache[cache_key]

        logger.info(f"🤖 Generating expert for: {section.name}")

        # Build generation prompt
        sample_questions = '\n'.join([f"- {q.text}" for q in section.questions[:5]])

        prompt = f"""You are an expert AI architect designing specialized document analysis personas.

Create an expert AI persona for analyzing construction/engineering bid specifications.

**Section Details:**
- Name: {section.name}
- Description: {section.description}
- Sample Questions:
{sample_questions}

**Generate the following (output as JSON):**

1. **expert_name**: A creative, descriptive name for this expert (e.g., "CIPP Materials & Standards Compliance Specialist")

2. **specialization**: 2-3 sentences describing this expert's domain knowledge and experience

3. **system_prompt**: Detailed instructions for this expert including:
   - Areas of expertise
   - Types of information to extract
   - Required citation format: <PDF pg X>
   - Precision requirements (measurements, standards, etc.)
   - Answer style (factual, concise, technical)

4. **citation_strategy**: How this expert should extract and include PDF page numbers

5. **answer_format**: Structure and style of answers this expert should produce

**CRITICAL**: The expert MUST always include PDF page citations in format: <PDF pg X>

Output only valid JSON, no markdown formatting."""

        try:
            # Call AI to generate expert
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert AI architect."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,  # Some creativity for persona generation
                response_format={"type": "json_object"}
            )

            # Parse response
            expert_data = json.loads(response.choices[0].message.content)

            # Validate required fields
            required_fields = ['expert_name', 'specialization', 'system_prompt',
                             'citation_strategy', 'answer_format']
            for field in required_fields:
                if field not in expert_data:
                    raise ValueError(f"Expert generation missing field: {field}")

            # Create expert object
            expert = ExpertPersona(
                id=f"{section.id}_expert",
                name=expert_data['expert_name'],
                section_id=section.id,
                section_name=section.name,
                system_prompt=expert_data['system_prompt'],
                specialization=expert_data['specialization'],
                citation_strategy=expert_data['citation_strategy'],
                answer_format=expert_data['answer_format'],
                cache_key=cache_key
            )

            # Cache for future use
            self.cache[cache_key] = expert

            logger.success(f"✅ Generated expert: {expert.name}")
            return expert

        except Exception as e:
            logger.error(f"❌ Expert generation failed: {e}")
            # Fallback to generic expert
            return self._create_generic_expert(section, cache_key)

    def _create_generic_expert(self, section: Section, cache_key: str) -> ExpertPersona:
        """Fallback generic expert if generation fails."""
        logger.warning(f"⚠️  Using generic expert for: {section.name}")

        expert = ExpertPersona(
            id=f"{section.id}_expert",
            name=f"{section.name} Specialist",
            section_id=section.id,
            section_name=section.name,
            system_prompt=f"""You are a document analysis expert specializing in {section.name}.

Extract factual information from construction bid specifications related to this category.

**CRITICAL**: Always cite PDF page numbers in your answers using the format: <PDF pg X>

Be precise, factual, and thorough in your responses.""",
            specialization=f"Expert in {section.name} for construction document analysis.",
            citation_strategy="Include <PDF pg X> in all answers",
            answer_format="Direct, factual answers with page citations",
            cache_key=cache_key
        )

        self.cache[cache_key] = expert
        return expert

    def _make_cache_key(self, section_name: str) -> str:
        """Generate consistent cache key from section name."""
        normalized = section_name.lower().strip()
        return f"expert:{hashlib.sha256(normalized.encode()).hexdigest()[:16]}"


# ============================================================================
# LAYER 5: TOKEN BUDGET MANAGER
# ============================================================================

class TokenBudgetManager:
    """
    Layer 5: Manage token usage to ensure exhaustive coverage.

    Single Responsibility: Token tracking and budget management
    - Tracks tokens used per window
    - Adjusts context if approaching limits
    - Prioritizes unanswered questions
    - Does NOT process documents
    - Does NOT generate experts
    """

    def __init__(self, max_prompt_tokens: int = 4000):
        self.max_prompt_tokens = max_prompt_tokens
        self.max_completion_tokens = 16000  # gpt-4 limit
        self.total_tokens_used = 0
        self.window_token_usage = []
        self.safety_buffer = 0.8  # Use 80% of max to be safe

    def check_budget_before_window(
        self,
        window_num: int,
        context_text: str,
        question_count: int
    ) -> Tuple[str, bool]:
        """
        Check if we have enough tokens for this window.
        Adjust prompt if needed.

        Args:
            window_num: Current window number
            context_text: Text from current 3-page window
            question_count: Number of questions to answer

        Returns:
            Tuple of (adjusted_context, can_proceed)
        """
        # Estimate tokens (rough: 4 chars ≈ 1 token)
        base_prompt_tokens = len(context_text) // 4
        question_tokens = question_count * 50  # ~50 tokens per question
        estimated_completion = question_count * 150  # ~150 tokens per answer

        total_estimate = base_prompt_tokens + question_tokens + estimated_completion

        logger.info(f"💰 Window {window_num} token estimate: {total_estimate}")
        logger.debug(f"   Context: {base_prompt_tokens}, Questions: {question_tokens}, Completion: {estimated_completion}")

        # Check if within limits
        max_allowed = self.max_prompt_tokens * self.safety_buffer

        if base_prompt_tokens > max_allowed:
            logger.warning(f"⚠️  Context exceeds budget ({base_prompt_tokens} > {max_allowed})")
            adjusted_context = self._truncate_context(context_text, max_allowed)
            logger.info(f"✂️  Truncated context to {len(adjusted_context) // 4} tokens")
            return adjusted_context, True

        return context_text, True

    def _truncate_context(self, text: str, max_tokens: int) -> str:
        """
        Intelligently truncate context to fit budget.
        Preserve beginning and end (most important sections).
        """
        target_chars = max_tokens * 4

        if len(text) <= target_chars:
            return text

        # Keep first 60% and last 40%
        keep_start = int(target_chars * 0.6)
        keep_end = int(target_chars * 0.4)

        truncated = (
            text[:keep_start] +
            "\n\n[... middle section truncated for token budget ...]\n\n" +
            text[-keep_end:]
        )

        return truncated

    def record_usage(self, window_num: int, prompt_tokens: int, completion_tokens: int):
        """Record actual token usage after API call."""
        total = prompt_tokens + completion_tokens
        self.total_tokens_used += total

        self.window_token_usage.append({
            'window': window_num,
            'prompt': prompt_tokens,
            'completion': completion_tokens,
            'total': total
        })

        logger.info(f"📊 Window {window_num} actual tokens: {total} (prompt: {prompt_tokens}, completion: {completion_tokens})")
        logger.info(f"📊 Total tokens used: {self.total_tokens_used}")

    def get_statistics(self) -> Dict:
        """Get token usage statistics."""
        if not self.window_token_usage:
            return {}

        total_prompt = sum(w['prompt'] for w in self.window_token_usage)
        total_completion = sum(w['completion'] for w in self.window_token_usage)
        avg_per_window = self.total_tokens_used / len(self.window_token_usage)

        return {
            'total_tokens': self.total_tokens_used,
            'total_prompt_tokens': total_prompt,
            'total_completion_tokens': total_completion,
            'windows_processed': len(self.window_token_usage),
            'avg_tokens_per_window': avg_per_window,
            'estimated_cost_usd': self.total_tokens_used * 0.00003  # Rough estimate for gpt-4
        }


# Note: Layer 3 (MultiExpertProcessor) is implemented in multi_expert_processor.py
# Layers 4 and 6 (SmartAccumulator, OutputCompiler) are complex and will be implemented
# in separate files due to their size and complexity. This keeps each module focused (SRP).
