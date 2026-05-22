"""
Integration test for validation pattern extraction in processor.
"""

import os
import json
import tempfile
from unittest.mock import Mock
from athenah_ai.labeler.processor import FileProcessor


def test_processor_extracts_validations():
    """Test that FileProcessor extracts validations and includes them in .ai.json."""

    # Create a mock client that returns valid JSON for both metadata and validation
    mock_client = Mock()

    # First call: metadata extraction
    # Second call: validation extraction
    mock_client.ask = Mock(side_effect=[
        # Metadata extraction response
        '''{
            "description": "Test file with validation",
            "functions": [{"name": "validate", "args": ["json"], "lineno": 2}],
            "classes": [{"name": "STTx", "args": ["Json::Value"], "lineno": 1}],
            "namespaces": [],
            "args": []
        }''',
        # Validation extraction response
        '''{
            "validations": [
                {
                    "field": "Fee",
                    "validated_by": "STTx::constructor",
                    "location": "STTx::STTx",
                    "validation_type": "format",
                    "error_thrown": "parse_error",
                    "validates": ["non-empty", "numeric"],
                    "confidence": 0.95
                }
            ],
            "validation_architecture": {
                "framework": "json_template",
                "validation_layer": "entry_point",
                "auto_validated_fields": ["Fee", "Amount"]
            }
        }'''
    ])

    # Create a temporary directory and test file
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.cpp")
        with open(test_file, "w") as f:
            f.write("""
class STTx {
    STTx(Json::Value const& json) {
        if (json[jss::Fee].empty())
            throw parse_error("Fee required");
    }
};
""")

        # Create processor
        processor = FileProcessor(
            client=mock_client,
            language_extensions={".cpp": "cpp", ".h": "cpp"},
            source_path=temp_dir,
            checkpoint_path=os.path.join(temp_dir, "checkpoint.json"),
            checkpoint_interval=10,
            retry_with_backoff=lambda f, max_retries=3: f(),
            report_progress=lambda x: None,
        )

        # Process the file
        result_path = processor._process_file(test_file, "test.cpp", context=None)

        # Verify the .ai.json file was created
        assert result_path.endswith(".ai.json")
        assert os.path.exists(result_path)

        # Read and verify the contents
        with open(result_path, "r") as f:
            metadata = json.load(f)

        # Check that language_patterns field exists
        assert "language_patterns" in metadata, "language_patterns field should exist"

        # Check that validations field exists
        assert "validations" in metadata, "validations field should exist"
        assert "validation_architecture" in metadata, "validation_architecture field should exist"

        # Check validation content
        validations = metadata["validations"]
        assert len(validations) == 1, "Should have 1 validation"

        validation = validations[0]
        assert validation["field"] == "Fee"
        assert validation["validated_by"] == "STTx::constructor"
        assert validation["validation_type"] == "format"
        assert validation["error_thrown"] == "parse_error"
        assert validation["confidence"] == 0.95

        # Check validation architecture
        arch = metadata["validation_architecture"]
        assert arch["framework"] == "json_template"
        assert arch["validation_layer"] == "entry_point"
        assert "Fee" in arch["auto_validated_fields"]

        print(f"✓ Validations extracted: {len(validations)}")
        print(f"✓ Validation architecture detected: {arch['framework']}")
        print(f"✓ Auto-validated fields: {arch['auto_validated_fields']}")


def test_processor_skips_validation_without_language_patterns():
    """Test that processor doesn't extract validations if no language patterns."""

    mock_client = Mock()
    mock_client.ask = Mock(return_value='''{
        "description": "Python file",
        "functions": [{"name": "test", "args": [], "lineno": 1}],
        "classes": [],
        "namespaces": [],
        "args": []
    }''')

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, "w") as f:
            f.write("def test():\n    pass\n")

        processor = FileProcessor(
            client=mock_client,
            language_extensions={".py": "python"},
            source_path=temp_dir,
            checkpoint_path=os.path.join(temp_dir, "checkpoint.json"),
            checkpoint_interval=10,
            retry_with_backoff=lambda f, max_retries=3: f(),
            report_progress=lambda x: None,
        )

        result_path = processor._process_file(test_file, "test.py", context=None)

        with open(result_path, "r") as f:
            metadata = json.load(f)

        # Python doesn't have a detector yet, so no language patterns
        # Therefore, no validation extraction should happen
        assert "validations" not in metadata or metadata["validations"] == []
        assert "validation_architecture" not in metadata or metadata["validation_architecture"] == {}

        print("✓ No validation extraction for Python file (no language patterns)")


def test_enhanced_ai_json_schema():
    """Test the complete enhanced .ai.json schema with all new fields."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=[
        # Metadata extraction
        '''{
            "description": "JSON template validation engine",
            "functions": [{"name": "validate", "args": ["json"], "lineno": 5}],
            "classes": [{"name": "STTx", "args": ["Json::Value"], "lineno": 1}],
            "namespaces": [{"name": "ripple", "lineno": 1}],
            "args": []
        }''',
        # Validation extraction
        '''{
            "validations": [
                {
                    "field": "Fee",
                    "validated_by": "json_template",
                    "location": "STTx::STTx",
                    "validation_type": "format",
                    "error_thrown": "parse_error",
                    "validates": ["non-empty", "numeric", "positive"],
                    "confidence": 0.95
                },
                {
                    "field": "Amount",
                    "validated_by": "json_template",
                    "location": "STTx::STTx",
                    "validation_type": "type",
                    "error_thrown": "parse_error",
                    "validates": ["valid amount format"],
                    "confidence": 0.90
                }
            ],
            "validation_architecture": {
                "framework": "json_template",
                "validation_layer": "entry_point",
                "auto_validated_fields": ["Fee", "Amount", "Destination"]
            }
        }'''
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "json_template.cpp")
        with open(test_file, "w") as f:
            f.write("""
namespace ripple {
class STTx {
    STTx(Json::Value const& json) {
        auto fee = json[jss::Fee];
        if (fee.empty()) throw parse_error("Fee required");
    }
};
}
""")

        processor = FileProcessor(
            client=mock_client,
            language_extensions={".cpp": "cpp"},
            source_path=temp_dir,
            checkpoint_path=os.path.join(temp_dir, "checkpoint.json"),
            checkpoint_interval=10,
            retry_with_backoff=lambda f, max_retries=3: f(),
            report_progress=lambda x: None,
        )

        result_path = processor._process_file(test_file, "json_template.cpp", context=None)

        with open(result_path, "r") as f:
            metadata = json.load(f)

        # Verify complete schema
        assert "file_path" in metadata
        assert "description" in metadata
        assert "language" in metadata
        assert "functions" in metadata
        assert "classes" in metadata
        assert "namespaces" in metadata
        assert "language_patterns" in metadata
        assert "validations" in metadata
        assert "validation_architecture" in metadata

        # Verify language patterns
        patterns = metadata["language_patterns"]
        assert len(patterns["template_validation"]) > 0
        assert len(patterns["exception_patterns"]) > 0

        # Verify validations
        validations = metadata["validations"]
        assert len(validations) == 2
        assert validations[0]["field"] == "Fee"
        assert validations[1]["field"] == "Amount"

        # Verify architecture
        arch = metadata["validation_architecture"]
        assert arch["framework"] == "json_template"
        assert len(arch["auto_validated_fields"]) == 3

        print("✓ Complete enhanced .ai.json schema verified")
        print(f"  - Language patterns: {list(patterns.keys())}")
        print(f"  - Validations: {len(validations)}")
        print(f"  - Framework: {arch['framework']}")


if __name__ == "__main__":
    test_processor_extracts_validations()
    test_processor_skips_validation_without_language_patterns()
    test_enhanced_ai_json_schema()
    print("\n✅ All integration tests passed!")
