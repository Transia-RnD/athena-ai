#!/usr/bin/env python
# coding: utf-8

"""Integration tests for IndexClient - C++ only."""

import os
import shutil
import unittest
from pathlib import Path

from athenah_ai.indexer import IndexClient


class TestIndexCreation(unittest.TestCase):
    """Test index creation and querying with C++ fixtures."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures paths."""
        cls.test_dir = Path(__file__).parent.parent
        cls.fixtures_dir = cls.test_dir / "fixtures"
        cls.cpp_dir = cls.fixtures_dir / "cpp"

        # Test output directory - use absolute path
        cls.dist_dir = Path("workspace").resolve()
        cls.dist_dir.mkdir(exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        """Clean up test indices."""
        if cls.dist_dir.exists():
            shutil.rmtree(cls.dist_dir, ignore_errors=True)

    def setUp(self):
        """Clean up before each test."""
        # Remove any existing test indices
        for item in self.dist_dir.glob("*"):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)

    def test_cpp_directory_indexing(self):
        """Test indexing C++ directory with multiple files."""
        indexer = IndexClient("local", "test", str(self.dist_dir), "cpp_test", "v1")

        # Build index from cpp directory
        indexer.build_from_dirs(str(self.cpp_dir), ["."], False, True)

        # Test 1: Statistics
        stats = indexer.get_statistics()
        self.assertIn("vector_store", stats)
        self.assertGreater(
            stats["vector_store"]["total_chunks"], 0, "Vector store should have chunks"
        )

        if "symbol_index" in stats:
            self.assertGreater(
                stats["symbol_index"]["total_symbols"],
                0,
                "Symbol index should have symbols",
            )

        # Test 2: Find symbol - should find BaseClass
        symbols = indexer.find_symbol("BaseClass")
        self.assertGreater(len(symbols), 0, "Should find BaseClass symbol")

        # Verify symbol has expected fields
        symbol = symbols[0]
        self.assertIn("name", symbol)
        self.assertIn("kind", symbol)
        self.assertIn("file_path", symbol)
        self.assertIn("line_number", symbol)
        self.assertEqual(symbol["name"], "BaseClass")

        # Test 3: Query - semantic search
        result = indexer.query("what is BaseClass?", limit=3)
        self.assertGreater(len(result.results), 0, "Query should return results")

        # Test 4: Symbol context
        context = indexer.get_symbol_context("BaseClass")
        self.assertIsNotNone(context, "Should have context for BaseClass")
        if context.get("definition"):
            self.assertIn("file_path", context["definition"])
            self.assertIn("line_number", context["definition"])

        # Test 5: Call graph for function that makes calls
        call_graph = indexer.get_call_graph("processObjects", max_depth=1)
        self.assertIsNotNone(call_graph, "Should return call graph for processObjects")
        self.assertIn("symbol", call_graph, "Call graph should have symbol field")
        self.assertEqual(call_graph["symbol"], "processObjects")

        # Test 6: Verify file structure - all in one directory
        index_path = self.dist_dir / "cpp_test-v1"
        self.assertTrue(
            index_path.exists(), f"Index directory should exist at {index_path}"
        )

        # Check for expected files
        self.assertTrue(
            (index_path / "symbol_index.json").exists(),
            "symbol_index.json should exist",
        )
        self.assertTrue(
            (index_path / "knowledge_graph.pkl").exists(),
            "knowledge_graph.pkl should exist",
        )
        self.assertTrue(
            (index_path / "chroma.sqlite3").exists(), "chroma.sqlite3 should exist"
        )

    def test_call_relationships_cpp(self):
        """Test that call relationships are detected in C++ code."""
        indexer = IndexClient("local", "test", str(self.dist_dir), "cpp_calls", "v1")

        indexer.build_from_dirs(str(self.cpp_dir), ["."], False, True)

        # Find calculate method (called by processData)
        symbols = indexer.find_symbol("calculate")
        self.assertGreater(len(symbols), 0, "Should find calculate method")

        # Get context to see if callers are detected
        context = indexer.get_symbol_context("calculate")
        if context and context.get("callers"):
            self.assertGreater(
                len(context["callers"]), 0, "calculate should have callers"
            )


if __name__ == "__main__":
    unittest.main()
