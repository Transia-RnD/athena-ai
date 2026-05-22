"""
Language pattern detection for code auditing.

This package provides language-specific pattern detectors that identify
patterns relevant to security auditing and false positive reduction.
"""

from athenah_ai.labeler.language_patterns.base import LanguagePatternDetector
from athenah_ai.labeler.language_patterns.cpp_patterns import CppPatternDetector

__all__ = [
    "LanguagePatternDetector",
    "CppPatternDetector",
]
