"""
Unit tests for code path documentation.
"""

import pytest
from unittest.mock import Mock
from athenah_ai.labeler.code_path_documenter import CodePathDocumenter


def test_document_code_paths_basic():
    """Test basic code path documentation."""

    code = """
    void apply(Transaction const& tx) {
        validateTx(tx);
        applyToLedger(tx);
    }

    void validateTx(Transaction const& tx) {
        STTx stTx(tx.getJson());
    }
    """

    validations = [
        {
            "field": "Fee",
            "validated_by": "STTx::constructor",
            "location": "STTx::STTx"
        }
    ]

    language_patterns = {
        "template_validation": [{"namespace": "jss"}]
    }

    functions = [
        {"name": "apply", "lineno": 2},
        {"name": "validateTx", "lineno": 7}
    ]

    mock_client = Mock()
    mock_client.ask = Mock(return_value='''{
        "call_chains": [
            {
                "entry_point": "apply",
                "call_chain": ["apply", "validateTx", "STTx::STTx"],
                "purpose": "Validates transaction before applying",
                "validation_points": ["STTx::STTx validates all fields"]
            }
        ],
        "data_flows": [
            {
                "field": "Fee",
                "origin": "JSON input",
                "flow": ["JSON", "STTx", "validate", "apply"],
                "transformations": ["Parsed as Amount"],
                "validated_at": "STTx::STTx"
            }
        ],
        "test_coverage_notes": "Tests exist in TxTest.cpp"
    }''')

    documenter = CodePathDocumenter(mock_client)
    result = documenter.document_code_paths(code, "test.cpp", validations, language_patterns, functions)

    # Verify structure
    assert "call_chains" in result
    assert "data_flows" in result
    assert "test_coverage_notes" in result

    # Verify call chains
    assert len(result["call_chains"]) == 1
    call_chain = result["call_chains"][0]
    assert call_chain["entry_point"] == "apply"
    assert "validateTx" in call_chain["call_chain"]

    # Verify data flows
    assert len(result["data_flows"]) == 1
    data_flow = result["data_flows"][0]
    assert data_flow["field"] == "Fee"
    assert data_flow["origin"] == "JSON input"

    # Verify test coverage notes
    assert "TxTest.cpp" in result["test_coverage_notes"]


def test_build_context_with_validations():
    """Test context building with validations."""

    validations = [
        {"field": "Fee", "validated_by": "test_func", "location": "test.cpp"},
        {"field": "Amount", "validated_by": "test_func", "location": "test.cpp"}
    ]

    language_patterns = {}
    functions = [{"name": "test_func", "lineno": 1}]

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    context = documenter._build_context(validations, language_patterns, functions)

    assert "VALIDATIONS" in context
    assert "Fee" in context
    assert "Amount" in context


def test_build_context_with_functions():
    """Test context building with functions."""

    validations = []
    language_patterns = {}
    functions = [
        {"name": "func1", "lineno": 1},
        {"name": "func2", "lineno": 5}
    ]

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    context = documenter._build_context(validations, language_patterns, functions)

    assert "FUNCTIONS" in context
    assert "func1" in context
    assert "func2" in context


def test_build_context_with_template_validation():
    """Test context building with template validation."""

    validations = []
    language_patterns = {
        "template_validation": [{"namespace": "jss"}]
    }
    functions = []

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    context = documenter._build_context(validations, language_patterns, functions)

    assert "TEMPLATE VALIDATION" in context
    assert "template-based validation" in context


def test_build_context_with_exceptions():
    """Test context building with exception patterns."""

    validations = []
    language_patterns = {
        "exception_patterns": [{"type": "exception_throwing"}]
    }
    functions = []

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    context = documenter._build_context(validations, language_patterns, functions)

    assert "ERROR HANDLING" in context
    assert "exceptions" in context


def test_parse_code_path_response_valid():
    """Test parsing valid code path response."""

    response = '''{
        "call_chains": [
            {"entry_point": "test", "call_chain": ["test"]}
        ],
        "data_flows": [
            {"field": "test", "origin": "input"}
        ],
        "test_coverage_notes": "Tests exist"
    }'''

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    result = documenter._parse_code_path_response(response)

    assert "call_chains" in result
    assert "data_flows" in result
    assert "test_coverage_notes" in result
    assert len(result["call_chains"]) == 1
    assert len(result["data_flows"]) == 1


def test_parse_code_path_response_with_markdown():
    """Test parsing code path response embedded in markdown."""

    response = '''Here's the documentation:

```json
{
    "call_chains": [],
    "data_flows": [],
    "test_coverage_notes": "Test notes"
}
```

Done!'''

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    result = documenter._parse_code_path_response(response)

    assert "call_chains" in result
    assert "data_flows" in result
    assert "test_coverage_notes" in result


def test_parse_code_path_response_invalid():
    """Test parsing invalid code path response."""

    response = "This is not JSON"

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    result = documenter._parse_code_path_response(response)

    assert result == {"call_chains": [], "data_flows": [], "test_coverage_notes": ""}


def test_parse_code_path_response_missing_keys():
    """Test parsing response with missing keys."""

    response = '{"call_chains": []}'

    mock_client = Mock()
    documenter = CodePathDocumenter(mock_client)
    result = documenter._parse_code_path_response(response)

    # Should add missing keys
    assert "call_chains" in result
    assert "data_flows" in result
    assert "test_coverage_notes" in result
    assert result["data_flows"] == []
    assert result["test_coverage_notes"] == ""


def test_document_code_paths_handles_errors():
    """Test that documentation handles LLM errors gracefully."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=Exception("LLM error"))

    documenter = CodePathDocumenter(mock_client)
    result = documenter.document_code_paths("code", "test.cpp", [], {}, [])

    # Should return empty structure instead of crashing
    assert result == {"call_chains": [], "data_flows": [], "test_coverage_notes": ""}


def test_code_path_documenter_truncates_long_code():
    """Test that documenter truncates code to 4000 chars."""

    # Create very long code
    code = "void test() {}\n" * 500  # Much longer than 4000 chars
    assert len(code) > 4000  # Verify code is indeed long

    mock_client = Mock()
    mock_client.ask = Mock(return_value='{"call_chains": [], "data_flows": [], "test_coverage_notes": ""}')

    documenter = CodePathDocumenter(mock_client)
    documenter.document_code_paths(code, "test.cpp", [], {}, [])

    # Check that the prompt passed to LLM was truncated
    call_args = mock_client.ask.call_args
    prompt = call_args[0][1]

    # The code in the prompt should be truncated to 4000 chars
    # Extract just the code section (between CODE: and \n\nDocument:)
    assert "CODE:" in prompt
    code_start = prompt.find("CODE:\n") + len("CODE:\n")
    code_end = prompt.find("\n\nDocument:", code_start)
    actual_code = prompt[code_start:code_end]

    # Should be truncated to 4000 chars
    assert len(actual_code) <= 4000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
