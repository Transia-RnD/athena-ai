"""
Index Client - The Ultimate RAG System for Code.

Extends BaseIndexClient with 3-layer hybrid search:
1. Symbol Index: O(1) exact matches
2. Knowledge Graph: Structural relationships (calls, inherits)
3. Vector Store: Semantic similarity (ChromaDB)

Plus intelligent query routing for optimal performance.
"""

import os
from typing import Dict, List, Optional, Tuple, Any
import logging

from athenah_ai.indexer.base_index_client import BaseIndexClient
from athenah_ai.indexer.multi_language_ast_parser import (
    MultiLanguageASTParser,
    is_ast_parsing_available,
    Symbol,
    Relationship,
)
from athenah_ai.indexer.symbol_index import SymbolIndex
from athenah_ai.indexer.knowledge_graph import (
    CodeKnowledgeGraph,
    is_knowledge_graph_available,
)
from athenah_ai.indexer.hybrid_query_engine import HybridQueryEngine, QueryResult
from athenah_ai.basedir import basedir

logger = logging.getLogger("app")


class IndexClient(BaseIndexClient):
    """
    Hybrid RAG index combining symbol index, knowledge graph, and vector store.

    Features:
    - AST parsing for C++, Python, TypeScript, JavaScript
    - Symbol index for instant lookups
    - Knowledge graph for structural queries (call graphs, inheritance)
    - Vector embeddings for semantic search
    - Intelligent query routing
    """

    def __init__(
        self,
        storage_type: str,
        id: str,
        dir: str,
        name: str,
        version: str = "v1",
        enable_ast: bool = True,
        enable_graph: bool = True,
    ):
        """
        Initialize hybrid index client.

        Args:
            storage_type: Storage backend (local or gcs)
            id: Unique identifier
            dir: Storage directory
            name: Index name
            version: Index version
            enable_ast: Enable AST parsing and symbol/graph layers
            enable_graph: Enable knowledge graph layer
        """
        # Initialize base vector store
        super().__init__(storage_type, id, dir, name, version)

        self.enable_ast = enable_ast and is_ast_parsing_available()
        self.enable_graph = enable_graph and is_knowledge_graph_available()

        # Initialize AST parser
        self.ast_parser: Optional[MultiLanguageASTParser] = None
        if self.enable_ast:
            try:
                self.ast_parser = MultiLanguageASTParser()
                logger.info("AST parser enabled")
            except Exception as e:
                logger.warning(f"AST parser initialization failed: {e}")
                self.enable_ast = False

        # Initialize symbol index
        self.symbol_index: Optional[SymbolIndex] = None
        if self.enable_ast:
            symbol_index_path = os.path.join(
                self.name_version_path, "symbol_index.json"
            )
            self.symbol_index = SymbolIndex(
                name=f"{name}_symbols", storage_path=symbol_index_path
            )
            self.symbol_index.load()

        # Initialize knowledge graph
        self.knowledge_graph: Optional[CodeKnowledgeGraph] = None
        if self.enable_ast and self.enable_graph:
            graph_path = os.path.join(self.name_version_path, "knowledge_graph.pkl")
            self.knowledge_graph = CodeKnowledgeGraph(
                name=f"{name}_graph", storage_path=graph_path
            )
            self.knowledge_graph.load()

        # Initialize hybrid query engine
        self.query_engine: Optional[HybridQueryEngine] = None
        if self.enable_ast:
            self.query_engine = HybridQueryEngine(
                symbol_index=self.symbol_index,
                knowledge_graph=self.knowledge_graph,
                vector_store=self,  # Pass self as vector store
            )

        # Load existing ChromaDB collection if it exists
        self.load()

        logger.info(
            f"Hybrid index client initialized: "
            f"AST={self.enable_ast}, Graph={self.enable_graph}"
        )

    # ========== Overridden Indexing Methods ==========

    def build_from_dir(
        self,
        source: str,
        clean_dir: bool = False,
        rebuild_index: bool = False,
    ) -> int:
        """Build index from a directory.

        Args:
            source: Source directory to index
            clean_dir: Whether to clean the source directory
            rebuild_index: Whether to completely rebuild the index (removes all previous index data)

        Returns:
            Number of documents indexed
        """
        from athenah_ai.indexer.cleaner import AthenahCleaner
        import shutil

        # Clean up entire index directory if rebuilding
        if rebuild_index and os.path.exists(self.name_version_path):
            logger.debug(f"Rebuilding index: removing {self.name_version_path}")
            shutil.rmtree(self.name_version_path, ignore_errors=True)
            os.makedirs(self.name_version_path, exist_ok=True)
            # Reinitialize ChromaDB client after cleanup
            if self.storage_type == "local":
                import chromadb
                from chromadb.config import Settings
                self._chroma_client = chromadb.PersistentClient(
                    path=self.name_version_path,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=False
                    )
                )

        source_name: str = f"{self.name}-source"
        build_paths: List[str] = [f"{self.name_path}/{source_name}"]

        if clean_dir:
            dest_filepath: str = os.path.join(self.name_path, source_name)
            shutil.rmtree(dest_filepath, ignore_errors=True)
            shutil.copytree(source, dest_filepath, dirs_exist_ok=True)
            _ = [AthenahCleaner().clean_dir(filepath, True) for filepath in build_paths]

        _docs, _metadata = self._build_from_dirs(source, build_paths, False)

        # AST parsing if enabled
        if self.enable_ast and self.ast_parser:
            logger.info(f"Parsing AST for directory")
            file_paths = []
            for doc, meta in zip(_docs, _metadata):
                if "source" in meta:
                    file_paths.append(meta["source"])
            self._parse_and_index_files(file_paths)

        success = self.store_from_docs(_docs, _metadata)
        if success:
            self._save_all_indexes()
            self.save()
        return len(_docs) if success else 0

    def build_from_dirs(
        self,
        source: str,
        folders: List[str] = None,
        include_root: bool = False,
        clean_dirs: bool = False,
        rebuild_index: bool = False,
    ) -> int:
        """Build index from multiple directories.

        Args:
            source: Source directory to index
            folders: List of subdirectories to include
            include_root: Whether to include root directory
            clean_dirs: Whether to clean source directories
            rebuild_index: Whether to completely rebuild the index (removes all previous index data)

        Returns:
            Number of documents indexed
        """
        from athenah_ai.indexer.cleaner import AthenahCleaner
        import shutil

        # Clean up entire index directory if rebuilding
        if rebuild_index and os.path.exists(self.name_version_path):
            logger.debug(f"Rebuilding index: removing {self.name_version_path}")
            shutil.rmtree(self.name_version_path, ignore_errors=True)
            os.makedirs(self.name_version_path, exist_ok=True)
            # Reinitialize ChromaDB client after cleanup
            if self.storage_type == "local":
                import chromadb
                from chromadb.config import Settings
                self._chroma_client = chromadb.PersistentClient(
                    path=self.name_version_path,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=False
                    )
                )

        source_name: str = f"{self.name}-source"
        build_paths: List[str] = [
            f"{self.name_path}/{source_name}/{f}" for f in folders
        ]

        if clean_dirs:
            dest_filepath: str = os.path.join(self.name_path, source_name)
            shutil.rmtree(dest_filepath, ignore_errors=True)
            shutil.copytree(source, dest_filepath, dirs_exist_ok=True)

            [AthenahCleaner().clean_dir(filepath, True) for filepath in build_paths]
            if include_root:
                AthenahCleaner().clean_dir(f"{self.name_path}/{source_name}", False)

        _docs, _metadata = self._build_from_dirs(source, build_paths, include_root)

        # AST parsing if enabled
        if self.enable_ast and self.ast_parser:
            logger.debug(f"Parsing AST for directories")
            file_paths = []
            for doc, meta in zip(_docs, _metadata):
                # Use file_path from metadata (set by prepare_dir)
                if "file_path" in meta:
                    file_paths.append(meta["file_path"])
                elif "source" in meta:
                    file_paths.append(meta["source"])
            logger.debug(f"AST parsing {len(set(file_paths))} unique files")
            self._parse_and_index_files(list(set(file_paths)))

        success = self.store_from_docs(_docs, _metadata)
        if success:
            self._save_all_indexes()
            self.save()
        return len(_docs) if success else 0

    def build_from_file(self, file_path: str, clean_file: bool = False) -> bool:
        """Build index from a single file.

        Args:
            file_path: Path to the file to index
            clean_file: Whether to clean the file before indexing

        Returns:
            True if successful
        """
        from athenah_ai.indexer.cleaner import AthenahCleaner
        import shutil

        source_name: str = f"{self.name}-source"
        dest_source: str = os.path.join(self.name_path, source_name)
        shutil.rmtree(dest_source, ignore_errors=True)
        os.makedirs(dest_source, exist_ok=True)

        # Copy file
        dest_file = os.path.join(dest_source, os.path.basename(file_path))
        shutil.copy2(file_path, dest_file)

        if clean_file:
            AthenahCleaner().clean_dir(dest_source, True)

        _docs, _metadata = self._build_from_dirs(dest_source, [dest_source], True)

        # AST parsing if enabled
        if self.enable_ast and self.ast_parser:
            logger.info(f"Parsing AST for file")
            self._parse_and_index_files([file_path])

        success = self.store_from_docs(_docs, _metadata)
        if success:
            self._save_all_indexes()
            self.save()
        return success

    def build_from_files(self, file_paths: List[str]) -> bool:
        """
        Build hybrid index from files (override).

        Processes files through:
        1. AST parsing (extract symbols and relationships)
        2. Symbol indexing
        3. Knowledge graph building
        4. Vector embedding (parent class method)

        Args:
            file_paths: List of source files to index

        Returns:
            True if successful
        """
        # Phase 1: AST parsing (if enabled)
        if self.enable_ast and self.ast_parser:
            logger.info(f"Phase 1/3: Parsing AST for {len(file_paths)} files")
            self._parse_and_index_files(file_paths)

        # Phase 2: Vector indexing (parent class method)
        logger.info(f"Phase 2/3: Building vector embeddings")
        success = super().build_from_files(file_paths)

        if not success:
            return False

        # Phase 3: Save all indexes
        logger.info(f"Phase 3/3: Saving indexes")
        self._save_all_indexes()

        logger.info("Hybrid index build complete")
        return True

    def _parse_and_index_files(self, file_paths: List[str]) -> None:
        """Parse files and build symbol index + knowledge graph."""
        logger.debug(f"Starting AST parsing for {len(file_paths)} files")
        for file_path in file_paths:
            try:
                logger.debug(f"Parsing file: {file_path}")
                # Parse file with AST
                symbols, relationships = self.ast_parser.parse_file(file_path)

                # Add symbols to index
                for symbol in symbols:
                    self.symbol_index.add_symbol(symbol)

                    # Add to knowledge graph if enabled
                    if self.knowledge_graph:
                        self.knowledge_graph.add_symbol(symbol)

                # Add relationships to knowledge graph
                if self.knowledge_graph:
                    for relationship in relationships:
                        self.knowledge_graph.add_relationship(relationship)

                logger.debug(
                    f"Indexed {file_path}: {len(symbols)} symbols, {len(relationships)} relationships"
                )

            except Exception as e:
                logger.error(f"Failed to parse {file_path}: {e}", exc_info=True)

    def _save_all_indexes(self) -> None:
        """Save all index layers."""
        if self.symbol_index:
            self.symbol_index.save()

        if self.knowledge_graph:
            self.knowledge_graph.save()

    # ========== Progressive Indexing (Single File) ==========

    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any],
        chunk_size: Optional[int] = None,
        chunk_overlap: int = None,
        model: str = None,
        max_tokens: int = 2048,
    ) -> bool:
        """
        Add single document with hybrid indexing (override).

        Args:
            content: Document content
            metadata: Document metadata (must include 'source' file path)
            chunk_size: Optional chunk size
            chunk_overlap: Overlap between chunks
            model: Embedding model
            max_tokens: Max tokens per chunk

        Returns:
            True if successful
        """
        # Get file path from metadata
        file_path = metadata.get("source")

        # Phase 1: AST parsing (if file is supported)
        if self.enable_ast and self.ast_parser and file_path:
            if os.path.exists(file_path):
                try:
                    logger.debug(f"Parsing AST for {file_path}")
                    symbols, relationships = self.ast_parser.parse_file(file_path)

                    # Add to symbol index
                    for symbol in symbols:
                        self.symbol_index.add_symbol(symbol)

                        if self.knowledge_graph:
                            self.knowledge_graph.add_symbol(symbol)

                    # Add to knowledge graph
                    if self.knowledge_graph:
                        for relationship in relationships:
                            self.knowledge_graph.add_relationship(relationship)

                    logger.debug(f"Indexed {file_path}: {len(symbols)} symbols")

                    # Save updated indexes
                    self._save_all_indexes()

                except Exception as e:
                    logger.warning(f"AST parsing failed for {file_path}: {e}")

        # Phase 2: Vector embedding (parent class method)
        return super().add_document(
            content=content,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap or self._get_default_chunk_overlap(),
            model=model or self._get_default_model(),
            max_tokens=max_tokens,
        )

    def _get_default_chunk_overlap(self) -> int:
        """Get default chunk overlap from config."""
        try:
            from athenah_ai.config import config

            return config.text_processing.indexer_chunk_overlap
        except:
            return 200

    def _get_default_model(self) -> str:
        """Get default embedding model from config."""
        try:
            from athenah_ai.config import config

            return config.indexer.embedding_model
        except:
            return "text-embedding-3-small"

    # ========== Hybrid Query Interface ==========

    def query(self, query_text: str, **kwargs) -> QueryResult:
        """
        Execute hybrid query using intelligent routing.

        Examples:
        - "find function processData" -> Symbol index (exact)
        - "what calls processData?" -> Knowledge graph (structural)
        - "find similar error handling patterns" -> Vector store (semantic)
        - "processData usage examples" -> Hybrid (all layers)

        Args:
            query_text: Natural language query
            **kwargs: Additional parameters (limit, filters, etc.)

        Returns:
            QueryResult with results and metadata
        """
        if not self.query_engine:
            raise RuntimeError(
                "Hybrid query engine not available (AST parsing disabled)"
            )

        return self.query_engine.query(query_text, **kwargs)

    def find_symbol(
        self, name: str, kind: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find symbol by name (exact match).

        Args:
            name: Symbol name
            kind: Optional kind filter (function, class, etc.)

        Returns:
            List of matching symbols
        """
        if not self.query_engine:
            return []

        return self.query_engine.find_symbol(name, kind)

    def find_callers(self, symbol_name: str) -> List[Dict[str, Any]]:
        """
        Find all functions/methods that call the given symbol.

        Args:
            symbol_name: Symbol to find callers for

        Returns:
            List of caller symbols
        """
        if not self.knowledge_graph:
            return []

        return self.knowledge_graph.find_callers(symbol_name)

    def find_callees(self, symbol_name: str) -> List[Dict[str, Any]]:
        """
        Find all functions/methods called by the given symbol.

        Args:
            symbol_name: Symbol to find callees for

        Returns:
            List of called symbols
        """
        if not self.knowledge_graph:
            return []

        return self.knowledge_graph.find_callees(symbol_name)

    def get_inheritance_tree(self, class_name: str) -> Dict[str, Any]:
        """
        Get inheritance hierarchy for a class.

        Args:
            class_name: Class to get hierarchy for

        Returns:
            Inheritance tree
        """
        if not self.knowledge_graph:
            return {}

        return self.knowledge_graph.get_inheritance_tree(class_name, "ancestors")

    def get_call_graph(self, symbol_name: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Get call graph for a symbol.

        Args:
            symbol_name: Symbol to get call graph for
            max_depth: Maximum traversal depth

        Returns:
            Call graph
        """
        if not self.knowledge_graph:
            return {}

        return self.knowledge_graph.get_call_graph(symbol_name, max_depth)

    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions for symbol names.

        Args:
            prefix: Prefix to complete
            limit: Maximum suggestions

        Returns:
            List of symbol name suggestions
        """
        if not self.symbol_index:
            return []

        return self.symbol_index.autocomplete(prefix, limit)

    def get_symbol_context(self, symbol_name: str) -> Dict[str, Any]:
        """
        Get comprehensive context for a symbol.

        Includes:
        - Definition (file, line, signature)
        - Callers and callees
        - Inheritance (if class)
        - Similar code examples

        Args:
            symbol_name: Symbol to get context for

        Returns:
            Dictionary with full symbol context
        """
        if not self.query_engine:
            return {}

        return self.query_engine.get_symbol_context(symbol_name)

    # ========== Statistics ==========

    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all layers."""
        stats = {
            "vector_store": {
                "collection_name": (
                    self._collection_name if hasattr(self, "_collection_name") else None
                ),
                "total_chunks": (
                    self._collection.count()
                    if hasattr(self, "_collection") and self._collection
                    else 0
                ),
            }
        }

        if self.query_engine:
            stats.update(self.query_engine.get_statistics())

        return stats

    # ========== Convenience Methods (Backwards Compatible API) ==========

    def index_dir(
        self,
        source: str,
        clean_dir: bool = False,
    ) -> int:
        """Index directory (backwards compatible)."""
        return self.build_from_dir(source, clean_dir)

    def index_dirs(
        self,
        source: str,
        dirs: List[str] = None,
        include_root: bool = False,
        clean_dirs: bool = False,
    ) -> int:
        """Index multiple directories (backwards compatible)."""
        if dirs == ["."]:
            return self.build_from_dir(source, clean_dirs)

        return self.build_from_dirs(source, dirs, include_root, clean_dirs)

    def index_files(
        self,
        file_paths: List[str],
    ) -> bool:
        """Index files (backwards compatible)."""
        return self.build_from_files(file_paths)

    def index_file(self, file_path: str, clean_file: bool = False) -> bool:
        """Index single file (backwards compatible)."""
        return self.build_from_file(file_path, clean_file)

    # ========== Load Override ==========

    def load(self) -> bool:
        """
        Load all index layers.

        Note: Returns True if ANY layer loads successfully (progressive RAG support).
        Vector collection may not exist yet - callers should check self._collection directly.

        Returns:
            True if at least one layer loaded successfully
        """
        success_vector = super().load()

        success_symbol = False
        if self.symbol_index:
            success_symbol = self.symbol_index.load()

        success_graph = False
        if self.knowledge_graph:
            success_graph = self.knowledge_graph.load()

        # Consider success if any layer loaded
        overall_success = success_vector or success_symbol or success_graph

        if overall_success:
            logger.info(
                f"Loaded hybrid index: "
                f"vector={success_vector}, symbol={success_symbol}, graph={success_graph}"
            )

        return overall_success


# Convenience factory function
def create_indexer(
    name: str,
    storage_type: str = "local",
    dir: str = "dist",
    version: str = "v1",
    enable_graph: bool = True,
) -> IndexClient:
    """
    Create an index client with sensible defaults.

    Args:
        name: Index name
        storage_type: Storage backend (local or gcs)
        dir: Storage directory
        version: Index version
        enable_graph: Enable knowledge graph (default: True)

    Returns:
        Configured IndexClient
    """
    return IndexClient(
        storage_type=storage_type,
        id="default",
        dir=dir,
        name=name,
        version=version,
        enable_ast=True,
        enable_graph=enable_graph,
    )
