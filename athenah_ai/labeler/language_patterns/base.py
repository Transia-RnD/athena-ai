"""
Base classes for language pattern detection.
"""

from typing import Dict, List, Any
from abc import ABC, abstractmethod


class LanguagePatternDetector(ABC):
    """Base class for language-specific pattern detection."""

    @abstractmethod
    def detect_patterns(
        self,
        source_code: str,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect language-specific patterns.

        Args:
            source_code: Source code content
            file_path: Path to file
            metadata: Existing metadata (functions, classes, etc.)

        Returns:
            Dictionary with detected patterns
        """
        pass

    @abstractmethod
    def get_language_name(self) -> str:
        """Return language name (e.g., 'cpp', 'python')."""
        pass
