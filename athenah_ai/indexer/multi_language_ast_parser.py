"""
Multi-Language AST Parser using tree-sitter.

Supports: C++, Python, TypeScript, JavaScript
Extracts symbols, relationships, and structural information from source code.
"""

import os
from typing import Dict, List, Optional, Tuple, Set, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger("app")

# Type hints for tree-sitter (only used for type checking)
if TYPE_CHECKING:
    from tree_sitter import Node, Language, Parser, Tree

# Try importing all tree-sitter languages
AVAILABLE_LANGUAGES = {}
Node = Any  # Fallback when tree-sitter not available
Language = Any
Parser = Any

try:
    import tree_sitter_cpp as tscpp
    from tree_sitter import Language, Parser, Node, Tree
    AVAILABLE_LANGUAGES['cpp'] = Language(tscpp.language())
    AVAILABLE_LANGUAGES['c'] = Language(tscpp.language())  # Use C++ parser for C too
except ImportError:
    logger.warning("tree-sitter-cpp not available")

try:
    import tree_sitter_python as tspython
    from tree_sitter import Language, Parser, Node, Tree
    AVAILABLE_LANGUAGES['python'] = Language(tspython.language())
except ImportError:
    logger.warning("tree-sitter-python not available")

try:
    import tree_sitter_typescript as tstyped
    from tree_sitter import Language, Parser, Node, Tree
    # TypeScript has two languages: typescript and tsx
    AVAILABLE_LANGUAGES['typescript'] = Language(tstyped.language_typescript())
    AVAILABLE_LANGUAGES['tsx'] = Language(tstyped.language_tsx())
except ImportError:
    logger.warning("tree-sitter-typescript not available")
except AttributeError:
    logger.warning("tree-sitter-typescript API mismatch")

try:
    import tree_sitter_javascript as tsjs
    from tree_sitter import Language, Parser, Node, Tree
    AVAILABLE_LANGUAGES['javascript'] = Language(tsjs.language())
except ImportError:
    logger.warning("tree-sitter-javascript not available")


@dataclass
class Symbol:
    """Represents a code symbol (function, class, variable)."""
    name: str
    kind: str  # function, class, struct, enum, variable, macro, method
    file_path: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    parent: Optional[str] = None  # For nested symbols (methods in classes)
    namespace: Optional[str] = None
    language: str = "unknown"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_qualified_name(self) -> str:
        """Get fully qualified name (namespace::class::function)."""
        parts = []
        if self.namespace:
            parts.append(self.namespace)
        if self.parent:
            parts.append(self.parent)
        parts.append(self.name)
        return "::".join(parts) if self.language in ['cpp', 'c'] else ".".join(parts)


@dataclass
class Relationship:
    """Represents a relationship between symbols."""
    source: str  # Symbol name (qualified)
    target: str  # Symbol name (qualified)
    kind: str  # calls, inherits, uses, defines, imports
    file_path: str
    line_number: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiLanguageASTParser:
    """Parse code in multiple languages and extract symbols and relationships."""

    # Map file extensions to language identifiers
    EXTENSION_TO_LANG = {
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'cpp',  # Headers could be C or C++, assume C++
        '.hpp': 'cpp',
        '.py': 'python',
        '.ts': 'typescript',
        '.tsx': 'tsx',  # TSX uses separate parser
        '.js': 'javascript',
        '.jsx': 'javascript',
    }

    def __init__(self):
        if not AVAILABLE_LANGUAGES:
            raise RuntimeError("No tree-sitter languages available")

        self.parsers = {}
        for lang_name, language in AVAILABLE_LANGUAGES.items():
            parser = Parser(language)
            self.parsers[lang_name] = parser

        logger.info(f"Multi-language AST parser initialized with: {list(AVAILABLE_LANGUAGES.keys())}")

    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect language from file extension."""
        ext = os.path.splitext(file_path)[1].lower()
        return self.EXTENSION_TO_LANG.get(ext)

    def parse_file(self, file_path: str) -> Tuple[List[Symbol], List[Relationship]]:
        """
        Parse a source file and extract symbols and relationships.

        Args:
            file_path: Path to source file

        Returns:
            Tuple of (symbols, relationships)
        """
        language = self.detect_language(file_path)
        if not language or language not in self.parsers:
            logger.debug(f"Unsupported language for {file_path}")
            return [], []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            parser = self.parsers[language]
            tree = parser.parse(bytes(source_code, 'utf-8'))

            # Use language-specific extraction
            if language in ['cpp', 'c']:
                symbols = self._extract_cpp_symbols(tree.root_node, file_path, source_code, language)
                relationships = self._extract_cpp_relationships(tree.root_node, file_path, source_code)
            elif language == 'python':
                symbols = self._extract_python_symbols(tree.root_node, file_path, source_code)
                relationships = self._extract_python_relationships(tree.root_node, file_path, source_code)
            elif language in ['typescript', 'tsx', 'javascript']:
                symbols = self._extract_ts_js_symbols(tree.root_node, file_path, source_code, language)
                relationships = self._extract_ts_js_relationships(tree.root_node, file_path, source_code)
            else:
                return [], []

            logger.debug(f"Parsed {file_path} ({language}): {len(symbols)} symbols, {len(relationships)} relationships")
            return symbols, relationships

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}", exc_info=True)
            return [], []

    # ========== C/C++ Extraction ==========

    def _extract_cpp_symbols(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str] = None, namespace: Optional[str] = None) -> List[Symbol]:
        """Extract symbols from C/C++ AST."""
        symbols = []

        if node.type == 'function_definition':
            symbol = self._extract_cpp_function(node, file_path, source_code, language, parent, namespace)
            if symbol:
                symbols.append(symbol)

        elif node.type in ['class_specifier', 'struct_specifier']:
            symbol = self._extract_cpp_class(node, file_path, source_code, language, parent, namespace)
            if symbol:
                symbols.append(symbol)
                # Parse class members
                body_node = self._find_child(node, 'field_declaration_list')
                if body_node:
                    symbols.extend(self._extract_cpp_symbols(body_node, file_path, source_code, language, symbol.name, namespace))

        elif node.type == 'enum_specifier':
            symbol = self._extract_cpp_enum(node, file_path, source_code, language, parent, namespace)
            if symbol:
                symbols.append(symbol)

        elif node.type == 'namespace_definition':
            ns_name = self._get_cpp_namespace_name(node, source_code)
            full_ns = f"{namespace}::{ns_name}" if namespace else ns_name
            body_node = self._find_child(node, 'declaration_list')
            if body_node:
                symbols.extend(self._extract_cpp_symbols(body_node, file_path, source_code, language, parent, full_ns))

        # Recurse
        for child in node.children:
            symbols.extend(self._extract_cpp_symbols(child, file_path, source_code, language, parent, namespace))

        return symbols

    def _extract_cpp_function(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str], namespace: Optional[str]) -> Optional[Symbol]:
        """Extract C++ function."""
        try:
            declarator = self._find_child(node, 'function_declarator')
            if not declarator:
                return None

            name_node = self._find_child(declarator, 'identifier') or self._find_child(declarator, 'field_identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)
            signature = self._get_node_text(declarator, source_code)

            return Symbol(
                name=name,
                kind='method' if parent else 'function',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                signature=signature,
                parent=parent,
                namespace=namespace,
                language=language
            )
        except:
            return None

    def _extract_cpp_class(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str], namespace: Optional[str]) -> Optional[Symbol]:
        """Extract C++ class/struct."""
        try:
            name_node = self._find_child(node, 'type_identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)
            kind = 'class' if node.type == 'class_specifier' else 'struct'

            base_classes = []
            base_clause = self._find_child(node, 'base_class_clause')
            if base_clause:
                for child in base_clause.children:
                    if child.type in ['type_identifier', 'template_type']:
                        base_classes.append(self._get_node_text(child, source_code))

            return Symbol(
                name=name,
                kind=kind,
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                parent=parent,
                namespace=namespace,
                language=language,
                metadata={'base_classes': base_classes}
            )
        except:
            return None

    def _extract_cpp_enum(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str], namespace: Optional[str]) -> Optional[Symbol]:
        """Extract C++ enum."""
        try:
            name_node = self._find_child(node, 'type_identifier')
            if not name_node:
                return None

            return Symbol(
                name=self._get_node_text(name_node, source_code),
                kind='enum',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                parent=parent,
                namespace=namespace,
                language=language
            )
        except:
            return None

    def _get_cpp_namespace_name(self, node: Node, source_code: str) -> str:
        """Get C++ namespace name."""
        name_node = self._find_child(node, 'identifier')
        return self._get_node_text(name_node, source_code) if name_node else "anonymous"

    def _extract_cpp_relationships(self, node: Node, file_path: str, source_code: str) -> List[Relationship]:
        """Extract C++ relationships."""
        relationships = []

        if node.type == 'call_expression':
            func_node = self._find_child(node, 'identifier') or self._find_child(node, 'field_identifier')
            if func_node:
                target = self._get_node_text(func_node, source_code)
                relationships.append(Relationship(
                    source='<unresolved>',
                    target=target,
                    kind='calls',
                    file_path=file_path,
                    line_number=node.start_point[0] + 1
                ))

        elif node.type == 'class_specifier':
            name_node = self._find_child(node, 'type_identifier')
            if name_node:
                class_name = self._get_node_text(name_node, source_code)
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

        for child in node.children:
            relationships.extend(self._extract_cpp_relationships(child, file_path, source_code))

        return relationships

    # ========== Python Extraction ==========

    def _extract_python_symbols(self, node: Node, file_path: str, source_code: str, parent: Optional[str] = None) -> List[Symbol]:
        """Extract symbols from Python AST."""
        symbols = []

        if node.type == 'function_definition':
            symbol = self._extract_python_function(node, file_path, source_code, parent)
            if symbol:
                symbols.append(symbol)

        elif node.type == 'class_definition':
            symbol = self._extract_python_class(node, file_path, source_code, parent)
            if symbol:
                symbols.append(symbol)
                # Parse class body for methods
                body_node = self._find_child(node, 'block')
                if body_node:
                    symbols.extend(self._extract_python_symbols(body_node, file_path, source_code, symbol.name))

        for child in node.children:
            symbols.extend(self._extract_python_symbols(child, file_path, source_code, parent))

        return symbols

    def _extract_python_function(self, node: Node, file_path: str, source_code: str, parent: Optional[str]) -> Optional[Symbol]:
        """Extract Python function/method."""
        try:
            name_node = self._find_child(node, 'identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)
            params_node = self._find_child(node, 'parameters')
            signature = self._get_node_text(params_node, source_code) if params_node else "()"

            return Symbol(
                name=name,
                kind='method' if parent else 'function',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                signature=f"{name}{signature}",
                parent=parent,
                language='python'
            )
        except:
            return None

    def _extract_python_class(self, node: Node, file_path: str, source_code: str, parent: Optional[str]) -> Optional[Symbol]:
        """Extract Python class."""
        try:
            name_node = self._find_child(node, 'identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)

            # Get base classes
            base_classes = []
            arg_list = self._find_child(node, 'argument_list')
            if arg_list:
                for child in arg_list.children:
                    if child.type == 'identifier':
                        base_classes.append(self._get_node_text(child, source_code))

            return Symbol(
                name=name,
                kind='class',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                parent=parent,
                language='python',
                metadata={'base_classes': base_classes}
            )
        except:
            return None

    def _extract_python_relationships(self, node: Node, file_path: str, source_code: str) -> List[Relationship]:
        """Extract Python relationships."""
        relationships = []

        if node.type == 'call':
            func_node = self._find_child(node, 'identifier') or self._find_child(node, 'attribute')
            if func_node:
                target = self._get_node_text(func_node, source_code)
                relationships.append(Relationship(
                    source='<unresolved>',
                    target=target,
                    kind='calls',
                    file_path=file_path,
                    line_number=node.start_point[0] + 1
                ))

        elif node.type == 'import_statement' or node.type == 'import_from_statement':
            # Extract import relationships
            for child in node.children:
                if child.type == 'dotted_name':
                    module = self._get_node_text(child, source_code)
                    relationships.append(Relationship(
                        source='<current_module>',
                        target=module,
                        kind='imports',
                        file_path=file_path,
                        line_number=node.start_point[0] + 1
                    ))

        for child in node.children:
            relationships.extend(self._extract_python_relationships(child, file_path, source_code))

        return relationships

    # ========== TypeScript/JavaScript Extraction ==========

    def _extract_ts_js_symbols(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str] = None) -> List[Symbol]:
        """Extract symbols from TypeScript/JavaScript AST."""
        symbols = []

        if node.type in ['function_declaration', 'function', 'method_definition', 'arrow_function']:
            symbol = self._extract_ts_js_function(node, file_path, source_code, language, parent)
            if symbol:
                symbols.append(symbol)

        elif node.type in ['class_declaration', 'class']:
            symbol = self._extract_ts_js_class(node, file_path, source_code, language, parent)
            if symbol:
                symbols.append(symbol)
                # Parse class body
                body_node = self._find_child(node, 'class_body')
                if body_node:
                    symbols.extend(self._extract_ts_js_symbols(body_node, file_path, source_code, language, symbol.name))

        elif node.type in ['interface_declaration', 'type_alias_declaration']:
            symbol = self._extract_ts_interface(node, file_path, source_code, language, parent)
            if symbol:
                symbols.append(symbol)

        for child in node.children:
            symbols.extend(self._extract_ts_js_symbols(child, file_path, source_code, language, parent))

        return symbols

    def _extract_ts_js_function(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str]) -> Optional[Symbol]:
        """Extract TS/JS function."""
        try:
            name_node = self._find_child(node, 'identifier') or self._find_child(node, 'property_identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)
            params_node = self._find_child(node, 'formal_parameters')
            signature = self._get_node_text(params_node, source_code) if params_node else "()"

            return Symbol(
                name=name,
                kind='method' if parent else 'function',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                signature=f"{name}{signature}",
                parent=parent,
                language=language
            )
        except:
            return None

    def _extract_ts_js_class(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str]) -> Optional[Symbol]:
        """Extract TS/JS class."""
        try:
            name_node = self._find_child(node, 'type_identifier') or self._find_child(node, 'identifier')
            if not name_node:
                return None

            name = self._get_node_text(name_node, source_code)

            # Get extends clause
            base_classes = []
            extends_clause = self._find_child(node, 'class_heritage')
            if extends_clause:
                extends_node = self._find_child(extends_clause, 'extends_clause')
                if extends_node:
                    for child in extends_node.children:
                        if child.type in ['identifier', 'type_identifier']:
                            base_classes.append(self._get_node_text(child, source_code))

            return Symbol(
                name=name,
                kind='class',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                parent=parent,
                language=language,
                metadata={'base_classes': base_classes}
            )
        except:
            return None

    def _extract_ts_interface(self, node: Node, file_path: str, source_code: str, language: str, parent: Optional[str]) -> Optional[Symbol]:
        """Extract TypeScript interface."""
        try:
            name_node = self._find_child(node, 'type_identifier')
            if not name_node:
                return None

            return Symbol(
                name=self._get_node_text(name_node, source_code),
                kind='interface',
                file_path=file_path,
                line_start=node.start_point[0] + 1,
                line_end=node.end_point[0] + 1,
                parent=parent,
                language=language
            )
        except:
            return None

    def _extract_ts_js_relationships(self, node: Node, file_path: str, source_code: str) -> List[Relationship]:
        """Extract TS/JS relationships."""
        relationships = []

        if node.type == 'call_expression':
            func_node = self._find_child(node, 'identifier') or self._find_child(node, 'member_expression')
            if func_node:
                target = self._get_node_text(func_node, source_code)
                relationships.append(Relationship(
                    source='<unresolved>',
                    target=target,
                    kind='calls',
                    file_path=file_path,
                    line_number=node.start_point[0] + 1
                ))

        elif node.type in ['import_statement', 'import_clause']:
            # Extract imports
            string_node = self._find_child(node, 'string')
            if string_node:
                module = self._get_node_text(string_node, source_code).strip('"\'')
                relationships.append(Relationship(
                    source='<current_module>',
                    target=module,
                    kind='imports',
                    file_path=file_path,
                    line_number=node.start_point[0] + 1
                ))

        for child in node.children:
            relationships.extend(self._extract_ts_js_relationships(child, file_path, source_code))

        return relationships

    # ========== Utility Methods ==========

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
    """Check if AST parsing is available for any language."""
    return len(AVAILABLE_LANGUAGES) > 0


def get_available_languages() -> List[str]:
    """Get list of supported languages."""
    return list(AVAILABLE_LANGUAGES.keys())
