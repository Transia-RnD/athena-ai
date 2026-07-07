"""FactStore: YAML persistence and layering for atlas facts.

Two layers live under the facts directory:

* taught  — ``*.yaml`` at the top level; human-owned, edited by hand or via
  ``teach``. The scanner never writes here.
* derived — ``derived/*.yaml``; machine-owned, rewritten wholesale by the
  scanner so stale facts disappear on rescan.

Merge contract (the load-time source of truth):

* Node present in both layers: taught wins ``name``/``notes``/``provenance``;
  ``attrs`` merge as ``{**derived.attrs, **taught.attrs}`` so scanner
  freshness (branch, last_seen) flows through unless the taught file pins
  the key.
* Edge with the same ``(kind, src, dst)`` in both layers: taught kept.
* ``imported`` provenance lives in taught files and behaves as taught.
"""

import os
from typing import Dict, List, Optional, Tuple, Union

import yaml

from athenah_ai.atlas.schema import Edge, Node, validate

# node kind -> taught domain file
_KIND_TO_FILE = {
    "person": "identities.yaml",
    "identity": "identities.yaml",
    "org": "orgs.yaml",
    "repo": "repos.yaml",
    "checkout": "repos.yaml",
    "server": "servers.yaml",
    "service": "servers.yaml",
    "environment": "servers.yaml",
    "workflow": "workflows.yaml",
    "skill": "workflows.yaml",
    "rule": "rules.yaml",
    "plan_store": "plan_stores.yaml",
}
_DEFAULT_FILE = "misc.yaml"

_NODE_FIELD_ORDER = ("id", "kind", "name", "provenance", "notes", "attrs")
_EDGE_FIELD_ORDER = ("kind", "src", "dst", "provenance", "notes", "attrs")


class AtlasValidationError(Exception):
    """Raised when facts fail schema validation; message lists every error."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


def _node_to_dict(node: Node) -> dict:
    data = {"id": node.id, "kind": node.kind, "name": node.name,
            "provenance": node.provenance}
    if node.notes:
        data["notes"] = node.notes
    if node.attrs:
        data["attrs"] = {k: node.attrs[k] for k in sorted(node.attrs)}
    return data


def _edge_to_dict(edge: Edge) -> dict:
    data = {"kind": edge.kind, "src": edge.src, "dst": edge.dst,
            "provenance": edge.provenance}
    if edge.notes:
        data["notes"] = edge.notes
    if edge.attrs:
        data["attrs"] = {k: edge.attrs[k] for k in sorted(edge.attrs)}
    return data


def _node_from_dict(data: dict, source: str) -> Node:
    return Node(
        id=str(data.get("id", "")),
        kind=str(data.get("kind", "")),
        name=str(data.get("name", "")),
        provenance=str(data.get("provenance", "")),
        notes=str(data.get("notes", "") or ""),
        attrs=data.get("attrs") or {},
    )


def _edge_from_dict(data: dict, source: str) -> Edge:
    return Edge(
        kind=str(data.get("kind", "")),
        src=str(data.get("src", "")),
        dst=str(data.get("dst", "")),
        provenance=str(data.get("provenance", "")),
        notes=str(data.get("notes", "") or ""),
        attrs=data.get("attrs") or {},
    )


def _dump(nodes: List[Node], edges: List[Edge]) -> str:
    payload = {}
    if nodes:
        payload["nodes"] = [
            _node_to_dict(n) for n in sorted(nodes, key=lambda n: n.id)
        ]
    if edges:
        payload["edges"] = [
            _edge_to_dict(e) for e in sorted(edges, key=lambda e: e.key())
        ]
    return yaml.safe_dump(
        payload, sort_keys=False, allow_unicode=True, width=88
    )


class FactStore:
    """Loads, merges, and persists atlas facts under one directory."""

    def __init__(self, facts_dir: str):
        """Initialize the store.

        Args:
            facts_dir: Directory holding taught ``*.yaml`` files and the
                ``derived/`` subdirectory. Expanded with expanduser.
        """
        self.facts_dir = os.path.expanduser(facts_dir)
        self.derived_dir = os.path.join(self.facts_dir, "derived")
        self._sources: Dict[Union[str, Tuple[str, str, str]], str] = {}

    # ------------------------------------------------------------- load

    def _layer_files(self, derived: bool) -> List[str]:
        base = self.derived_dir if derived else self.facts_dir
        if not os.path.isdir(base):
            return []
        return sorted(
            os.path.join(base, f)
            for f in os.listdir(base)
            if f.endswith((".yaml", ".yml"))
            and os.path.isfile(os.path.join(base, f))
        )

    def _read_layer(
        self, derived: bool
    ) -> Tuple[List[Node], List[Edge], List[str]]:
        nodes: List[Node] = []
        edges: List[Edge] = []
        errors: List[str] = []
        for path in self._layer_files(derived):
            rel = os.path.relpath(path, self.facts_dir)
            try:
                with open(path, "r") as f:
                    data = yaml.safe_load(f) or {}
            except yaml.YAMLError as exc:
                errors.append(f"{rel}: invalid YAML ({exc})")
                continue
            if not isinstance(data, dict):
                errors.append(f"{rel}: top level must be a mapping")
                continue
            for raw in data.get("nodes") or []:
                node = _node_from_dict(raw, rel)
                nodes.append(node)
                self._sources[node.id] = rel
            for raw in data.get("edges") or []:
                edge = _edge_from_dict(raw, rel)
                edges.append(edge)
                self._sources[edge.key()] = rel
        return nodes, edges, errors

    @staticmethod
    def _merge_nodes(taught: List[Node], derived: List[Node]) -> List[Node]:
        derived_by_id = {n.id: n for n in derived}
        merged: List[Node] = []
        for node in taught:
            shadow = derived_by_id.pop(node.id, None)
            if shadow is not None:
                node = Node(
                    id=node.id,
                    kind=node.kind,
                    name=node.name,
                    provenance=node.provenance,
                    notes=node.notes,
                    attrs={**shadow.attrs, **node.attrs},
                )
            merged.append(node)
        merged.extend(derived_by_id.values())
        return merged

    @staticmethod
    def _merge_edges(taught: List[Edge], derived: List[Edge]) -> List[Edge]:
        taught_keys = {e.key() for e in taught}
        return list(taught) + [
            e for e in derived if e.key() not in taught_keys
        ]

    @staticmethod
    def _layer_duplicates(nodes: List[Node], layer: str) -> List[str]:
        seen = set()
        errors = []
        for node in nodes:
            if node.id in seen:
                errors.append(
                    f"duplicate node id '{node.id}' in {layer} layer"
                )
            seen.add(node.id)
        return errors

    def load(self) -> Tuple[List[Node], List[Edge]]:
        """Load, merge, and validate all facts.

        Returns:
            Tuple (nodes, edges) after taught-over-derived merging.

        Raises:
            AtlasValidationError: If any file is malformed or the merged
                facts fail schema validation.
        """
        self._sources = {}
        t_nodes, t_edges, errors = self._read_layer(derived=False)
        d_nodes, d_edges, d_errors = self._read_layer(derived=True)
        errors += d_errors
        errors += self._layer_duplicates(t_nodes, "taught")
        errors += self._layer_duplicates(d_nodes, "derived")

        nodes = self._merge_nodes(t_nodes, d_nodes)
        edges = self._merge_edges(t_edges, d_edges)

        schema_errors, _ = validate(nodes, edges)
        errors += [self._with_source(e) for e in schema_errors]
        if errors:
            raise AtlasValidationError(errors)
        return nodes, edges

    def _with_source(self, error: str) -> str:
        for key, rel in self._sources.items():
            if isinstance(key, str) and f"'{key}'" in error:
                return f"{rel}: {error}"
        return error

    def warnings(self) -> List[str]:
        """Return schema warnings for the current facts (best effort).

        Returns:
            Warning strings; empty when facts are fully standard.
        """
        t_nodes, t_edges, _ = self._read_layer(derived=False)
        d_nodes, d_edges, _ = self._read_layer(derived=True)
        _, warns = validate(
            self._merge_nodes(t_nodes, d_nodes),
            self._merge_edges(t_edges, d_edges),
        )
        return warns

    def source_of(self, fact: Union[Node, Edge]) -> Optional[str]:
        """Return the facts-dir-relative file a fact was loaded from.

        Args:
            fact: A Node or Edge returned by load().

        Returns:
            Relative path like ``repos.yaml`` or None if unknown.
        """
        key = fact.id if isinstance(fact, Node) else fact.key()
        return self._sources.get(key)

    # ------------------------------------------------------------ write

    def write_derived(
        self, domain: str, nodes: List[Node], edges: List[Edge]
    ) -> str:
        """Wholesale-rewrite one derived domain file.

        Args:
            domain: Basename without extension, e.g. ``checkouts``.
            nodes: Derived nodes for this domain.
            edges: Derived edges for this domain.

        Returns:
            Path of the file written.
        """
        os.makedirs(self.derived_dir, exist_ok=True)
        path = os.path.join(self.derived_dir, f"{domain}.yaml")
        with open(path, "w") as f:
            f.write(
                "# machine-owned; rewritten by "
                "`python -m athenah_ai.atlas scan` — do not hand-edit\n"
            )
            f.write(_dump(nodes, edges))
        return path

    def _taught_file_for(self, fact: Union[Node, Edge]) -> str:
        if isinstance(fact, Node):
            kind = fact.kind
        else:
            kind = fact.src.split(":", 1)[0]
        return os.path.join(
            self.facts_dir, _KIND_TO_FILE.get(kind, _DEFAULT_FILE)
        )

    def _teach(self, fact: Union[Node, Edge]) -> None:
        # Work on the RAW taught layer so merged-in derived attrs are never
        # frozen into a taught file.
        self._sources = {}
        t_nodes, t_edges, errors = self._read_layer(derived=False)
        d_nodes, d_edges, d_errors = self._read_layer(derived=True)
        errors += d_errors
        if errors:
            raise AtlasValidationError(errors)

        if isinstance(fact, Node):
            t_nodes = [n for n in t_nodes if n.id != fact.id] + [fact]
        else:
            t_edges = [e for e in t_edges if e.key() != fact.key()] + [fact]

        merged_nodes = self._merge_nodes(t_nodes, d_nodes)
        merged_edges = self._merge_edges(t_edges, d_edges)
        errors = self._layer_duplicates(t_nodes, "taught")
        schema_errors, _ = validate(merged_nodes, merged_edges)
        errors += schema_errors
        if errors:
            raise AtlasValidationError(errors)

        path = self._taught_file_for(fact)
        rel = os.path.relpath(path, self.facts_dir)
        file_nodes = [
            n for n in t_nodes
            if self._sources.get(n.id, rel if n is fact else None) == rel
        ]
        file_edges = [
            e for e in t_edges
            if self._sources.get(e.key(), rel if e is fact else None) == rel
        ]

        os.makedirs(self.facts_dir, exist_ok=True)
        with open(path, "w") as f:
            f.write(_dump(file_nodes, file_edges))

    def teach_node(self, node: Node) -> None:
        """Validate and persist a taught node into its domain file.

        Args:
            node: The node to teach.

        Raises:
            AtlasValidationError: If adding the node yields invalid facts.
        """
        self._teach(node)

    def teach_edge(self, edge: Edge) -> None:
        """Validate and persist a taught edge into its domain file.

        Args:
            edge: The edge to teach.

        Raises:
            AtlasValidationError: If adding the edge yields invalid facts.
        """
        self._teach(edge)
