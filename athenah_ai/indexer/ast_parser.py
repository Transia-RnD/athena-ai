"""
AST Parser for C/C++ code using tree-sitter.

Extracts symbols, relationships, and structural information from source code.
"""

import os
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("app")

try:
    import tree_sitter_cpp as tscpp
    from tree_sitter import Language, Parser, Node, Tree
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    logger.warning("tree-sitter not available - AST parsing disabled")


@dataclass
class Symbol:
    """Represents a code symbol (function, class, variable)."""
    name: str
    kind: str  # function, class, struct, enum, variable, macro
    file_path: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    parent: Optional[str] = None  # For nested symbols
    namespace: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Relationship:
    """Represents a relationship between symbols."""
    source: str  # Symbol name
    target: str  # Symbol name
    kind: str  # calls, inherits, uses, defines, includes
    file_path: str
    line_number: int


class CppASTParser:
    """Parse C++ code and extract symbols and relationships."""

    def __init__(self):
        if not TREE_SITTER_AVAILABLE:
            raise RuntimeError("tree-sitter-cpp not installed")

        self.language = Language(tscpp.language())
        self.parser = Parser(self.language)
        logger.info("C++ AST parser initialized")

    def parse_file(self, file_path: str) -> Tuple[List[Symbol], List[Relationship]]:
        """
        Parse a C++ file and extract symbols and relationships.

        Args:
            file_path: Path to C++ source file

        Returns:
            Tuple of (symbols, relationships)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            tree = self.parser.parse(bytes(source_code, 'utf-8'))
            symbols = self._extract_symbols(tree.root_node, file_path, source_code)
            relationships = self._extract_relationships(tree.root_node, file_path, source_code)

            logger.debug(f"Parsed {file_path}: {len(symbols)} symbols, {len(relationships)} relationships")
            return symbols, relationships

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return [], []

    def _extract_symbols(self, node: Node, file_path: str, source_code: str, parent: Optional[str] = None, namespace: Optional[str] = None) -> List[Symbol]:
        """Extract all symbols from AST recursively."""
        symbols = []

        # Function definitions
        if node.type == 'function_definition':
            symbol = self._extract_function(node, file_path, source_code, parent, namespace)
            if symbol:
                symbols.append(symbol)
                # Parse function body for nested symbols
                body_node = self._find_child(node, 'compound_statement')
                if body_node:
                    symbols.extend(self._extract_symbols(body_node, file_path, source_code, symbol.name, namespace))

        # Class/struct definitions
        elif node.type in ['class_specifier', 'struct_specifier']:
            symbol = self._extract_class(node, file_path, source_code, parent, namespace)
            if symbol:
                symbols.append(symbol)
                # Parse class members with class as parent
                body_node = self._find_child(node, 'field_declaration_list')
                if body_node:
                    symbols.extend(self._extract_symbols(body_node, file_path, source_code, symbol.name, namespace))

        # Enum definitions
        elif node.type == 'enum_specifier':
            symbol = self._extract_enum(node, file_path, source_code, parent, namespace)
            if symbol:
                symbols.append(symbol)

        # Namespace declarations
        elif node.type == 'namespace_definition':
            ns_name = self._get_namespace_name(node, source_code)
            full_namespace = f"{namespace}::{ns_name}" if namespace else ns_name
            # Continue parsing within namespace
            body_node = self._find_child(node, 'declaration_list')
            if body_node:
                symbols.extend(self._extract_symbols(body_node, file_path, source_code, parent, full_namespace))

        # Variable declarations
        elif node.type == 'declaration':
            var_symbols = self._extract_variables(node, file_path, source_code, parent, namespace)
            symbols.extend(var_symbols)

        # Recursively process children
        for child in node.children:
            symbols.extend(self._extract_symbols(child, file_path, source_code, parent, namespace))

        return symbols

    def _extract_function(self, node: Node, file_path: str, source_code: str, parent: Optional[str], namespace: Optional[str]) -> Optional[Symbol]:
        """Extract function symbol."""
        try:
            declarator = self._find_child(node, 'function_declarator')
            if not declarator:
                return None

            # Get function name
            name_node = self._find_child(declarator, 'identifier')
            if not name_node:
                name_node = self._find_child(declarator, 'field_identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)

            # Get full signature
            signature = self._get_node_text(declarator, source_code)

            return Symbol(
                name=name,
                kind='function',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                signature=signature,
                parent=parent,
                namespace=namespace
            )
        except Exception as e:
            logger.debug(f"Failed to extract function: {e}")
            return None

    def _extract_class(self, node: Node, file_path: str, source_code: str, parent: Optional[str], namespace: Optional[str]) -> Optional[Symbol]:
        """Extract class/struct symbol."""
        try:
            # Get class name
            name_node = self._find_child(node, 'type_identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)
            kind = 'class' if node.type == 'class_specifier' else 'struct'

            # Check for inheritance
            base_classes = []
            base_clause = self._find_child(node, 'base_class_clause')
            if base_clause:
                for child in base_clause.children:
                    if child.type in ['type_identifier', 'template_type']:
                        base_name = self._get_node_text(child, source_code)
                        base_classes.append(base_name)

            return Symbol(
                name=name,
                kind=kind,
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                parent=parent,
                namespace=namespace,
                metadata={'base_classes': base_classes}
            )
        except Exception as e:
            logger.debug(f"Failed to extract class: {e}")
            return None

    def _extract_enum(self, node: Node, file_path: str, source_code: str, parent: Optional[str], namespace: Optional[str]) -> Optional[Symbol]:
        """Extract enum symbol."""
        try:
            name_node = self._find_child(node, 'type_identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)

            return Symbol(
                name=name,
                kind='enum',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                parent=parent,
                namespace=namespace
            )
        except Exception as e:
            logger.debug(f"Failed to extract enum: {e}")
            return None

    def _extract_variables(self, node: Node, file_path: str, source_code: str, parent: Optional[str], namespace: Optional[str]) -> List[Symbol]:
        """Extract variable declarations."""
        variables = []
        try:
            for child in node.children:
                if child.type in ['init_declarator', 'identifier']:
                    name_node = child if child.type == 'identifier' else self._find_child(child, 'identifier')
                    if name_node:
                        name = self._get_node_text(name_node, source_code)
                        variables.append(Symbol(
                            name=name,
                            kind='variable',
                            file_path=file_path,
                            line_start=node.start_point[0] + 1,
                            line_end=node.end_point[0] + 1,
                            parent=parent,
                            namespace=namespace
                        ))
        except Exception as e:
            logger.debug(f"Failed to extract variables: {e}")

        return variables

    def _extract_relationships(self, node: Node, file_path: str, source_code: str) -> List[Relationship]:
        """Extract relationships (calls, inherits, uses)."""
        relationships = []

        # Function calls
        if node.type == 'call_expression':
            rel = self._extract_call_relationship(node, file_path, source_code)
            if rel:
                relationships.append(rel)

        # Inheritance (handled in _extract_class, but we can add edges here)
        elif node.type == 'class_specifier':
            rels = self._extract_inheritance_relationships(node, file_path, source_code)
            relationships.extend(rels)

        # Recursively process children
        for child in node.children:
            relationships.extend(self._extract_relationships(child, file_path, source_code))

        return relationships

    def _extract_call_relationship(self, node: Node, file_path: str, source_code: str) -> Optional[Relationship]:
        """Extract function call relationship."""
        try:
            # Get function being called
            func_node = self._find_child(node, 'identifier')
            if not func_node:
                func_node = self._find_child(node, 'field_identifier')
            if not func_node:
                return None

            target = self._get_node_text(func_node, source_code)

            # We don't know the source yet - will be resolved later in context
            return Relationship(
                source='<unresolved>',  # Will be filled by context
                target=target,
                kind='calls',
                file_path=file_path,
                line_number=node.start_point[0] + 1
            )
        except Exception as e:
            logger.debug(f"Failed to extract call relationship: {e}")
            return None

    def _extract_inheritance_relationships(self, node: Node, file_path: str, source_code: str) -> List[Relationship]:
        """Extract inheritance relationships."""
        relationships = []
        try:
            # Get class name
            name_node = self._find_child(node, 'type_identifier')
            if not name_node:
                return []

            class_name = self._get_node_text(name_node, source_code)

            # Get base classes
            base_clause = self._find_child(node, 'base_class_clause')
            if base_clause:
                for child in base_clause.children:
                    if child.type in ['type_identifier', 'template_type']:
                        base_name = self._get_node_text(child, source_code)
                        relationships.append(Relationship(
                            source=class_name,
                            target=base_name,
                            kind='inherits',
                            file_path=file_path,
                            line_number=node.start_point[0] + 1
                        ))
        except Exception as e:
            logger.debug(f"Failed to extract inheritance: {e}")

        return relationships

    def _get_namespace_name(self, node: Node, source_code: str) -> str:
        """Get namespace name from namespace_definition node."""
        name_node = self._find_child(node, 'identifier')
        if name_node:
            return self._get_node_text(name_node, source_code)
        return "anonymous"

    def _find_child(self, node: Node, child_type: str) -> Optional[Node]:
        """Find first child of specific type."""
        for child in node.children:
            if child.type == child_type:
                return child
        return None

    def _get_node_text(self, node: Node, source_code: str) -> str:
        """Get text content of a node."""
        return source_code[node.start_byte:node.end_byte]


def is_ast_parsing_available() -> bool:
    """Check if AST parsing is available."""
    return TREE_SITTER_AVAILABLE
