#!/usr/bin/env python
# coding: utf-8

"""
Athenah AI Indexer - Hybrid RAG System.

V2.0: Complete rewrite with hybrid architecture:
- Symbol Index (O(1) exact lookups)
- Knowledge Graph (structural relationships)
- Vector Store (semantic similarity)

BREAKING CHANGE: V1.x indexes are incompatible and must be regenerated.
"""

from dotenv import load_dotenv

from athenah_ai.indexer.index_client import IndexClient, create_indexer

load_dotenv()

# Version marker for detecting old indexes
INDEXER_VERSION = "2.0.0"


# Export main classes
__all__ = [
    'IndexClient',
    'create_indexer',
    'INDEXER_VERSION'
]
