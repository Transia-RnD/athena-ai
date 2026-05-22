"""
Hybrid Query Engine - Combines Symbol Index, Knowledge Graph, and Vector Store.

Intelligently routes queries to the optimal search method:
- Exact match -> Symbol Index (O(1))
- Structural query -> Knowledge Graph (graph traversal)
- Semantic search -> Vector Store (embedding similarity)
- Complex query -> Combined multi-stage search
"""

import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging
import re

from athenah_ai.indexer.symbol_index import SymbolIndex
from athenah_ai.indexer.knowledge_graph import CodeKnowledgeGraph, is_knowledge_graph_available
from athenah_ai.indexer.base_index_client import BaseIndexClient

logger = logging.getLogger("app")


class QueryType(Enum):
    """Type of query based on intent."""
    EXACT_MATCH = "exact"  # "find function foo"
    STRUCTURAL = "structural"  # "what calls foo?", "show inheritance"
    SEMANTIC = "semantic"  # "find similar error handling"
    HYBRID = "hybrid"  # Complex queries combining multiple types


@dataclass
class QueryResult:
    """Result from hybrid query."""
    query: str
    query_type: QueryType
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    execution_time_ms: float


class HybridQueryEngine:
    """
    Intelligent query engine combining 3 search layers.

    Architecture:
    1. Symbol Index: Fast exact lookups (O(1))
    2. Knowledge Graph: Structural queries (graph traversal)
    3. Vector Store: Semantic similarity (embedding search)
    """

    def __init__(
        self,
        symbol_index: SymbolIndex,
        knowledge_graph: Optional[CodeKnowledgeGraph],
        vector_store: Optional[BaseIndexClient]
    ):
        """
        Initialize hybrid query engine.

        Args:
            symbol_index: Symbol index for exact matches
            knowledge_graph: Knowledge graph for structural queries
            vector_store: Vector store for semantic search
        """
        self.symbol_index = symbol_index
        self.knowledge_graph = knowledge_graph
        self.vector_store = vector_store

        # Query pattern matchers
        self._structural_patterns = {
            r'what calls? (\w+)': 'find_callers',
            r'who calls? (\w+)': 'find_callers',
            r'(?:what|who) (?:does|do) (\w+) calls?': 'find_callees',
            r'(?:show|get) (?:the )?inheritance (?:tree|hierarchy) (?:for|of) (\w+)': 'inheritance_tree',
            r'(?:what|which) (?:classes? )?(?:inherit|extends?) (?:from )?(\w+)': 'find_descendants',
            r'(?:what|which) (?:is|are) (?:the )?(?:parent|base) (?:classes? )?(?:of |for )?(\w+)': 'find_ancestors',
            r'(?:show|get) (?:the )?dependencies (?:for|of) (.+)': 'file_dependencies',
            r'(?:show|get) (?:the )?call graph (?:for|of) (\w+)': 'call_graph',
        }

        self._exact_patterns = {
            r'find (?:function|method|class|symbol) (\w+)': 'find_exact',
            r'(?:go to|jump to|show) (?:definition|declaration) (?:of )?(\w+)': 'find_exact',
            r'(?:where (?:is|are)) (\w+)': 'find_exact',
        }

        logger.info("Hybrid query engine initialized")

    def query(self, query_text: str, **kwargs) -> QueryResult:
        """
        Execute a hybrid query.

        Args:
            query_text: Natural language query
            **kwargs: Additional query parameters (limit, filters, etc.)

        Returns:
            QueryResult with results and metadata
        """
        import time
        start_time = time.time()

        # Classify query type
        query_type, method, params = self._classify_query(query_text)

        # Route to appropriate search method
        if query_type == QueryType.EXACT_MATCH:
            results = self._execute_exact_query(method, params, **kwargs)
        elif query_type == QueryType.STRUCTURAL:
            results = self._execute_structural_query(method, params, **kwargs)
        elif query_type == QueryType.SEMANTIC:
            results = self._execute_semantic_query(query_text, **kwargs)
        else:  # HYBRID
            results = self._execute_hybrid_query(query_text, **kwargs)

        execution_time = (time.time() - start_time) * 1000  # Convert to ms

        return QueryResult(
            query=query_text,
            query_type=query_type,
            results=results,
            metadata={
                'method': method,
                'params': params,
                'result_count': len(results)
            },
            execution_time_ms=execution_time
        )

    def _classify_query(self, query_text: str) -> Tuple[QueryType, Optional[str], Dict[str, Any]]:
        """
        Classify query type and extract parameters.

        Returns:
            (query_type, method, params)
        """
        query_lower = query_text.lower()

        # Check structural patterns
        for pattern, method in self._structural_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                return (QueryType.STRUCTURAL, method, {'symbol': match.group(1)})

        # Check exact match patterns
        for pattern, method in self._exact_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                return (QueryType.EXACT_MATCH, method, {'symbol': match.group(1)})

        # Check for semantic indicators
        semantic_keywords = ['similar', 'like', 'patterns', 'examples', 'related']
        if any(keyword in query_lower for keyword in semantic_keywords):
            return (QueryType.SEMANTIC, 'semantic_search', {})

        # Default to semantic for unstructured queries
        return (QueryType.SEMANTIC, 'semantic_search', {})

    # ========== Exact Match Queries ==========

    def _execute_exact_query(self, method: str, params: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Execute exact match query using symbol index."""
        symbol_name = params.get('symbol')
        if not symbol_name:
            return []

        logger.debug(f"Exact query: {method} for symbol '{symbol_name}'")

        if method == 'find_exact':
            # Try qualified name first
            result = self.symbol_index.find_qualified(symbol_name)
            if result:
                return [result]

            # Fall back to name search
            return self.symbol_index.find_exact(symbol_name)

        return []

    # ========== Structural Queries ==========

    def _execute_structural_query(self, method: str, params: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Execute structural query using knowledge graph."""
        if not self.knowledge_graph:
            logger.warning("Knowledge graph not available for structural query")
            return []

        symbol_name = params.get('symbol')
        if not symbol_name:
            return []

        logger.debug(f"Structural query: {method} for symbol '{symbol_name}'")

        if method == 'find_callers':
            return self.knowledge_graph.find_callers(symbol_name)

        elif method == 'find_callees':
            return self.knowledge_graph.find_callees(symbol_name)

        elif method == 'inheritance_tree':
            tree = self.knowledge_graph.get_inheritance_tree(symbol_name, 'ancestors')
            return [tree] if tree else []

        elif method == 'find_descendants':
            tree = self.knowledge_graph.get_inheritance_tree(symbol_name, 'descendants')
            return [tree] if tree else []

        elif method == 'find_ancestors':
            tree = self.knowledge_graph.get_inheritance_tree(symbol_name, 'ancestors')
            return [tree] if tree else []

        elif method == 'file_dependencies':
            deps = self.knowledge_graph.get_file_dependencies(symbol_name)
            return [deps]

        elif method == 'call_graph':
            max_depth = kwargs.get('max_depth', 2)
            graph = self.knowledge_graph.get_call_graph(symbol_name, max_depth)
            return [graph] if graph else []

        return []

    # ========== Semantic Queries ==========

    def _execute_semantic_query(self, query_text: str, **kwargs) -> List[Dict[str, Any]]:
        """Execute semantic query using vector store."""
        if not self.vector_store:
            logger.warning("Vector store not available for semantic query")
            return []

        logger.debug(f"Semantic query: '{query_text}'")

        limit = kwargs.get('limit', 5)
        filter_metadata = kwargs.get('filter', None)

        # Use vector store search
        results = self.vector_store.search(
            query=query_text,
            limit=limit,
            filter_metadata=filter_metadata
        )

        return results

    # ========== Hybrid Queries ==========

    def _execute_hybrid_query(self, query_text: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute hybrid query combining multiple search methods.

        Strategy:
        1. Try exact match first (fastest)
        2. If no results, try structural query
        3. Fall back to semantic search
        4. Merge and rank results
        """
        logger.debug(f"Hybrid query: '{query_text}'")

        all_results = []
        limit = kwargs.get('limit', 10)

        # Stage 1: Try exact/fuzzy symbol match
        fuzzy_results = self.symbol_index.fuzzy_search(query_text, limit=5)
        for result in fuzzy_results:
            result['source'] = 'symbol_index'
            result['relevance_score'] = 1.0  # Exact/fuzzy match is highly relevant
        all_results.extend(fuzzy_results)

        # Stage 2: Semantic search in vector store
        if self.vector_store:
            semantic_results = self.vector_store.search(query_text, limit=limit)
            for result in semantic_results:
                result['source'] = 'vector_store'
                result['relevance_score'] = result.get('score', 0.5)
            all_results.extend(semantic_results)

        # Stage 3: If we have symbol results, enrich with structural data
        if self.knowledge_graph and fuzzy_results:
            for symbol_result in fuzzy_results[:3]:  # Top 3 symbols
                symbol_name = symbol_result['qualified_name']

                # Get callers/callees
                callers = self.knowledge_graph.find_callers(symbol_name)
                if callers:
                    symbol_result['callers'] = callers[:5]

                callees = self.knowledge_graph.find_callees(symbol_name)
                if callees:
                    symbol_result['callees'] = callees[:5]

        # Deduplicate and sort by relevance
        seen = set()
        unique_results = []
        for result in all_results:
            # Create unique key
            key = result.get('qualified_name') or result.get('file_path', '') + str(result.get('line_start', ''))
            if key not in seen:
                seen.add(key)
                unique_results.append(result)

        # Sort by relevance score
        unique_results.sort(key=lambda r: r.get('relevance_score', 0), reverse=True)

        return unique_results[:limit]

    # ========== Convenience Methods ==========

    def find_symbol(self, name: str, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find symbol by name.

        Args:
            name: Symbol name
            kind: Optional kind filter

        Returns:
            List of matching symbols
        """
        results = self.symbol_index.find_exact(name)

        if kind:
            results = [r for r in results if r['kind'] == kind]

        return results

    def find_similar_code(self, code_snippet: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Find code similar to a snippet.

        Args:
            code_snippet: Code to find similar patterns for
            limit: Maximum results

        Returns:
            List of similar code chunks
        """
        if not self.vector_store:
            return []

        return self.vector_store.search(code_snippet, limit=limit)

    def get_symbol_context(self, symbol_name: str) -> Dict[str, Any]:
        """
        Get full context for a symbol (definition + relationships + similar code).

        Args:
            symbol_name: Symbol to get context for

        Returns:
            Dictionary with comprehensive symbol context
        """
        context = {}

        # Get definition from symbol index
        symbols = self.symbol_index.find_exact(symbol_name)
        if symbols:
            context['definition'] = symbols[0]

        # Get relationships from knowledge graph
        if self.knowledge_graph:
            context['callers'] = self.knowledge_graph.find_callers(symbol_name)
            context['callees'] = self.knowledge_graph.find_callees(symbol_name)

            # Check if it's a class
            symbol = symbols[0] if symbols else None
            if symbol and symbol['kind'] in ['class', 'struct']:
                context['inheritance'] = self.knowledge_graph.get_inheritance_tree(symbol_name, 'ancestors')
                context['descendants'] = self.knowledge_graph.get_inheritance_tree(symbol_name, 'descendants')

        # Get similar code from vector store
        if self.vector_store and symbols:
            # Use signature if available, otherwise use symbol name
            signature = symbols[0].get('signature') or symbol_name
            context['similar_code'] = self.vector_store.search(signature, limit=3)

        return context

    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions.

        Args:
            prefix: Prefix to complete
            limit: Maximum suggestions

        Returns:
            List of suggested symbol names
        """
        return self.symbol_index.autocomplete(prefix, limit)

    # ========== Statistics ==========

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics from all layers."""
        stats = {
            'symbol_index': self.symbol_index.get_statistics(),
        }

        if self.knowledge_graph:
            stats['knowledge_graph'] = self.knowledge_graph.get_statistics()

        if self.vector_store:
            try:
                collection = self.vector_store._collection
                if collection:
                    stats['vector_store'] = {
                        'total_chunks': collection.count()
                    }
            except:
                pass

        return stats
