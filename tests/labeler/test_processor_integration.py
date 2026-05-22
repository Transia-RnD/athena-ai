"""
Integration test for language pattern detection in processor.
"""

import os
import json
import tempfile
from unittest.mock import Mock
from athenah_ai.labeler.processor import FileProcessor


def test_processor_detects_cpp_patterns():
    """Test that FileProcessor detects C++ patterns and includes them in .ai.json."""

    # Create a mock client that returns valid JSON
    mock_client = Mock()
    mock_client.ask = Mock(return_value='''{
        "description": "Test file with smart pointers",
        "functions": [{"name": "test_func", "args": [], "lineno": 2}],
        "classes": [],
        "namespaces": [],
        "args": []
    }''')

    # Create a temporary directory and test file
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.cpp")
        with open(test_file, "w") as f:
            f.write("""
void test_func() {
    std::unique_ptr<Foo> ptr = std::make_unique<Foo>();
    auto fee = tx[jss::Fee];
    throw std::runtime_error("error");
}
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

        # Check that C++ patterns were detected
        patterns = metadata["language_patterns"]
        assert "raii_usage" in patterns
        assert "template_validation" in patterns
        assert "exception_patterns" in patterns
        assert "namespace_accessors" in patterns
        assert "smart_pointers" in patterns

        # Check that specific patterns were detected
        assert len(patterns["raii_usage"]) > 0, "Should detect std::unique_ptr"
        assert len(patterns["template_validation"]) > 0, "Should detect jss:: namespace"
        assert len(patterns["exception_patterns"]) > 0, "Should detect throw statement"

        print(f"✓ Language patterns detected: {list(patterns.keys())}")
        print(f"✓ RAII patterns: {len(patterns['raii_usage'])}")
        print(f"✓ Template validation: {len(patterns['template_validation'])}")
        print(f"✓ Exception patterns: {len(patterns['exception_patterns'])}")


def test_processor_skips_pattern_detection_for_non_cpp():
    """Test that processor doesn't run C++ pattern detection on non-C++ files."""

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

        # Python doesn't have a detector yet, so language_patterns should not exist
        # or should be empty
        if "language_patterns" in metadata:
            assert metadata["language_patterns"] == {}, "No detector for Python yet"

        print("✓ No C++ patterns detected for Python file")


if __name__ == "__main__":
    test_processor_detects_cpp_patterns()
    test_processor_skips_pattern_detection_for_non_cpp()
    print("\n✅ All integration tests passed!")
