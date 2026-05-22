"""
C++ specific pattern detection for code auditing.
"""

import re
from typing import Dict, List, Any
from athenah_ai.labeler.language_patterns.base import LanguagePatternDetector


class CppPatternDetector(LanguagePatternDetector):
    """Detect C++ patterns relevant to security auditing."""

    def get_language_name(self) -> str:
        return "cpp"

    def detect_patterns(
        self,
        source_code: str,
        file_path: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect C++ patterns."""

        patterns = {
            "raii_usage": self.detect_raii(source_code),
            "template_validation": self.detect_template_validation(source_code),
            "exception_patterns": self.detect_exception_patterns(source_code),
            "namespace_accessors": self.detect_namespace_accessors(source_code),
            "smart_pointers": self.detect_smart_pointers(source_code),
        }

        return patterns

    def detect_raii(self, source_code: str) -> List[Dict]:
        """
        Detect RAII patterns (smart pointers, file handles, etc.).

        RAII = Resource Acquisition Is Initialization
        Implications for auditing:
        - No manual cleanup needed
        - No null checks needed after construction
        - No memory leaks possible
        """
        raii_patterns = []

        # Smart pointers
        smart_pointer_types = [
            "std::unique_ptr",
            "std::shared_ptr",
            "std::weak_ptr",
            "boost::shared_ptr",
        ]

        for sp_type in smart_pointer_types:
            if sp_type in source_code:
                raii_patterns.append({
                    "type": "smart_pointer",
                    "pointer_type": sp_type,
                    "audit_implication": "No manual delete needed, no null checks after construction",
                    "false_positive_risk": "Missing null check, memory leak"
                })

        # RAII wrappers (locks, file handles)
        raii_wrappers = [
            ("std::lock_guard", "mutex lock"),
            ("std::unique_lock", "mutex lock"),
            ("std::ifstream", "file handle"),
            ("std::ofstream", "file handle"),
        ]

        for wrapper, resource in raii_wrappers:
            if wrapper in source_code:
                raii_patterns.append({
                    "type": "raii_wrapper",
                    "wrapper_type": wrapper,
                    "resource": resource,
                    "audit_implication": f"Automatic {resource} cleanup",
                    "false_positive_risk": f"Missing {resource} cleanup"
                })

        return raii_patterns

    def detect_template_validation(self, source_code: str) -> List[Dict]:
        """
        Detect template-based validation patterns.

        Example: json_template in XRPL rippled
        """
        validations = []

        # Pattern 1: Template constructors (validation on construction)
        # Example: STTx tx(json_value); // Validates all fields
        template_constructor_pattern = r'(\w+)\s+(\w+)\s*\(([^)]+)\)'
        matches = re.finditer(template_constructor_pattern, source_code)

        template_types = ["STTx", "STObject", "Template", "Validator"]
        for match in matches:
            type_name = match.group(1)
            if any(tt in type_name for tt in template_types):
                validations.append({
                    "type": "template_constructor",
                    "template_type": type_name,
                    "validates": "Input validated on construction",
                    "error_behavior": "Throws exception if invalid",
                    "audit_implication": "Fields validated before use",
                    "false_positive_risk": "Missing validation check"
                })

        # Pattern 2: Namespace accessors (pre-validated fields)
        # Example: tx[jss::Fee] means Fee is validated by template
        if "jss::" in source_code:
            validations.append({
                "type": "namespace_accessor",
                "namespace": "jss",
                "pattern": "jss::FieldName",
                "validates": "Field access implies template validation",
                "audit_implication": "Field guaranteed valid by framework",
                "false_positive_risk": "Missing field validation"
            })

        return validations

    def detect_exception_patterns(self, source_code: str) -> List[Dict]:
        """
        Detect exception handling patterns.

        C++ uses exceptions for error handling (not error codes).
        """
        patterns = []

        # Detect throw statements
        if "throw" in source_code:
            patterns.append({
                "type": "exception_throwing",
                "pattern": "throw statement",
                "audit_implication": "Errors reported via exceptions, not return codes",
                "false_positive_risk": "Missing error return value"
            })

        # Detect try-catch blocks
        if "try" in source_code and "catch" in source_code:
            patterns.append({
                "type": "exception_handling",
                "pattern": "try-catch block",
                "audit_implication": "Exception handling present",
                "context": "Test code may use try-catch as assertion"
            })

        # Common exception types
        exception_types = [
            "std::exception",
            "std::runtime_error",
            "std::logic_error",
            "parse_error",
            "validation_error",
        ]

        for exc_type in exception_types:
            if exc_type in source_code:
                patterns.append({
                    "type": "exception_type",
                    "exception_type": exc_type,
                    "audit_implication": f"Uses {exc_type} for error reporting"
                })

        return patterns

    def detect_namespace_accessors(self, source_code: str) -> List[Dict]:
        """
        Detect namespace accessor patterns.

        Namespaces often indicate framework-level abstractions.
        """
        accessors = []

        # Find namespace usages: namespace::identifier
        namespace_pattern = r'(\w+)::(\w+)'
        matches = re.finditer(namespace_pattern, source_code)

        seen_namespaces = set()
        for match in matches:
            namespace = match.group(1)
            if namespace not in seen_namespaces:
                seen_namespaces.add(namespace)

                # Known validation namespaces
                validation_namespaces = {
                    "jss": "JSON String constants - indicates template validation",
                    "sfld": "Serialized field - framework-managed",
                }

                if namespace in validation_namespaces:
                    accessors.append({
                        "namespace": namespace,
                        "meaning": validation_namespaces[namespace],
                        "audit_implication": "Fields accessed via this namespace are framework-validated",
                        "false_positive_risk": "Missing validation for framework-managed fields"
                    })

        return accessors

    def detect_smart_pointers(self, source_code: str) -> List[Dict]:
        """
        Detect smart pointer usage and implications.
        """
        pointers = []

        smart_pointer_implications = {
            "unique_ptr": {
                "ownership": "exclusive",
                "null_check_needed": False,
                "cleanup_needed": False,
                "audit_note": "Cannot be null after construction, auto cleanup"
            },
            "shared_ptr": {
                "ownership": "shared",
                "null_check_needed": False,
                "cleanup_needed": False,
                "audit_note": "Reference counted, auto cleanup when last ref dropped"
            },
        }

        for ptr_type, implications in smart_pointer_implications.items():
            if ptr_type in source_code:
                pointers.append({
                    "type": ptr_type,
                    **implications,
                    "false_positive_risk": "Missing null check or manual delete"
                })

        return pointers
