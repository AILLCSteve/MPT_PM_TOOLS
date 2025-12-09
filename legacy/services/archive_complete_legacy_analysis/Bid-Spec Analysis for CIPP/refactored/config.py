"""
Configuration module for CIPP Analyzer application.
Centralizes all configuration constants following DRY principle.
"""

import os
from pathlib import Path


class Config:
    """Application configuration constants."""

    # Server configuration
    HOST = os.getenv('HOST', 'localhost')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # PDF extraction configuration
    MIN_TEXT_LENGTH = 10
    PDF_TEMP_SUFFIX = '.pdf'

    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    # Browser configuration
    BROWSER_STARTUP_DELAY = 2  # seconds

    @staticmethod
    def get_resource_path(relative_path: str) -> str:
        """
        Get absolute path to resource, works for dev and PyInstaller builds.

        Args:
            relative_path: Path relative to application root

        Returns:
            Absolute path to resource
        """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            import sys
            base_path = sys._MEIPASS
        except (ImportError, AttributeError):
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)
