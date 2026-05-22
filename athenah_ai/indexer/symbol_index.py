"""
Fast symbol index for O(1) exact-match lookups.

Provides instant autocomplete, "go to definition" functionality.
"""

import os
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict
import logging
import json
import pickle

from athenah_ai.indexer.multi_language_ast_parser import Symbol

logger = logging.getLogger("app")


class SymbolIndex:
    """
    Fast hash-based symbol index.

    Provides O(1) lookups for exact symbol name matches.
    Useful for autocomplete, "go to definition", quick navigation.
    """

    def __init__(self, name: str, storage_path: Optional[str] = None):
        """
        Initialize symbol index.

        Args:
            name: Index identifier
            storage_path: Path to store/load index
        """
        self.name = name
        self.storage_path = storage_path

        # Primary indexes: name -> [symbols]
        self.by_name: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.by_qualified_name: Dict[str, Dict[str, Any]] = {}  # Unique

        # Secondary indexes for filtering
        self.by_kind: Dict[str, Set[str]] = defaultdict(set)  # kind -> {names}
        self.by_file: Dict[str, Set[str]] = defaultdict(set)  # file -> {names}
        self.by_namespace: Dict[str, Set[str]] = defaultdict(set)  # namespace -> {names}
        self.by_parent: Dict[str, Set[str]] = defaultdict(set)  # parent -> {names}

        # Prefix tree for autocomplete
        self.prefix_tree: Dict[str, Set[str]] = defaultdict(set)

        logger.info(f"Symbol index '{name}' initialized")

    def add_symbol(self, symbol: Symbol) -> None:
        """
        Add a symbol to the index.

        Args:
            symbol: Symbol to add
        """
        # Convert to dict for storage
        symbol_dict = {
            'name': symbol.name,
            'qualified_name': symbol.get_qualified_name(),
            'kind': symbol.kind,
            'file_path': symbol.file_path,
            'line_start': symbol.line_start,
            'line_end': symbol.line_end,
            'line_number': symbol.line_start,  # Alias for backward compatibility
            'signature': symbol.signature,
            'parent': symbol.parent,
            'namespace': symbol.namespace,
            'language': symbol.language,
            'metadata': symbol.metadata
        }

        # Add to primary indexes
        self.by_name[symbol.name].append(symbol_dict)
        self.by_qualified_name[symbol.get_qualified_name()] = symbol_dict

        # Add to secondary indexes
        self.by_kind[symbol.kind].add(symbol.name)
        self.by_file[symbol.file_path].add(symbol.name)

        if symbol.namespace:
            self.by_namespace[symbol.namespace].add(symbol.name)

        if symbol.parent:
            self.by_parent[symbol.parent].add(symbol.name)

        # Add to prefix tree (for autocomplete)
        self._add_to_prefix_tree(symbol.name)

    def _add_to_prefix_tree(self, name: str) -> None:
        """Add name to prefix tree for autocomplete."""
        for i in range(1, len(name) + 1):
            prefix = name[:i].lower()
            self.prefix_tree[prefix].add(name)

    # ========== Lookup Methods ==========

    def find_exact(self, name: str) -> List[Dict[str, Any]]:
        """
        Find symbols with exact name match.

        Args:
            name: Symbol name

        Returns:
            List of matching symbols
        """
        return self.by_name.get(name, [])

    def find_qualified(self, qualified_name: str) -> Optional[Dict[str, Any]]:
        """
        Find symbol by qualified name (e.g., "namespace::class::method").

        Args:
            qualified_name: Fully qualified symbol name

        Returns:
            Symbol or None
        """
        return self.by_qualified_name.get(qualified_name)

    def find_by_kind(self, kind: str) -> List[Dict[str, Any]]:
        """
        Find all symbols of a specific kind.

        Args:
            kind: Symbol kind (function, class, method, etc.)

        Returns:
            List of matching symbols
        """
        names = self.by_kind.get(kind, set())
        symbols = []
        for name in names:
            symbols.extend(self.by_name[name])
        return symbols

    def find_in_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Find all symbols in a specific file.

        Args:
            file_path: File path

        Returns:
            List of symbols in file
        """
        names = self.by_file.get(file_path, set())
        symbols = []
        for name in names:
            symbols.extend(self.by_name[name])
        return symbols

    def find_in_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        """
        Find all symbols in a namespace.

        Args:
            namespace: Namespace name

        Returns:
            List of symbols in namespace
        """
        names = self.by_namespace.get(namespace, set())
        symbols = []
        for name in names:
            symbols.extend(self.by_name[name])
        return symbols

    def find_children(self, parent_name: str) -> List[Dict[str, Any]]:
        """
        Find all symbols that are children of a parent (methods in a class).

        Args:
            parent_name: Parent symbol name (usually a class)

        Returns:
            List of child symbols
        """
        names = self.by_parent.get(parent_name, set())
        symbols = []
        for name in names:
            symbols.extend(self.by_name[name])
        return symbols

    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions for a prefix.

        Args:
            prefix: Prefix to match
            limit: Maximum number of suggestions

        Returns:
            List of suggested symbol names
        """
        matches = self.prefix_tree.get(prefix.lower(), set())
        return sorted(list(matches))[:limit]

    def fuzzy_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fuzzy search for symbols (case-insensitive substring match).

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching symbols
        """
        query_lower = query.lower()
        matches = []

        for name, symbols in self.by_name.items():
            if query_lower in name.lower():
                matches.extend(symbols)

        # Sort by name length (shorter = better match)
        matches.sort(key=lambda s: len(s['name']))

        return matches[:limit]

    # ========== Filtering ==========

    def filter(
        self,
        name: Optional[str] = None,
        kind: Optional[str] = None,
        file_path: Optional[str] = None,
        namespace: Optional[str] = None,
        parent: Optional[str] = None,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter symbols by multiple criteria.

        Args:
            name: Optional name filter
            kind: Optional kind filter
            file_path: Optional file filter
            namespace: Optional namespace filter
            parent: Optional parent filter
            language: Optional language filter

        Returns:
            List of matching symbols
        """
        # Start with all symbols or filtered set
        if name:
            candidates = self.by_name.get(name, [])
        elif kind:
            candidates = self.find_by_kind(kind)
        elif file_path:
            candidates = self.find_in_file(file_path)
        elif namespace:
            candidates = self.find_in_namespace(namespace)
        elif parent:
            candidates = self.find_children(parent)
        else:
            # All symbols
            candidates = []
            for symbols_list in self.by_name.values():
                candidates.extend(symbols_list)

        # Apply remaining filters
        results = []
        for symbol in candidates:
            if kind and symbol['kind'] != kind:
                continue
            if file_path and symbol['file_path'] != file_path:
                continue
            if namespace and symbol['namespace'] != namespace:
                continue
            if parent and symbol['parent'] != parent:
                continue
            if language and symbol['language'] != language:
                continue

            results.append(symbol)

        return results

    # ========== Statistics ==========

    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        total_symbols = sum(len(symbols) for symbols in self.by_name.values())
        unique_names = len(self.by_name)

        return {
            'total_symbols': total_symbols,
            'unique_names': unique_names,
            'qualified_names': len(self.by_qualified_name),
            'kinds': {kind: len(names) for kind, names in self.by_kind.items()},
            'files_indexed': len(self.by_file),
            'namespaces': len(self.by_namespace)
        }

    # ========== Persistence ==========

    def save(self, path: Optional[str] = None) -> bool:
        """
        Save index to disk.

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

            # Convert sets to lists for JSON serialization
            data = {
                'by_name': dict(self.by_name),
                'by_qualified_name': self.by_qualified_name,
                'by_kind': {k: list(v) for k, v in self.by_kind.items()},
                'by_file': {k: list(v) for k, v in self.by_file.items()},
                'by_namespace': {k: list(v) for k, v in self.by_namespace.items()},
                'by_parent': {k: list(v) for k, v in self.by_parent.items()},
                'prefix_tree': {k: list(v) for k, v in self.prefix_tree.items()}
            }

            with open(save_path, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved symbol index to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save symbol index: {e}")
            return False

    def load(self, path: Optional[str] = None) -> bool:
        """
        Load index from disk.

        Args:
            path: Optional path override

        Returns:
            True if successful
        """
        load_path = path or self.storage_path
        if not load_path or not os.path.exists(load_path):
            logger.info("No existing symbol index found")
            return False

        try:
            with open(load_path, 'r') as f:
                data = json.load(f)

            self.by_name = defaultdict(list, data['by_name'])
            self.by_qualified_name = data['by_qualified_name']
            self.by_kind = defaultdict(set, {k: set(v) for k, v in data['by_kind'].items()})
            self.by_file = defaultdict(set, {k: set(v) for k, v in data['by_file'].items()})
            self.by_namespace = defaultdict(set, {k: set(v) for k, v in data['by_namespace'].items()})
            self.by_parent = defaultdict(set, {k: set(v) for k, v in data['by_parent'].items()})
            self.prefix_tree = defaultdict(set, {k: set(v) for k, v in data['prefix_tree'].items()})

            stats = self.get_statistics()
            logger.info(f"Loaded symbol index from {load_path}: {stats['total_symbols']} symbols")
            return True

        except Exception as e:
            logger.error(f"Failed to load symbol index: {e}")
            return False
