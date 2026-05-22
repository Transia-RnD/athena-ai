"""
Unit tests for validation pattern extraction.
"""

import pytest
from unittest.mock import Mock
from athenah_ai.labeler.validation_extractor import ValidationExtractor


def test_extract_validation_patterns_basic():
    """Test basic validation pattern extraction."""

    code = """
    STTx::STTx(Json::Value const& json) {
        if (json[jss::Fee].empty())
            throw parse_error("Fee required");
        if (!json[jss::Amount].isNumeric())
            throw parse_error("Amount must be numeric");
    }
    """

    language_patterns = {
        "template_validation": [
            {"namespace": "jss", "type": "namespace_accessor"}
        ]
    }

    # Mock client that returns valid JSON
    mock_client = Mock()
    mock_client.ask = Mock(return_value='''{
        "validations": [
            {
                "field": "Fee",
                "validated_by": "STTx::constructor",
                "location": "STTx::STTx",
                "validation_type": "format",
                "error_thrown": "parse_error",
                "validates": ["non-empty"],
                "confidence": 0.95
            },
            {
                "field": "Amount",
                "validated_by": "STTx::constructor",
                "location": "STTx::STTx",
                "validation_type": "type",
                "error_thrown": "parse_error",
                "validates": ["numeric"],
                "confidence": 0.90
            }
        ],
        "validation_architecture": {
            "framework": "json_template",
            "validation_layer": "entry_point",
            "auto_validated_fields": ["Fee", "Amount"]
        }
    }''')

    extractor = ValidationExtractor(mock_client)
    result = extractor.extract_validation_patterns(code, "test.cpp", language_patterns)

    # Verify structure
    assert "validations" in result
    assert "validation_architecture" in result

    # Verify validations
    assert len(result["validations"]) == 2

    # Verify first validation
    fee_validation = result["validations"][0]
    assert fee_validation["field"] == "Fee"
    assert fee_validation["validated_by"] == "STTx::constructor"
    assert fee_validation["validation_type"] == "format"
    assert fee_validation["error_thrown"] == "parse_error"

    # Verify architecture
    arch = result["validation_architecture"]
    assert arch["framework"] == "json_template"
    assert arch["validation_layer"] == "entry_point"
    assert "Fee" in arch["auto_validated_fields"]
    assert "Amount" in arch["auto_validated_fields"]


def test_build_context_with_raii():
    """Test context building with RAII patterns."""

    language_patterns = {
        "raii_usage": [
            {"type": "smart_pointer", "pointer_type": "std::unique_ptr"}
        ]
    }

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    context = extractor._build_context(language_patterns)

    assert "RAII" in context
    assert "smart pointers" in context


def test_build_context_with_template_validation():
    """Test context building with template validation patterns."""

    language_patterns = {
        "template_validation": [
            {"namespace": "jss", "type": "namespace_accessor"}
        ]
    }

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    context = extractor._build_context(language_patterns)

    assert "template-based validation" in context
    assert "jss::" in context


def test_build_context_with_exceptions():
    """Test context building with exception patterns."""

    language_patterns = {
        "exception_patterns": [
            {"type": "exception_throwing"}
        ]
    }

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    context = extractor._build_context(language_patterns)

    assert "exceptions for error handling" in context


def test_build_context_empty():
    """Test context building with no patterns."""

    language_patterns = {}

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    context = extractor._build_context(language_patterns)

    assert "No specific language patterns detected" in context


def test_parse_validation_response_valid_json():
    """Test parsing valid JSON response."""

    response = '''{
        "validations": [
            {"field": "test", "validated_by": "func"}
        ],
        "validation_architecture": {
            "framework": "test_framework"
        }
    }'''

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    result = extractor._parse_validation_response(response)

    assert "validations" in result
    assert "validation_architecture" in result
    assert len(result["validations"]) == 1
    assert result["validation_architecture"]["framework"] == "test_framework"


def test_parse_validation_response_with_markdown():
    """Test parsing JSON embedded in markdown."""

    response = '''Here's the analysis:

```json
{
    "validations": [
        {"field": "test"}
    ],
    "validation_architecture": {}
}
```

That's all!'''

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    result = extractor._parse_validation_response(response)

    # Should still extract JSON from within markdown
    assert "validations" in result
    assert "validation_architecture" in result


def test_parse_validation_response_invalid_json():
    """Test parsing invalid JSON response."""

    response = "This is not JSON at all"

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    result = extractor._parse_validation_response(response)

    # Should return empty structure
    assert result == {"validations": [], "validation_architecture": {}}


def test_parse_validation_response_missing_keys():
    """Test parsing JSON with missing keys."""

    response = '{"validations": []}'  # Missing validation_architecture

    mock_client = Mock()
    extractor = ValidationExtractor(mock_client)
    result = extractor._parse_validation_response(response)

    # Should add missing keys
    assert "validations" in result
    assert "validation_architecture" in result
    assert result["validation_architecture"] == {}


def test_extract_validation_patterns_handles_errors():
    """Test that extraction handles LLM errors gracefully."""

    code = "void test() {}"
    language_patterns = {}

    # Mock client that raises an exception
    mock_client = Mock()
    mock_client.ask = Mock(side_effect=Exception("LLM error"))

    extractor = ValidationExtractor(mock_client)
    result = extractor.extract_validation_patterns(code, "test.cpp", language_patterns)

    # Should return empty structure instead of crashing
    assert result == {"validations": [], "validation_architecture": {}}


def test_validation_extractor_truncates_long_code():
    """Test that extractor truncates code to 3000 chars."""

    # Create very long code
    code = "void test() {}\n" * 500  # Much longer than 3000 chars
    language_patterns = {}

    mock_client = Mock()
    mock_client.ask = Mock(return_value='{"validations": [], "validation_architecture": {}}')

    extractor = ValidationExtractor(mock_client)
    extractor.extract_validation_patterns(code, "test.cpp", language_patterns)

    # Check that the prompt passed to LLM was truncated
    call_args = mock_client.ask.call_args
    prompt = call_args[0][1]

    # The code in the prompt should be truncated to 3000 chars
    assert "CODE:" in prompt
    code_section = prompt.split("CODE:")[1].split("\n\n")[0]
    assert len(code_section) <= 3100  # 3000 + some buffer for newlines


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
