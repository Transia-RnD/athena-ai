"""
Integration test for complete Week 1+2+3 pipeline (language patterns + validations + FP patterns).
"""

import os
import json
import tempfile
from unittest.mock import Mock
from athenah_ai.labeler.processor import FileProcessor


def test_complete_pipeline():
    """Test complete Week 1+2+3 pipeline: language patterns → validations → FP patterns."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=[
        # Metadata extraction
        '''{
            "description": "Transaction validation with RAII and templates",
            "functions": [{"name": "validate", "args": ["json"], "lineno": 5}],
            "classes": [{"name": "STTx", "args": ["Json::Value"], "lineno": 2}],
            "namespaces": [],
            "args": []
        }''',
        # Validation extraction
        '''{
            "validations": [
                {
                    "field": "Fee",
                    "validated_by": "json_template::constructor",
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

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "transaction.cpp")
        with open(test_file, "w") as f:
            f.write("""
namespace ripple {
class STTx {
    STTx(Json::Value const& json) {
        std::unique_ptr<Foo> ptr = std::make_unique<Foo>();
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

        result_path = processor._process_file(test_file, "transaction.cpp", context=None)

        with open(result_path, "r") as f:
            metadata = json.load(f)

        # Verify Week 1: Language patterns
        assert "language_patterns" in metadata
        patterns = metadata["language_patterns"]
        assert len(patterns["raii_usage"]) > 0
        assert len(patterns["template_validation"]) > 0
        assert len(patterns["exception_patterns"]) > 0

        # Verify Week 2: Validations
        assert "validations" in metadata
        assert len(metadata["validations"]) == 1
        assert metadata["validations"][0]["field"] == "Fee"

        assert "validation_architecture" in metadata
        assert metadata["validation_architecture"]["framework"] == "json_template"

        # Verify Week 3: False positive patterns
        assert "false_positive_patterns" in metadata
        fp_patterns = metadata["false_positive_patterns"]
        assert len(fp_patterns) > 0

        # Check for specific FP patterns
        fp_types = [fp["issue_pattern"] for fp in fp_patterns]

        # Should have FPs from framework validation (Fee, Amount)
        framework_fps = [fp for fp in fp_types if "Fee" in fp or "Amount" in fp]
        assert len(framework_fps) > 0

        # Should have FPs from RAII (smart pointers)
        raii_fps = [fp for fp in fp_types if "null check" in fp.lower() or "memory leak" in fp.lower()]
        assert len(raii_fps) > 0

        # Should have FPs from exceptions
        exception_fps = [fp for fp in fp_types if "error return" in fp.lower()]
        assert len(exception_fps) > 0

        # Should have FPs from namespace accessors
        namespace_fps = [fp for fp in fp_types if "jss" in fp.lower()]
        assert len(namespace_fps) > 0

        print(f"✓ Complete pipeline tested")
        print(f"  - Language patterns: {list(patterns.keys())}")
        print(f"  - Validations: {len(metadata['validations'])}")
        print(f"  - FP patterns: {len(fp_patterns)}")
        print(f"  - FP categories detected: framework, RAII, exceptions, namespaces")


def test_fp_pattern_structure():
    """Test that FP patterns have correct structure."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=[
        '{"description": "test", "functions": [], "classes": [], "namespaces": [], "args": []}',
        '{"validations": [{"field": "Fee", "validated_by": "test", "location": "test", "validation_type": "format", "confidence": 0.9}], "validation_architecture": {"framework": "test", "auto_validated_fields": ["Fee"]}}'
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.cpp")
        with open(test_file, "w") as f:
            f.write("std::unique_ptr<Foo> ptr;\nthrow std::runtime_error(\"err\");")

        processor = FileProcessor(
            client=mock_client,
            language_extensions={".cpp": "cpp"},
            source_path=temp_dir,
            checkpoint_path=os.path.join(temp_dir, "checkpoint.json"),
            checkpoint_interval=10,
            retry_with_backoff=lambda f, max_retries=3: f(),
            report_progress=lambda x: None,
        )

        result_path = processor._process_file(test_file, "test.cpp", context=None)

        with open(result_path, "r") as f:
            metadata = json.load(f)

        fp_patterns = metadata["false_positive_patterns"]

        # All FP patterns should have required fields
        for fp in fp_patterns:
            assert "issue_pattern" in fp
            assert "why_false_positive" in fp
            assert "detection_keywords" in fp
            assert "confidence" in fp
            assert "applies_to" in fp
            assert "evidence" in fp

            # Verify types
            assert isinstance(fp["issue_pattern"], str)
            assert isinstance(fp["why_false_positive"], str)
            assert isinstance(fp["detection_keywords"], list)
            assert isinstance(fp["confidence"], (int, float))
            assert isinstance(fp["applies_to"], list)
            assert isinstance(fp["evidence"], str)

            # Verify values
            assert len(fp["issue_pattern"]) > 0
            assert len(fp["why_false_positive"]) > 0
            assert len(fp["detection_keywords"]) >= 2
            assert 0.0 <= fp["confidence"] <= 1.0
            assert len(fp["applies_to"]) > 0

        print(f"✓ All {len(fp_patterns)} FP patterns have correct structure")


def test_fp_pattern_categories():
    """Test that FP patterns are generated from all sources."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=[
        '{"description": "test", "functions": [], "classes": [], "namespaces": [], "args": []}',
        '{"validations": [{"field": "Fee", "validated_by": "framework", "location": "test", "validation_type": "format", "confidence": 0.9}], "validation_architecture": {"framework": "test_framework", "auto_validated_fields": ["Fee"]}}'
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.cpp")
        with open(test_file, "w") as f:
            f.write("""
std::unique_ptr<Foo> ptr;
std::lock_guard<std::mutex> lock(mtx);
throw std::runtime_error("err");
auto x = obj[jss::Field];
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

        result_path = processor._process_file(test_file, "test.cpp", context=None)

        with open(result_path, "r") as f:
            metadata = json.load(f)

        fp_patterns = metadata["false_positive_patterns"]

        # Categorize FPs by source
        framework_fps = [fp for fp in fp_patterns if "Fee" in fp["issue_pattern"] or "framework" in fp["why_false_positive"].lower()]
        raii_fps = [fp for fp in fp_patterns if "smart pointer" in fp["why_false_positive"].lower() or "lock_guard" in fp.get("evidence", "")]
        exception_fps = [fp for fp in fp_patterns if "exception" in fp["why_false_positive"].lower()]
        namespace_fps = [fp for fp in fp_patterns if "jss" in fp.get("evidence", "").lower() or "namespace" in fp["why_false_positive"].lower()]

        # Should have FPs from all categories
        assert len(framework_fps) > 0, "Should have framework validation FPs"
        assert len(raii_fps) > 0, "Should have RAII FPs"
        assert len(exception_fps) > 0, "Should have exception FPs"
        assert len(namespace_fps) > 0, "Should have namespace FPs"

        print(f"✓ FP patterns from all categories:")
        print(f"  - Framework: {len(framework_fps)}")
        print(f"  - RAII: {len(raii_fps)}")
        print(f"  - Exceptions: {len(exception_fps)}")
        print(f"  - Namespaces: {len(namespace_fps)}")


if __name__ == "__main__":
    test_complete_pipeline()
    test_fp_pattern_structure()
    test_fp_pattern_categories()
    print("\n✅ All integration tests passed!")
