"""
Code path documentation using LLM analysis.

Documents validation code paths, data flows, and test coverage implications.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger("app")


class CodePathDocumenter:
    """Document code paths and data flows for audit context."""

    def __init__(self, client):
        self.client = client

    def document_code_paths(
        self,
        source_code: str,
        file_path: str,
        validations: List[Dict],
        language_patterns: Dict,
        functions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Document code paths and data flows.

        Args:
            source_code: Source code content
            file_path: Path to file
            validations: List of detected validations
            language_patterns: Detected language patterns
            functions: List of functions in file

        Returns:
            Dictionary with code paths and data flows
        """

        # Build context from validations and language patterns
        context = self._build_context(validations, language_patterns, functions)

        prompt = f"""Analyze this code and document the validation code paths and data flows.

FILE: {file_path}

CONTEXT:
{context}

CODE:
{source_code[:4000]}

Document:
1. **Call Chains**: What functions call what (especially validation paths)
2. **Data Flows**: How fields flow through the code (origin → transformations → destination)
3. **Test Coverage**: What tests exist and what's NOT tested

CRITICAL: Focus on VALIDATION CODE PATHS and DATA FLOWS.
Look for:
- Entry points that trigger validation
- Call chains leading to validation
- How data flows from input to validation to usage
- What test files might test this code

Respond in JSON:
{{
  "call_chains": [
    {{
      "entry_point": "function_name",
      "call_chain": ["func1", "func2", "func3"],
      "purpose": "What this call chain does",
      "validation_points": ["Where validation occurs in chain"]
    }}
  ],
  "data_flows": [
    {{
      "field": "field_name",
      "origin": "Where field comes from",
      "flow": ["origin", "step1", "step2", "destination"],
      "transformations": ["What happens to field"],
      "validated_at": "Where validation occurs"
    }}
  ],
  "test_coverage_notes": "Brief notes on test coverage and gaps"
}}
"""

        try:
            response = self.client.ask(prompt)
            return self._parse_code_path_response(response)
        except Exception as e:
            logger.error(f"Code path documentation failed for {file_path}: {e}")
            return {"call_chains": [], "data_flows": [], "test_coverage_notes": ""}

    def _build_context(
        self,
        validations: List[Dict],
        language_patterns: Dict,
        functions: List[Dict]
    ) -> str:
        """Build context string from validations and patterns."""
        context_lines = []

        # Validation context
        if validations:
            context_lines.append(f"VALIDATIONS ({len(validations)}):")
            for v in validations[:5]:  # First 5
                field = v.get("field", "unknown")
                validated_by = v.get("validated_by", "unknown")
                context_lines.append(f"  - {field} validated by {validated_by}")

        # Function context
        if functions:
            context_lines.append(f"\nFUNCTIONS ({len(functions)}):")
            for f in functions[:10]:  # First 10
                context_lines.append(f"  - {f.get('name', 'unknown')}")

        # Language pattern context
        if language_patterns.get("template_validation"):
            context_lines.append("\nTEMPLATE VALIDATION:")
            context_lines.append("  - Code uses template-based validation framework")

        if language_patterns.get("exception_patterns"):
            context_lines.append("\nERROR HANDLING:")
            context_lines.append("  - Uses exceptions for error reporting")

        return "\n".join(context_lines) if context_lines else "No specific context available"

    def _parse_code_path_response(self, response: str) -> Dict:
        """Parse LLM response into structured code path data."""
        import json

        try:
            # Extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                parsed = json.loads(response[json_start:json_end])

                # Ensure required keys exist
                if "call_chains" not in parsed:
                    parsed["call_chains"] = []
                if "data_flows" not in parsed:
                    parsed["data_flows"] = []
                if "test_coverage_notes" not in parsed:
                    parsed["test_coverage_notes"] = ""

                return parsed
            else:
                logger.warning("No JSON found in code path response")
                return {"call_chains": [], "data_flows": [], "test_coverage_notes": ""}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse code path JSON: {e}")
            return {"call_chains": [], "data_flows": [], "test_coverage_notes": ""}
