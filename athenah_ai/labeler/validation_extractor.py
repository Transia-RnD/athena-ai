"""
Validation pattern extraction using LLM analysis.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger("app")


class ValidationExtractor:
    """Extract validation patterns from code using LLM."""

    def __init__(self, client):
        self.client = client

    def extract_validation_patterns(
        self,
        source_code: str,
        file_path: str,
        language_patterns: Dict
    ) -> Dict[str, Any]:
        """
        Extract validation patterns from code.

        Uses LLM to identify:
        - What is being validated
        - How it's validated (function/framework)
        - Where validation occurs
        - What errors are thrown

        Args:
            source_code: Source code content
            file_path: Path to file
            language_patterns: Detected language patterns

        Returns:
            Dictionary with validation patterns
        """

        # Build context from language patterns
        context = self._build_context(language_patterns)

        prompt = f"""Analyze this code and identify ALL validation that occurs.

FILE: {file_path}

LANGUAGE CONTEXT:
{context}

CODE:
{source_code[:3000]}

For each validation found, provide:
1. **What** is being validated (field/input name)
2. **How** it's validated (function/framework/method)
3. **Where** it happens (function name or line reference)
4. **Error behavior** (what exception/error is thrown)
5. **Validation type** (format, type, business logic, etc.)

CRITICAL: Focus on INPUT VALIDATION and FIELD VALIDATION.
Look for:
- Template/constructor validation
- Explicit validation functions
- Framework validation (jss::, template engine, etc.)
- Type checking
- Range checking
- Format validation

Respond in JSON:
{{
  "validations": [
    {{
      "field": "field_name",
      "validated_by": "function_or_framework",
      "location": "function_name or constructor",
      "validation_type": "format|type|range|business_logic",
      "error_thrown": "exception_type",
      "validates": ["specific", "checks", "performed"],
      "confidence": 0.0-1.0
    }}
  ],
  "validation_architecture": {{
    "framework": "name_of_validation_framework",
    "validation_layer": "entry_point|middleware|business_logic",
    "auto_validated_fields": ["list", "of", "fields"]
  }}
}}
"""

        try:
            response = self.client.ask(prompt)
            return self._parse_validation_response(response)
        except Exception as e:
            logger.error(f"Validation extraction failed for {file_path}: {e}")
            return {"validations": [], "validation_architecture": {}}

    def _build_context(self, language_patterns: Dict) -> str:
        """Build context string from language patterns."""
        context_lines = []

        # RAII context
        if language_patterns.get("raii_usage"):
            context_lines.append("- Code uses RAII (smart pointers, auto cleanup)")

        # Template validation context
        if language_patterns.get("template_validation"):
            context_lines.append("- Code uses template-based validation")
            for tv in language_patterns["template_validation"]:
                if tv.get("namespace"):
                    context_lines.append(f"  - {tv['namespace']}:: namespace indicates framework validation")

        # Exception context
        if language_patterns.get("exception_patterns"):
            context_lines.append("- Code uses exceptions for error handling (not return codes)")

        return "\n".join(context_lines) if context_lines else "No specific language patterns detected"

    def _parse_validation_response(self, response: str) -> Dict:
        """Parse LLM response into structured validation data."""
        import json

        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(response[json_start:json_end])

                # Ensure required keys exist
                if "validations" not in parsed:
                    parsed["validations"] = []
                if "validation_architecture" not in parsed:
                    parsed["validation_architecture"] = {}

                return parsed
            else:
                logger.warning("No JSON found in validation response")
                return {"validations": [], "validation_architecture": {}}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation JSON: {e}")
            return {"validations": [], "validation_architecture": {}}
