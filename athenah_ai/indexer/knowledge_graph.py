"""
Knowledge Graph for code structure using NetworkX.

Stores symbols as nodes and relationships (calls, inherits, imports) as edges.
Enables structural queries like "what calls this?", "show inheritance tree", etc.
"""

import os
from typing import Dict, List, Optional, Tuple, Set, Any
import logging
import json
import pickle

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

from athenah_ai.indexer.multi_language_ast_parser import Symbol, Relationship

logger = logging.getLogger("app")


class CodeKnowledgeGraph:
    """
    Knowledge graph representing code structure and relationships.

    Nodes: Symbols (functions, classes, variables)
    Edges: Relationships (calls, inherits, imports, uses)
    """

    def __init__(self, name: str, storage_path: Optional[str] = None):
        """
        Initialize knowledge graph.

        Args:
            name: Graph identifier
            storage_path: Path to store/load graph
        """
        if not NETWORKX_AVAILABLE:
            raise RuntimeError("NetworkX not installed - knowledge graph unavailable")

        self.name = name
        self.storage_path = storage_path

        # Create directed multigraph (allows multiple edges between same nodes)
        self.graph = nx.MultiDiGraph()

        # Index for fast lookups
        self.symbol_by_name: Dict[str, List[str]] = {}  # name -> [node_ids]
        self.symbol_by_file: Dict[str, List[str]] = {}  # file -> [node_ids]
        self.symbol_by_kind: Dict[str, List[str]] = {}  # kind -> [node_ids]

        logger.info(f"Knowledge graph '{name}' initialized")

    def add_symbol(self, symbol: Symbol) -> str:
        """
        Add a symbol to the graph.

        Args:
            symbol: Symbol to add

        Returns:
            Node ID (qualified name)
        """
        node_id = symbol.get_qualified_name()

        # Add node with attributes
        self.graph.add_node(
            node_id,
            name=symbol.name,
            kind=symbol.kind,
            file_path=symbol.file_path,
            line_start=symbol.line_start,
            line_end=symbol.line_end,
            signature=symbol.signature,
            parent=symbol.parent,
            namespace=symbol.namespace,
            language=symbol.language,
            metadata=symbol.metadata
        )

        # Update indexes
        if symbol.name not in self.symbol_by_name:
            self.symbol_by_name[symbol.name] = []
        self.symbol_by_name[symbol.name].append(node_id)

        if symbol.file_path not in self.symbol_by_file:
            self.symbol_by_file[symbol.file_path] = []
        self.symbol_by_file[symbol.file_path].append(node_id)

        if symbol.kind not in self.symbol_by_kind:
            self.symbol_by_kind[symbol.kind] = []
        self.symbol_by_kind[symbol.kind].append(node_id)

        return node_id

    def add_relationship(self, relationship: Relationship) -> bool:
        """
        Add a relationship (edge) between symbols.

        Args:
            relationship: Relationship to add

        Returns:
            True if added successfully
        """
        # Resolve source/target to node IDs
        source_node = self._resolve_symbol(relationship.source, relationship.file_path)
        target_node = self._resolve_symbol(relationship.target, relationship.file_path)

        if not source_node or not target_node:
            logger.debug(f"Could not resolve relationship: {relationship.source} -> {relationship.target}")
            return False

        # Add edge
        self.graph.add_edge(
            source_node,
            target_node,
            kind=relationship.kind,
            file_path=relationship.file_path,
            line_number=relationship.line_number,
            metadata=relationship.metadata
        )

        return True

    def _resolve_symbol(self, symbol_name: str, context_file: Optional[str] = None) -> Optional[str]:
        """
        Resolve a symbol name to a node ID.

        Tries:
        1. Exact match (qualified name)
        2. Match in same file (for local references)
        3. Match by name (first match)

        Args:
            symbol_name: Symbol to resolve
            context_file: File where symbol is referenced (for context)

        Returns:
            Node ID or None
        """
        # Special case: unresolved placeholders
        if symbol_name == '<unresolved>' or symbol_name == '<current_module>':
            return None

        # Try exact match (qualified name)
        if self.graph.has_node(symbol_name):
            return symbol_name

        # Try match in same file
        if context_file and context_file in self.symbol_by_file:
            candidates = self.symbol_by_file[context_file]
            for node_id in candidates:
                node_data = self.graph.nodes[node_id]
                if node_data['name'] == symbol_name:
                    return node_id

        # Try match by name (take first)
        if symbol_name in self.symbol_by_name:
            candidates = self.symbol_by_name[symbol_name]
            if candidates:
                return candidates[0]

        return None

    # ========== Query Methods ==========

    def find_symbol(self, name: str, kind: Optional[str] = None, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find symbols by name, optionally filtered by kind or file.

        Args:
            name: Symbol name to search
            kind: Optional symbol kind filter (function, class, etc.)
            file_path: Optional file path filter

        Returns:
            List of matching symbol data
        """
        results = []

        candidates = self.symbol_by_name.get(name, [])

        for node_id in candidates:
            node_data = self.graph.nodes[node_id]

            # Apply filters
            if kind and node_data['kind'] != kind:
                continue
            if file_path and node_data['file_path'] != file_path:
                continue

            results.append({
                'id': node_id,
                **node_data
            })

        return results

    def find_callers(self, symbol_name: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """
        Find all symbols that call the given symbol.

        Args:
            symbol_name: Symbol to find callers for
            max_depth: Maximum depth to search (1 = direct callers only,
                       >1 = include transitive callers up to max_depth)

        Returns:
            List of caller symbols with call information and depth
        """
        node_id = self._resolve_symbol(symbol_name)
        if not node_id:
            return []

        callers = []
        visited: set = set()
        frontier = [(node_id, 0)]

        while frontier:
            current_id, depth = frontier.pop(0)
            if depth >= max_depth:
                continue

            for caller_id in self.graph.predecessors(current_id):
                if caller_id in visited:
                    continue
                edges = self.graph.get_edge_data(caller_id, current_id)
                for edge_key, edge_data in edges.items():
                    if edge_data['kind'] == 'calls':
                        visited.add(caller_id)
                        caller_node = self.graph.nodes[caller_id]
                        callers.append({
                            'id': caller_id,
                            'name': caller_node['name'],
                            'kind': caller_node['kind'],
                            'file_path': caller_node['file_path'],
                            'line_number': edge_data['line_number'],
                            'depth': depth + 1,
                        })
                        frontier.append((caller_id, depth + 1))
                        break  # One edge per caller is enough

        return callers

    def find_callees(self, symbol_name: str, max_depth: int = 1) -> List[Dict[str, Any]]:
        """
        Find all symbols called by the given symbol.

        Args:
            symbol_name: Symbol to find callees for
            max_depth: Maximum depth to search (1 = direct calls only,
                       >1 = include transitive callees up to max_depth)

        Returns:
            List of called symbols with depth
        """
        node_id = self._resolve_symbol(symbol_name)
        if not node_id:
            return []

        callees = []
        visited: set = set()
        frontier = [(node_id, 0)]

        while frontier:
            current_id, depth = frontier.pop(0)
            if depth >= max_depth:
                continue

            for callee_id in self.graph.successors(current_id):
                if callee_id in visited:
                    continue
                edges = self.graph.get_edge_data(current_id, callee_id)
                for edge_key, edge_data in edges.items():
                    if edge_data['kind'] == 'calls':
                        visited.add(callee_id)
                        callee_node = self.graph.nodes[callee_id]
                        callees.append({
                            'id': callee_id,
                            'name': callee_node['name'],
                            'kind': callee_node['kind'],
                            'file_path': callee_node['file_path'],
                            'line_number': edge_data['line_number'],
                            'depth': depth + 1,
                        })
                        frontier.append((callee_id, depth + 1))
                        break  # One edge per callee is enough

        return callees

    def find_entrance(self, symbol_names: List[str], max_depth: int = 5) -> Optional[Dict[str, Any]]:
        """Find the root caller (entrance) for a set of symbols.

        Traces callers upward from each symbol until finding a function
        with no callers in the graph (the entry point).  If multiple
        roots exist, returns the one closest to the most changed symbols.

        Args:
            symbol_names: List of changed symbol names to trace from
            max_depth: Maximum depth to search upward

        Returns:
            The root symbol dict, or None if no symbols resolve
        """
        # Collect all roots reachable from any changed symbol
        root_counts: Dict[str, int] = {}
        root_data: Dict[str, Dict[str, Any]] = {}

        for sym in symbol_names:
            node_id = self._resolve_symbol(sym)
            if not node_id:
                continue

            # Walk up the caller chain
            current = node_id
            visited: set = set()
            depth = 0
            while depth < max_depth:
                visited.add(current)
                callers_of_current = [
                    cid for cid in self.graph.predecessors(current)
                    if cid not in visited
                    and any(
                        ed['kind'] == 'calls'
                        for _, ed in self.graph.get_edge_data(cid, current).items()
                    )
                ]
                if not callers_of_current:
                    # current is a root
                    node = self.graph.nodes[current]
                    root_counts[current] = root_counts.get(current, 0) + 1
                    root_data[current] = {
                        'id': current,
                        'name': node['name'],
                        'kind': node['kind'],
                        'file_path': node['file_path'],
                        'line_number': node.get('line_start', 0),
                    }
                    break
                current = callers_of_current[0]
                depth += 1

        if not root_data:
            return None

        # Return the root reachable from the most changed symbols
        best = max(root_counts, key=root_counts.get)
        return root_data[best]

    def get_inheritance_tree(self, class_name: str, direction: str = 'ancestors') -> Dict[str, Any]:
        """
        Get inheritance tree (ancestors or descendants) for a class.

        Args:
            class_name: Class to get tree for
            direction: 'ancestors' (parent classes) or 'descendants' (child classes)

        Returns:
            Tree structure as nested dict
        """
        node_id = self._resolve_symbol(class_name)
        if not node_id:
            return {}

        node_data = self.graph.nodes[node_id]
        tree = {
            'id': node_id,
            'name': node_data['name'],
            'kind': node_data['kind'],
            'file_path': node_data['file_path'],
            'children': []
        }

        if direction == 'ancestors':
            # Get parent classes (successors with 'inherits' edge)
            for parent_id in self.graph.successors(node_id):
                edges = self.graph.get_edge_data(node_id, parent_id)
                for edge_key, edge_data in edges.items():
                    if edge_data['kind'] == 'inherits':
                        parent_tree = self.get_inheritance_tree(parent_id, 'ancestors')
                        tree['children'].append(parent_tree)

        elif direction == 'descendants':
            # Get child classes (predecessors with 'inherits' edge)
            for child_id in self.graph.predecessors(node_id):
                edges = self.graph.get_edge_data(child_id, node_id)
                for edge_key, edge_data in edges.items():
                    if edge_data['kind'] == 'inherits':
                        child_tree = self.get_inheritance_tree(child_id, 'descendants')
                        tree['children'].append(child_tree)

        return tree

    def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """
        Get dependencies for a file (what it imports, what imports it).

        Args:
            file_path: File to get dependencies for

        Returns:
            Dict with 'imports' and 'imported_by' lists
        """
        imports = set()
        imported_by = set()

        # Get all symbols in this file
        if file_path not in self.symbol_by_file:
            return {'imports': [], 'imported_by': []}

        file_symbols = self.symbol_by_file[file_path]

        for symbol_id in file_symbols:
            # Check outgoing imports
            for target_id in self.graph.successors(symbol_id):
                edges = self.graph.get_edge_data(symbol_id, target_id)
                for edge_key, edge_data in edges.items():
                    if edge_data['kind'] == 'imports':
                        target_node = self.graph.nodes[target_id]
                        imports.add(target_node['file_path'])

            # Check incoming imports
            for source_id in self.graph.predecessors(symbol_id):
                edges = self.graph.get_edge_data(source_id, symbol_id)
                for edge_key, edge_data in edges.items():
                    if edge_data['kind'] == 'imports':
                        source_node = self.graph.nodes[source_id]
                        imported_by.add(source_node['file_path'])

        return {
            'imports': list(imports),
            'imported_by': list(imported_by)
        }

    def get_call_graph(self, symbol_name: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Get call graph centered on a symbol (who calls it, what it calls).

        Args:
            symbol_name: Symbol to center graph on
            max_depth: Maximum depth to traverse

        Returns:
            Call graph as nested dict
        """
        node_id = self._resolve_symbol(symbol_name)
        if not node_id:
            return {}

        node_data = self.graph.nodes[node_id]

        return {
            'id': node_id,
            'symbol': symbol_name,  # Alias for backward compatibility
            'name': node_data['name'],
            'kind': node_data['kind'],
            'file_path': node_data['file_path'],
            'calls': self.find_callees(node_id, max_depth),
            'called_by': self.find_callers(node_id, max_depth)
        }

    # ========== Statistics ==========

    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics."""
        return {
            'total_symbols': self.graph.number_of_nodes(),
            'total_relationships': self.graph.number_of_edges(),
            'symbols_by_kind': {
                kind: len(nodes) for kind, nodes in self.symbol_by_kind.items()
            },
            'files_indexed': len(self.symbol_by_file),
            'avg_degree': sum(dict(self.graph.degree()).values()) / max(1, self.graph.number_of_nodes())
        }

    # ========== Persistence ==========

    def save(self, path: Optional[str] = None) -> bool:
        """
        Save graph to disk.

        Args:
            path: Optional path override

        Returns:
            True if successful
        """
        save_path = path or self.storage_path
        if not save_path:
            logger.warning("No storage path specified")
            return False

        try:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save graph using pickle (preserves all metadata)
            with open(save_path, 'wb') as f:
                pickle.dump({
                    'graph': self.graph,
                    'symbol_by_name': self.symbol_by_name,
                    'symbol_by_file': self.symbol_by_file,
                    'symbol_by_kind': self.symbol_by_kind
                }, f)

            logger.info(f"Saved knowledge graph to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")
            return False

    def load(self, path: Optional[str] = None) -> bool:
        """
        Load graph from disk.

        Args:
            path: Optional path override

        Returns:
            True if successful
        """
        load_path = path or self.storage_path
        if not load_path or not os.path.exists(load_path):
            logger.info("No existing knowledge graph found")
            return False

        try:
            with open(load_path, 'rb') as f:
                data = pickle.load(f)

            self.graph = data['graph']
            self.symbol_by_name = data['symbol_by_name']
            self.symbol_by_file = data['symbol_by_file']
            self.symbol_by_kind = data['symbol_by_kind']

            stats = self.get_statistics()
            logger.info(f"Loaded knowledge graph from {load_path}: {stats['total_symbols']} symbols, {stats['total_relationships']} relationships")
            return True

        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {e}")
            return False


def is_knowledge_graph_available() -> bool:
    """Check if knowledge graph functionality is available."""
    return NETWORKX_AVAILABLE
