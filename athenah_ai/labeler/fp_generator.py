"""
False positive pattern generator.

Automatically generates patterns that predict what will be incorrectly flagged
as issues by audit agents.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger("app")


class FalsePositivePatternGenerator:
    """Generate false positive patterns from validation and language patterns."""

    def generate_fp_patterns(
        self,
        file_path: str,
        validations: List[Dict],
        language_patterns: Dict,
        validation_architecture: Dict
    ) -> List[Dict]:
        """
        Generate false positive patterns.

        Args:
            file_path: Path to file
            validations: List of detected validations
            language_patterns: Detected language patterns
            validation_architecture: High-level validation info

        Returns:
            List of false positive patterns
        """
        fp_patterns = []

        # Pattern 1: Template/framework validation
        fp_patterns.extend(
            self._generate_framework_validation_fps(validations, validation_architecture)
        )

        # Pattern 2: RAII patterns
        fp_patterns.extend(
            self._generate_raii_fps(language_patterns)
        )

        # Pattern 3: Exception handling patterns
        fp_patterns.extend(
            self._generate_exception_fps(language_patterns)
        )

        # Pattern 4: Namespace accessor patterns
        fp_patterns.extend(
            self._generate_namespace_fps(language_patterns)
        )

        logger.info(f"Generated {len(fp_patterns)} FP patterns for {file_path}")
        return fp_patterns

    def _generate_framework_validation_fps(
        self,
        validations: List[Dict],
        validation_architecture: Dict
    ) -> List[Dict]:
        """Generate FPs for framework-level validation."""
        fp_patterns = []

        framework = validation_architecture.get("framework")
        if not framework:
            return fp_patterns

        auto_validated_fields = validation_architecture.get("auto_validated_fields", [])

        # For each auto-validated field, generate FP pattern
        for field in auto_validated_fields:
            fp_patterns.append({
                "issue_pattern": f"Missing validation for {field}",
                "why_false_positive": f"{framework} validates {field} automatically",
                "detection_keywords": [field, "validation", "missing", "check"],
                "confidence": 0.90,
                "applies_to": ["validation", "input_validation"],
                "evidence": f"Field {field} validated by {framework}"
            })

        # Generate patterns for specific validations
        for validation in validations:
            field = validation.get("field")
            validated_by = validation.get("validated_by")
            validation_type = validation.get("validation_type")
            location = validation.get("location", "unknown")

            if not field or not validated_by:
                continue

            # Empty string validation
            fp_patterns.append({
                "issue_pattern": f"Missing empty string validation for {field}",
                "why_false_positive": f"{validated_by} validates {field} for empty strings",
                "detection_keywords": [field, "empty", "string", "validation"],
                "confidence": validation.get("confidence", 0.85),
                "applies_to": ["validation", "null_empty"],
                "evidence": f"{validated_by} at {location}"
            })

            # Type validation
            if validation_type == "type":
                fp_patterns.append({
                    "issue_pattern": f"Missing type validation for {field}",
                    "why_false_positive": f"{validated_by} validates {field} type",
                    "detection_keywords": [field, "type", "validation", "check"],
                    "confidence": 0.85,
                    "applies_to": ["validation", "type_safety"],
                    "evidence": f"{validated_by} at {location}"
                })

            # Format validation
            if validation_type == "format":
                fp_patterns.append({
                    "issue_pattern": f"Missing format validation for {field}",
                    "why_false_positive": f"{validated_by} validates {field} format",
                    "detection_keywords": [field, "format", "validation", "invalid"],
                    "confidence": 0.85,
                    "applies_to": ["validation", "input_validation"],
                    "evidence": f"{validated_by} at {location}"
                })

            # Range validation
            if validation_type == "range":
                fp_patterns.append({
                    "issue_pattern": f"Missing range validation for {field}",
                    "why_false_positive": f"{validated_by} validates {field} range",
                    "detection_keywords": [field, "range", "bounds", "validation"],
                    "confidence": 0.85,
                    "applies_to": ["validation", "bounds_check"],
                    "evidence": f"{validated_by} at {location}"
                })

        return fp_patterns

    def _generate_raii_fps(self, language_patterns: Dict) -> List[Dict]:
        """Generate FPs for RAII patterns."""
        fp_patterns = []

        raii_usage = language_patterns.get("raii_usage", [])
        for raii in raii_usage:
            if raii["type"] == "smart_pointer":
                fp_patterns.append({
                    "issue_pattern": f"Missing null check for {raii['pointer_type']}",
                    "why_false_positive": "RAII smart pointers guarantee initialization",
                    "detection_keywords": ["null", "nullptr", "check", raii['pointer_type']],
                    "confidence": 0.90,
                    "applies_to": ["null_check", "memory_safety"],
                    "evidence": f"Code uses {raii['pointer_type']}"
                })

                fp_patterns.append({
                    "issue_pattern": "Memory leak - missing delete",
                    "why_false_positive": "Smart pointer handles cleanup automatically",
                    "detection_keywords": ["memory", "leak", "delete"],
                    "confidence": 0.85,
                    "applies_to": ["memory_safety", "resource_leak"],
                    "evidence": f"Code uses {raii['pointer_type']}"
                })

            if raii["type"] == "raii_wrapper":
                resource = raii.get("resource", "resource")
                wrapper = raii.get("wrapper_type", "wrapper")
                fp_patterns.append({
                    "issue_pattern": f"Missing {resource} cleanup",
                    "why_false_positive": f"{wrapper} provides automatic {resource} cleanup",
                    "detection_keywords": [resource, "cleanup", "release", "close"],
                    "confidence": 0.88,
                    "applies_to": ["resource_management", "cleanup"],
                    "evidence": f"Code uses {wrapper}"
                })

        return fp_patterns

    def _generate_exception_fps(self, language_patterns: Dict) -> List[Dict]:
        """Generate FPs for exception handling patterns."""
        fp_patterns = []

        exception_patterns = language_patterns.get("exception_patterns", [])
        if any(p["type"] == "exception_throwing" for p in exception_patterns):
            fp_patterns.append({
                "issue_pattern": "Missing error return value",
                "why_false_positive": "Function uses exceptions for error reporting, not return codes",
                "detection_keywords": ["error", "return", "value", "check"],
                "confidence": 0.80,
                "applies_to": ["error_handling"],
                "evidence": "Code uses throw statements"
            })

            fp_patterns.append({
                "issue_pattern": "Function does not return error code",
                "why_false_positive": "Errors are reported via exceptions, not return values",
                "detection_keywords": ["error", "code", "return", "status"],
                "confidence": 0.82,
                "applies_to": ["error_handling", "return_value"],
                "evidence": "Code uses exception-based error handling"
            })

        return fp_patterns

    def _generate_namespace_fps(self, language_patterns: Dict) -> List[Dict]:
        """Generate FPs for namespace accessor patterns."""
        fp_patterns = []

        namespace_accessors = language_patterns.get("namespace_accessors", [])
        for accessor in namespace_accessors:
            namespace = accessor.get("namespace")
            meaning = accessor.get("meaning", "")

            if "validation" in meaning.lower():
                fp_patterns.append({
                    "issue_pattern": f"Missing validation for {namespace}:: field",
                    "why_false_positive": meaning,
                    "detection_keywords": [namespace, "validation", "missing"],
                    "confidence": 0.85,
                    "applies_to": ["validation", "input_validation"],
                    "evidence": f"Uses {namespace}:: namespace accessor"
                })

                fp_patterns.append({
                    "issue_pattern": f"Unvalidated field access via {namespace}::",
                    "why_false_positive": f"{namespace}:: namespace indicates framework-validated fields",
                    "detection_keywords": [namespace, "unvalidated", "field"],
                    "confidence": 0.83,
                    "applies_to": ["validation", "field_access"],
                    "evidence": f"Framework validates all {namespace}:: fields"
                })

        return fp_patterns
