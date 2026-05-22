"""
Integration test for complete Week 1+2+3+4 pipeline.
"""

import os
import json
import tempfile
from unittest.mock import Mock
from athenah_ai.labeler.processor import FileProcessor


def test_complete_week1234_pipeline():
    """Test complete Week 1+2+3+4 pipeline: patterns → validations → FPs → code paths."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=[
        # Metadata extraction
        '''{
            "description": "Transaction validation system",
            "functions": [{"name": "apply", "args": ["tx"], "lineno": 2}, {"name": "validateTx", "args": ["tx"], "lineno": 7}],
            "classes": [{"name": "STTx", "args": ["Json::Value"], "lineno": 12}],
            "namespaces": [],
            "args": []
        }''',
        # Validation extraction
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
        }''',
        # Code path documentation
        '''{
            "call_chains": [
                {
                    "entry_point": "apply",
                    "call_chain": ["apply", "validateTx", "STTx::STTx"],
                    "purpose": "Validates transaction before applying to ledger",
                    "validation_points": ["STTx::STTx validates all JSON fields"]
                }
            ],
            "data_flows": [
                {
                    "field": "Fee",
                    "origin": "JSON transaction input",
                    "flow": ["JSON", "STTx::STTx", "validate", "apply", "ledger"],
                    "transformations": ["Parsed as Amount", "Validated for positive value"],
                    "validated_at": "STTx::STTx constructor"
                }
            ],
            "test_coverage_notes": "Tests exist in TxTest.cpp. No edge case tests for zero Fee."
        }'''
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "apply.cpp")
        with open(test_file, "w") as f:
            f.write("""
void apply(Transaction const& tx) {
    std::unique_ptr<TxData> data = std::make_unique<TxData>();
    validateTx(tx);
    applyToLedger(tx);
}

void validateTx(Transaction const& tx) {
    if (!tx.isValid()) throw std::runtime_error("Invalid tx");
    STTx stTx(tx.getJson());
    auto fee = stTx[jss::Fee];
}

class STTx {
    STTx(Json::Value const& json) {
        validateFields(json);
    }
};
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

        result_path = processor._process_file(test_file, "apply.cpp", context=None)

        with open(result_path, "r") as f:
            metadata = json.load(f)

        # Verify Week 1: Language patterns
        assert "language_patterns" in metadata
        patterns = metadata["language_patterns"]
        assert len(patterns["raii_usage"]) > 0
        assert len(patterns["exception_patterns"]) > 0

        # Verify Week 2: Validations
        assert "validations" in metadata
        assert len(metadata["validations"]) == 1
        assert metadata["validations"][0]["field"] == "Fee"

        assert "validation_architecture" in metadata
        assert metadata["validation_architecture"]["framework"] == "json_template"

        # Verify Week 3: FP patterns
        assert "false_positive_patterns" in metadata
        fp_patterns = metadata["false_positive_patterns"]
        assert len(fp_patterns) > 0

        # Verify Week 4: Code paths
        assert "code_paths" in metadata
        assert "data_flows" in metadata
        assert "test_coverage_notes" in metadata

        code_paths = metadata["code_paths"]
        assert len(code_paths) == 1
        assert code_paths[0]["entry_point"] == "apply"
        assert "validateTx" in code_paths[0]["call_chain"]

        data_flows = metadata["data_flows"]
        assert len(data_flows) == 1
        assert data_flows[0]["field"] == "Fee"
        assert data_flows[0]["origin"] == "JSON transaction input"

        test_notes = metadata["test_coverage_notes"]
        assert "TxTest.cpp" in test_notes

        print(f"✓ Complete Week 1+2+3+4 pipeline tested")
        print(f"  - Language patterns: {list(patterns.keys())}")
        print(f"  - Validations: {len(metadata['validations'])}")
        print(f"  - FP patterns: {len(fp_patterns)}")
        print(f"  - Code paths: {len(code_paths)}")
        print(f"  - Data flows: {len(data_flows)}")
        print(f"  - Test coverage: documented")


def test_complete_enhanced_schema():
    """Test the complete enhanced .ai.json schema with all Week 1-4 fields."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=[
        '{"description": "test", "functions": [{"name": "test", "lineno": 1}], "classes": [], "namespaces": [], "args": []}',
        '{"validations": [{"field": "Fee", "validated_by": "test", "location": "test", "validation_type": "format", "confidence": 0.9}], "validation_architecture": {"framework": "test", "auto_validated_fields": ["Fee"]}}',
        '{"call_chains": [{"entry_point": "test", "call_chain": ["test"], "purpose": "test", "validation_points": ["test"]}], "data_flows": [{"field": "Fee", "origin": "input", "flow": ["input", "test"], "transformations": ["parsed"], "validated_at": "test"}], "test_coverage_notes": "Tests exist"}'
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

        # Verify complete schema has all fields from Week 1-4
        required_fields = [
            "file_path",
            "description",
            "language",
            "functions",
            "classes",
            "namespaces",
            "args",
            "language_patterns",  # Week 1
            "validations",  # Week 2
            "validation_architecture",  # Week 2
            "false_positive_patterns",  # Week 3
            "code_paths",  # Week 4
            "data_flows",  # Week 4
            "test_coverage_notes"  # Week 4
        ]

        for field in required_fields:
            assert field in metadata, f"Missing field: {field}"

        print("✓ Complete enhanced .ai.json schema verified")
        print(f"  - All {len(required_fields)} required fields present")


def test_code_path_data_flow_structure():
    """Test that code paths and data flows have correct structure."""

    mock_client = Mock()
    mock_client.ask = Mock(side_effect=[
        '{"description": "test", "functions": [{"name": "test", "lineno": 1}], "classes": [], "namespaces": [], "args": []}',
        '{"validations": [{"field": "Fee", "validated_by": "test", "location": "test", "validation_type": "format", "confidence": 0.9}], "validation_architecture": {"framework": "test"}}',
        '{"call_chains": [{"entry_point": "apply", "call_chain": ["apply", "validate"], "purpose": "Validate tx", "validation_points": ["validate"]}], "data_flows": [{"field": "Fee", "origin": "JSON", "flow": ["JSON", "parse", "validate"], "transformations": ["parsed"], "validated_at": "validate"}], "test_coverage_notes": "Tests in TxTest.cpp"}'
    ])

    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.cpp")
        with open(test_file, "w") as f:
            f.write("void test() {}")

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

        # Verify code path structure
        assert "code_paths" in metadata
        for call_chain in metadata["code_paths"]:
            assert "entry_point" in call_chain
            assert "call_chain" in call_chain
            assert "purpose" in call_chain
            assert "validation_points" in call_chain

            assert isinstance(call_chain["entry_point"], str)
            assert isinstance(call_chain["call_chain"], list)
            assert isinstance(call_chain["purpose"], str)
            assert isinstance(call_chain["validation_points"], list)

        # Verify data flow structure
        assert "data_flows" in metadata
        for data_flow in metadata["data_flows"]:
            assert "field" in data_flow
            assert "origin" in data_flow
            assert "flow" in data_flow
            assert "transformations" in data_flow
            assert "validated_at" in data_flow

            assert isinstance(data_flow["field"], str)
            assert isinstance(data_flow["origin"], str)
            assert isinstance(data_flow["flow"], list)
            assert isinstance(data_flow["transformations"], list)
            assert isinstance(data_flow["validated_at"], str)

        # Verify test coverage notes
        assert isinstance(metadata["test_coverage_notes"], str)

        print("✓ Code paths and data flows have correct structure")


if __name__ == "__main__":
    test_complete_week1234_pipeline()
    test_complete_enhanced_schema()
    test_code_path_data_flow_structure()
    print("\n✅ All integration tests passed!")
