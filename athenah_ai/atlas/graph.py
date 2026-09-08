"""AtlasGraph: in-memory queries over atlas facts.

Mirrors the shape of ``indexer/knowledge_graph.py`` (nx.MultiDiGraph plus
secondary indexes) but is always rebuilt from the YAML FactStore — never
pickled. The YAML facts are the single source of truth.
"""

import fnmatch
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import networkx as nx

from athenah_ai.atlas.schema import Edge, Node
from athenah_ai.atlas.store import FactStore

_CAPABILITY_KINDS = ("can_write", "can_comment", "can_review")


def _expand(path: str) -> str:
    return os.path.realpath(os.path.expanduser(path))


def to_tilde(path: str) -> str:
    """Return a path tilde-relative to the current user's home.

    Args:
        path: Absolute or ~-relative path.

    Returns:
        The path with the home prefix replaced by ``~`` when applicable.
    """
    home = os.path.expanduser("~")
    expanded = os.path.expanduser(path)
    if expanded == home or expanded.startswith(home + os.sep):
        return "~" + expanded[len(home):]
    return expanded


@dataclass
class AtlasContext:
    """Everything a zero-context agent needs about one working directory."""

    checkout: Optional[Node] = None
    main_checkout: Optional[Node] = None
    worktrees: List[Node] = field(default_factory=list)
    repo: Optional[Node] = None
    org: Optional[Node] = None
    capabilities: List[Edge] = field(default_factory=list)
    workflows: List[Node] = field(default_factory=list)
    plan_stores: List[Node] = field(default_factory=list)
    servers: List[Node] = field(default_factory=list)
    rules: List[Node] = field(default_factory=list)
    plans: List[Node] = field(default_factory=list)
    repo_plans: List[Node] = field(default_factory=list)


class AtlasGraph:
    """Typed entity graph over the life/job facts."""

    def __init__(self, nodes: List[Node], edges: List[Edge],
                 store: Optional[FactStore] = None):
        """Build the graph from facts.

        Args:
            nodes: Merged fact nodes.
            edges: Merged fact edges.
            store: Optional originating store (enables source citations).
        """
        self.store = store
        self.nodes_by_id: Dict[str, Node] = {n.id: n for n in nodes}
        self.by_kind: Dict[str, List[str]] = {}
        self.checkout_by_path: Dict[str, str] = {}
        self.graph = nx.MultiDiGraph()

        for node in nodes:
            self.graph.add_node(node.id)
            self.by_kind.setdefault(node.kind, []).append(node.id)
            if node.kind == "checkout":
                path = node.attrs.get("path") or node.id.split(":", 1)[1]
                self.checkout_by_path[_expand(path)] = node.id
        for kind in self.by_kind:
            self.by_kind[kind].sort()

        self.edges: List[Edge] = list(edges)
        for edge in edges:
            if edge.src in self.nodes_by_id and edge.dst in self.nodes_by_id:
                self.graph.add_edge(edge.src, edge.dst, kind=edge.kind,
                                    fact=edge)

    # ------------------------------------------------------ constructors

    @classmethod
    def from_facts(cls, nodes: List[Node], edges: List[Edge]) -> "AtlasGraph":
        """Build a graph from in-memory facts.

        Args:
            nodes: Fact nodes.
            edges: Fact edges.

        Returns:
            The constructed AtlasGraph.
        """
        return cls(nodes, edges)

    @classmethod
    def from_store(cls, store: FactStore) -> "AtlasGraph":
        """Build a graph by loading a FactStore.

        Args:
            store: The fact store to load.

        Returns:
            The constructed AtlasGraph.

        Raises:
            AtlasValidationError: If the store's facts are invalid.
        """
        nodes, edges = store.load()
        return cls(nodes, edges, store=store)

    # ----------------------------------------------------------- helpers

    def without_provenance(self, provenance: str) -> "AtlasGraph":
        """Return a copy of the graph with one provenance layer removed.

        Args:
            provenance: Layer to drop, e.g. ``proposed``.

        Returns:
            A new AtlasGraph without those facts (edges touching dropped
            nodes are dropped too).
        """
        nodes = [
            n for n in self.nodes_by_id.values()
            if n.provenance != provenance
        ]
        ids = {n.id for n in nodes}
        edges = [
            e for e in self.edges
            if e.provenance != provenance and e.src in ids and e.dst in ids
        ]
        return AtlasGraph(nodes, edges, store=self.store)

    def node(self, node_id: str) -> Optional[Node]:
        """Return a node by id.

        Args:
            node_id: Full node id.

        Returns:
            The Node or None.
        """
        return self.nodes_by_id.get(node_id)

    def _out(self, node_id: str, kind: str) -> List[Node]:
        if node_id not in self.graph:
            return []
        hits = []
        for _, dst, data in self.graph.out_edges(node_id, data=True):
            if data.get("kind") == kind:
                hits.append(self.nodes_by_id[dst])
        return sorted(hits, key=lambda n: n.id)

    def _in(self, node_id: str, kind: str) -> List[Node]:
        if node_id not in self.graph:
            return []
        hits = []
        for src, _, data in self.graph.in_edges(node_id, data=True):
            if data.get("kind") == kind:
                hits.append(self.nodes_by_id[src])
        return sorted(hits, key=lambda n: n.id)

    # ----------------------------------------------------------- queries

    def resolve_cwd(self, path: str) -> Optional[str]:
        """Resolve a filesystem path to the checkout containing it.

        Args:
            path: Any path; subdirectories resolve to their checkout via
                longest-prefix match.

        Returns:
            The checkout node id, or None when no checkout contains it.
        """
        target = _expand(path)
        best: Tuple[int, Optional[str]] = (-1, None)
        for cpath, cid in self.checkout_by_path.items():
            if target == cpath or target.startswith(cpath + os.sep):
                if len(cpath) > best[0]:
                    best = (len(cpath), cid)
        return best[1]

    def who_owns(self, ref: str) -> Optional[Node]:
        """Return the org that owns a repo.

        Args:
            ref: A ``repo:`` node id, an ``Owner/name`` string, or a
                filesystem path inside a checkout.

        Returns:
            The owning org Node, or None if unknown.
        """
        repo: Optional[Node] = None
        if ref.startswith("repo:"):
            repo = self.node(ref)
        elif self.node(f"repo:{ref}") is not None:
            repo = self.node(f"repo:{ref}")
        else:
            cid = self.resolve_cwd(ref)
            if cid:
                repos = self._out(cid, "checkout_of")
                repo = repos[0] if repos else None
        if repo is None:
            return None
        owners = self._out(repo.id, "owned_by")
        return owners[0] if owners else None

    def context_for(self, cwd: str) -> AtlasContext:
        """Assemble the scoped bootstrap context for a working directory.

        Args:
            cwd: Path inside a known checkout.

        Returns:
            AtlasContext; fields are None/empty for whatever is unknown.
        """
        ctx = AtlasContext()
        cid = self.resolve_cwd(cwd)
        if cid is None:
            return ctx
        ctx.checkout = self.node(cid)
        ctx.plans = self._out(cid, "governed_by")

        mains = self._out(cid, "worktree_of")
        ctx.main_checkout = mains[0] if mains else ctx.checkout
        ctx.worktrees = [
            n for n in self._in(ctx.main_checkout.id, "worktree_of")
            if n.id != cid
        ]

        repos = self._out(cid, "checkout_of")
        ctx.repo = repos[0] if repos else None
        if ctx.repo is None:
            return ctx
        orgs = self._out(ctx.repo.id, "owned_by")
        ctx.org = orgs[0] if orgs else None
        seen = {n.id for n in ctx.plans}
        ctx.repo_plans = sorted(
            (n for n in self._out(ctx.repo.id, "governed_by") if n.id not in seen),
            key=lambda n: n.id,
        )

        scope_ids = {ctx.repo.id}
        if ctx.org is not None:
            scope_ids.add(ctx.org.id)
        ctx.capabilities = sorted(
            (e for e in self.edges
             if e.kind in _CAPABILITY_KINDS and e.dst in scope_ids),
            key=lambda e: (e.src, e.kind),
        )
        for scope in sorted(scope_ids):
            ctx.workflows += self._out(scope, "deploys_via")
            ctx.plan_stores += self._out(scope, "plans_in")
            ctx.servers += self._out(scope, "deploys_to")
            ctx.rules += [
                n for n in self._in(scope, "documented_in")
                if n.kind == "rule"
            ]
        for workflow in ctx.workflows:
            ctx.servers += self._out(workflow.id, "deploys_to")
        ctx.servers = sorted(
            {n.id: n for n in ctx.servers}.values(), key=lambda n: n.id
        )

        # Conditional rules scoped here via applies_to (checkout, repo, org,
        # plus everything reachable: workflows, servers).
        rule_scopes = [cid] + sorted(scope_ids)
        rule_scopes += [n.id for n in ctx.workflows]
        rule_scopes += [n.id for n in ctx.servers]
        for scope in rule_scopes:
            ctx.rules += self._in(scope, "applies_to")
        ctx.rules = sorted(
            {n.id: n for n in ctx.rules}.values(), key=lambda n: n.id
        )
        return ctx

    def capabilities_of(self, identity_id: str) -> List[Edge]:
        """Return an identity's capability edges.

        Args:
            identity_id: The ``identity:`` node id.

        Returns:
            Sorted list of can_write/can_comment/can_review edges.
        """
        return sorted(
            (e for e in self.edges
             if e.src == identity_id and e.kind in _CAPABILITY_KINDS),
            key=lambda e: (e.kind, e.dst),
        )

    def find(self, kind: str, pattern: str = "*") -> List[Node]:
        """Find nodes of a kind whose name or id-tail matches a glob.

        Args:
            kind: Node kind.
            pattern: fnmatch glob applied to name and id tail.

        Returns:
            Matching nodes sorted by id.
        """
        hits = []
        for node_id in self.by_kind.get(kind, []):
            node = self.nodes_by_id[node_id]
            tail = node.id.split(":", 1)[1]
            if (fnmatch.fnmatch(node.name, pattern)
                    or fnmatch.fnmatch(tail, pattern)):
                hits.append(node)
        return hits

    def neighbors(self, node_id: str) -> Dict[str, List[Tuple[str, str]]]:
        """Return a node's edges grouped by edge kind.

        Args:
            node_id: The node id.

        Returns:
            Mapping edge kind -> list of (direction, other node id),
            direction being ``out`` or ``in``.
        """
        groups: Dict[str, List[Tuple[str, str]]] = {}
        if node_id not in self.graph:
            return groups
        for _, dst, data in self.graph.out_edges(node_id, data=True):
            groups.setdefault(data["kind"], []).append(("out", dst))
        for src, _, data in self.graph.in_edges(node_id, data=True):
            groups.setdefault(data["kind"], []).append(("in", src))
        for kind in groups:
            groups[kind].sort()
        return groups

    def why(
        self, src: str, dst: Optional[str] = None
    ) -> List[Tuple[Edge, str, Optional[str]]]:
        """Explain the edges touching src (optionally narrowed to dst).

        Args:
            src: Source node id.
            dst: Optional destination node id filter.

        Returns:
            List of (edge, provenance, source file) rows; the source file
            is None when the graph was not loaded from a store.
        """
        rows = []
        for edge in self.edges:
            if edge.src != src and edge.dst != src:
                continue
            if dst is not None and dst not in (edge.src, edge.dst):
                continue
            source = self.store.source_of(edge) if self.store else None
            rows.append((edge, edge.provenance, source))
        return sorted(rows, key=lambda r: (r[0].kind, r[0].src, r[0].dst))
