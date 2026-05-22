"""
Unit tests for false positive pattern generation.
"""

import pytest
from athenah_ai.labeler.fp_generator import FalsePositivePatternGenerator


def test_generate_framework_validation_fps():
    """Test FP generation for framework validation."""

    validations = [
        {
            "field": "Fee",
            "validated_by": "json_template::constructor",
            "location": "STTx::STTx",
            "validation_type": "format",
            "confidence": 0.95
        }
    ]

    validation_architecture = {
        "framework": "json_template",
        "auto_validated_fields": ["Fee", "Amount"]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator._generate_framework_validation_fps(validations, validation_architecture)

    assert len(fps) > 0

    # Should have patterns for auto-validated fields
    auto_field_fps = [fp for fp in fps if "Missing validation for Fee" in fp["issue_pattern"] or "Missing validation for Amount" in fp["issue_pattern"]]
    assert len(auto_field_fps) >= 2

    # Should have patterns for specific validations
    empty_string_fps = [fp for fp in fps if "empty string" in fp["issue_pattern"]]
    assert len(empty_string_fps) >= 1

    format_fps = [fp for fp in fps if "format validation" in fp["issue_pattern"]]
    assert len(format_fps) >= 1


def test_generate_raii_fps():
    """Test FP generation for RAII patterns."""

    language_patterns = {
        "raii_usage": [
            {
                "type": "smart_pointer",
                "pointer_type": "std::unique_ptr"
            },
            {
                "type": "raii_wrapper",
                "wrapper_type": "std::lock_guard",
                "resource": "mutex lock"
            }
        ]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator._generate_raii_fps(language_patterns)

    assert len(fps) > 0

    # Should have null check FP
    null_check_fps = [fp for fp in fps if "null check" in fp["issue_pattern"].lower()]
    assert len(null_check_fps) >= 1
    assert "std::unique_ptr" in null_check_fps[0]["detection_keywords"]

    # Should have memory leak FP
    memory_leak_fps = [fp for fp in fps if "memory leak" in fp["issue_pattern"].lower()]
    assert len(memory_leak_fps) >= 1

    # Should have resource cleanup FP
    cleanup_fps = [fp for fp in fps if "cleanup" in fp["issue_pattern"].lower()]
    assert len(cleanup_fps) >= 1
    assert "mutex lock" in cleanup_fps[0]["issue_pattern"]


def test_generate_exception_fps():
    """Test FP generation for exception patterns."""

    language_patterns = {
        "exception_patterns": [
            {"type": "exception_throwing"}
        ]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator._generate_exception_fps(language_patterns)

    assert len(fps) >= 2

    # Should have error return value FP
    error_return_fps = [fp for fp in fps if "error return" in fp["issue_pattern"].lower()]
    assert len(error_return_fps) >= 1
    assert "exceptions" in error_return_fps[0]["why_false_positive"].lower()


def test_generate_namespace_fps():
    """Test FP generation for namespace accessor patterns."""

    language_patterns = {
        "namespace_accessors": [
            {
                "namespace": "jss",
                "meaning": "JSON String constants - indicates template validation"
            }
        ]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator._generate_namespace_fps(language_patterns)

    assert len(fps) >= 2

    # Should have validation FP
    validation_fps = [fp for fp in fps if "validation" in fp["issue_pattern"].lower()]
    assert len(validation_fps) >= 1
    assert "jss" in validation_fps[0]["detection_keywords"]


def test_generate_fp_patterns_complete():
    """Test complete FP pattern generation with all inputs."""

    validations = [
        {
            "field": "Fee",
            "validated_by": "json_template",
            "location": "STTx::STTx",
            "validation_type": "format",
            "confidence": 0.95
        }
    ]

    language_patterns = {
        "raii_usage": [
            {"type": "smart_pointer", "pointer_type": "std::unique_ptr"}
        ],
        "exception_patterns": [
            {"type": "exception_throwing"}
        ],
        "namespace_accessors": [
            {
                "namespace": "jss",
                "meaning": "JSON String constants - indicates template validation"
            }
        ]
    }

    validation_architecture = {
        "framework": "json_template",
        "auto_validated_fields": ["Fee"]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator.generate_fp_patterns(
        "test.cpp",
        validations,
        language_patterns,
        validation_architecture
    )

    # Should generate patterns from all sources
    assert len(fps) >= 8  # Multiple patterns from each category

    # Verify structure of FP patterns
    for fp in fps:
        assert "issue_pattern" in fp
        assert "why_false_positive" in fp
        assert "detection_keywords" in fp
        assert "confidence" in fp
        assert "applies_to" in fp

        # Verify types
        assert isinstance(fp["issue_pattern"], str)
        assert isinstance(fp["why_false_positive"], str)
        assert isinstance(fp["detection_keywords"], list)
        assert isinstance(fp["confidence"], float)
        assert isinstance(fp["applies_to"], list)


def test_fp_patterns_have_evidence():
    """Test that FP patterns include evidence."""

    validations = [
        {
            "field": "Fee",
            "validated_by": "json_template",
            "location": "STTx::STTx",
            "validation_type": "format",
            "confidence": 0.95
        }
    ]

    validation_architecture = {
        "framework": "json_template",
        "auto_validated_fields": ["Fee"]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator._generate_framework_validation_fps(validations, validation_architecture)

    # All FPs should have evidence field
    for fp in fps:
        assert "evidence" in fp
        assert isinstance(fp["evidence"], str)
        assert len(fp["evidence"]) > 0


def test_fp_confidence_scores():
    """Test that confidence scores are reasonable."""

    validations = [
        {
            "field": "Fee",
            "validated_by": "json_template",
            "location": "STTx::STTx",
            "validation_type": "format",
            "confidence": 0.95
        }
    ]

    language_patterns = {
        "raii_usage": [
            {"type": "smart_pointer", "pointer_type": "std::unique_ptr"}
        ]
    }

    validation_architecture = {
        "framework": "json_template",
        "auto_validated_fields": ["Fee"]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator.generate_fp_patterns(
        "test.cpp",
        validations,
        language_patterns,
        validation_architecture
    )

    # All confidence scores should be between 0 and 1
    for fp in fps:
        assert 0.0 <= fp["confidence"] <= 1.0
        # Most should be reasonably high (>0.75)
        assert fp["confidence"] > 0.75


def test_fp_detection_keywords_not_empty():
    """Test that all FP patterns have detection keywords."""

    language_patterns = {
        "raii_usage": [
            {"type": "smart_pointer", "pointer_type": "std::unique_ptr"}
        ]
    }

    generator = FalsePositivePatternGenerator()
    fps = generator._generate_raii_fps(language_patterns)

    for fp in fps:
        assert len(fp["detection_keywords"]) > 0
        # Should have at least 2 keywords for matching
        assert len(fp["detection_keywords"]) >= 2


def test_empty_inputs():
    """Test FP generation with empty inputs."""

    generator = FalsePositivePatternGenerator()
    fps = generator.generate_fp_patterns(
        "test.cpp",
        [],  # No validations
        {},  # No language patterns
        {}   # No validation architecture
    )

    # Should return empty list without crashing
    assert isinstance(fps, list)
    assert len(fps) == 0


def test_validation_type_specific_fps():
    """Test that different validation types generate appropriate FPs."""

    validations = [
        {
            "field": "Fee",
            "validated_by": "validator",
            "location": "func",
            "validation_type": "type",
            "confidence": 0.9
        },
        {
            "field": "Amount",
            "validated_by": "validator",
            "location": "func",
            "validation_type": "range",
            "confidence": 0.9
        }
    ]

    validation_architecture = {"framework": "test"}

    generator = FalsePositivePatternGenerator()
    fps = generator._generate_framework_validation_fps(validations, validation_architecture)

    # Should have type-specific FPs
    type_fps = [fp for fp in fps if "type validation" in fp["issue_pattern"]]
    assert len(type_fps) >= 1

    range_fps = [fp for fp in fps if "range validation" in fp["issue_pattern"]]
    assert len(range_fps) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
