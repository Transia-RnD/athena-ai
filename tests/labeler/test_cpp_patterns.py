"""
Unit tests for C++ pattern detection.
"""

import pytest
from athenah_ai.labeler.language_patterns.cpp_patterns import CppPatternDetector


def test_raii_detection():
    """Test detection of RAII patterns (smart pointers)."""
    code = """
    std::unique_ptr<Foo> ptr = std::make_unique<Foo>();
    std::shared_ptr<Bar> bar = std::make_shared<Bar>();
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    assert "raii_usage" in patterns
    assert len(patterns["raii_usage"]) == 2

    # Check that both smart pointer types were detected
    pointer_types = [p["pointer_type"] for p in patterns["raii_usage"]]
    assert "std::unique_ptr" in pointer_types
    assert "std::shared_ptr" in pointer_types


def test_raii_wrappers():
    """Test detection of RAII wrappers (locks, file handles)."""
    code = """
    std::lock_guard<std::mutex> lock(mutex_);
    std::ifstream file("data.txt");
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    assert "raii_usage" in patterns
    assert len(patterns["raii_usage"]) == 2

    wrapper_types = [p["wrapper_type"] for p in patterns["raii_usage"]]
    assert "std::lock_guard" in wrapper_types
    assert "std::ifstream" in wrapper_types


def test_template_validation_detection():
    """Test detection of template-based validation patterns."""
    code = """
    STTx tx(json_value);
    auto fee = tx[jss::Fee];
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    assert "template_validation" in patterns
    assert len(patterns["template_validation"]) >= 1

    # Should detect jss:: namespace accessor
    namespaces = [p["namespace"] for p in patterns["template_validation"] if p["type"] == "namespace_accessor"]
    assert "jss" in namespaces


def test_exception_patterns():
    """Test detection of exception handling patterns."""
    code = """
    void validate() {
        if (invalid) {
            throw std::runtime_error("Invalid input");
        }
    }

    void process() {
        try {
            validate();
        } catch (std::exception& e) {
            // handle error
        }
    }
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    assert "exception_patterns" in patterns
    assert len(patterns["exception_patterns"]) >= 3

    # Should detect throw, try-catch, and std::runtime_error
    types = [p["type"] for p in patterns["exception_patterns"]]
    assert "exception_throwing" in types
    assert "exception_handling" in types
    assert "exception_type" in types


def test_namespace_accessors():
    """Test detection of namespace accessor patterns."""
    code = """
    auto fee = tx[jss::Fee];
    auto amount = tx[jss::Amount];
    auto field = obj[sfld::Destination];
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    assert "namespace_accessors" in patterns
    assert len(patterns["namespace_accessors"]) == 2

    namespaces = [p["namespace"] for p in patterns["namespace_accessors"]]
    assert "jss" in namespaces
    assert "sfld" in namespaces


def test_smart_pointers():
    """Test detection of smart pointer usage."""
    code = """
    std::unique_ptr<Foo> ptr1;
    std::shared_ptr<Bar> ptr2;
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    assert "smart_pointers" in patterns
    assert len(patterns["smart_pointers"]) == 2

    types = [p["type"] for p in patterns["smart_pointers"]]
    assert "unique_ptr" in types
    assert "shared_ptr" in types


def test_no_patterns():
    """Test that no patterns are detected in plain code."""
    code = """
    int add(int a, int b) {
        return a + b;
    }
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    # Should still return the pattern keys, but with empty lists
    assert "raii_usage" in patterns
    assert "template_validation" in patterns
    assert "exception_patterns" in patterns
    assert "namespace_accessors" in patterns
    assert "smart_pointers" in patterns

    assert len(patterns["raii_usage"]) == 0
    assert len(patterns["template_validation"]) == 0
    assert len(patterns["exception_patterns"]) == 0
    assert len(patterns["namespace_accessors"]) == 0
    assert len(patterns["smart_pointers"]) == 0


def test_get_language_name():
    """Test that detector returns correct language name."""
    detector = CppPatternDetector()
    assert detector.get_language_name() == "cpp"


def test_false_positive_risk_included():
    """Test that false positive risks are included in patterns."""
    code = """
    std::unique_ptr<Foo> ptr = std::make_unique<Foo>();
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    assert "raii_usage" in patterns
    assert len(patterns["raii_usage"]) > 0

    # Check that false_positive_risk field exists
    for pattern in patterns["raii_usage"]:
        assert "false_positive_risk" in pattern
        assert isinstance(pattern["false_positive_risk"], str)
        assert len(pattern["false_positive_risk"]) > 0


def test_audit_implications_included():
    """Test that audit implications are included in patterns."""
    code = """
    std::unique_ptr<Foo> ptr = std::make_unique<Foo>();
    throw std::runtime_error("error");
    """

    detector = CppPatternDetector()
    patterns = detector.detect_patterns(code, "test.cpp", {})

    # Check RAII patterns
    assert "raii_usage" in patterns
    for pattern in patterns["raii_usage"]:
        assert "audit_implication" in pattern
        assert isinstance(pattern["audit_implication"], str)

    # Check exception patterns
    assert "exception_patterns" in patterns
    for pattern in patterns["exception_patterns"]:
        assert "audit_implication" in pattern
        assert isinstance(pattern["audit_implication"], str)
