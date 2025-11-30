"""
HOTDOG AI Document Processing System
Hierarchical Orchestrated Thorough Document Oversight & Guidance

This package implements a dynamic, user-centric AI architecture for
exhaustive document analysis with perfect PDF page citation preservation.

Key Features:
- Dynamic expert persona generation from section headings
- Smart answer accumulation with information preservation
- Mandatory PDF page number tracking at every stage
- Token budget management for exhaustive coverage
- Flexible question configuration system

Architecture follows SOLID principles:
- Single Responsibility: Each class has one clear purpose
- Open/Closed: Extension through interfaces, not modification
- Dependency Inversion: Depend on abstractions, not concrete implementations
"""

__version__ = "1.0.0"
__author__ = "AI LLC"

from .orchestrator import HotdogOrchestrator
from .layers import (
    DocumentIngestionLayer,
    ConfigurationLoader,
    ExpertPersonaGenerator,
    TokenBudgetManager
)
from .multi_expert_processor import MultiExpertProcessor
from .smart_accumulator import SmartAccumulator
from .output_compiler import OutputCompiler

__all__ = [
    'HotdogOrchestrator',
    'DocumentIngestionLayer',
    'ConfigurationLoader',
    'ExpertPersonaGenerator',
    'MultiExpertProcessor',
    'SmartAccumulator',
    'TokenBudgetManager',
    'OutputCompiler'
]
