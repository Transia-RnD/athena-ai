"""Atlas schema: closed kind vocabularies, Node/Edge facts, validate().

Stable id conventions (enforced by validate, produced by make_id):
    org:        lowercase slug            org:transia-rnd
    repo:       exact Owner/name          repo:Transia-RnD/athenah-ai
    identity:   provider/login            identity:github/dangell8
    checkout:   tilde-relative path       checkout:~/projects/transia/athenah-ai
    others:     lowercase slug            server:sentinel, workflow:deploy-alphanet

Kinds prefixed ``x-`` are accepted with a warning (escape hatch for facts
that do not fit the closed vocabulary yet).
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple

NODE_KINDS = frozenset({
    "person",
    "identity",
    "org",
    "repo",
    "checkout",
    "server",
    "service",
    "workflow",
    "skill",
    "rule",
    "plan_store",
    "plan",
    "environment",
})

EDGE_KINDS = frozenset({
    "owned_by",
    "checkout_of",
    "worktree_of",
    "plans_in",
    "deploys_to",
    "deploys_via",
    "can_write",
    "can_comment",
    "can_review",
    "consumes",
    "runs_on",
    "member_of",
    "operates",
    "documented_in",
    "applies_to",
    "governed_by",
})

# "proposed" facts are agent-suggested and await human review; renders skip
# them until `review --accept` flips them to taught.
PROVENANCE = frozenset({"taught", "derived", "imported", "proposed"})

# edge kind -> (allowed src kinds, allowed dst kinds). Kinds absent from the
# table are unconstrained beyond the closed vocabulary.
EDGE_ENDPOINT_RULES: Dict[str, Tuple[frozenset, frozenset]] = {
    "owned_by": (frozenset({"repo"}), frozenset({"org", "person"})),
    "checkout_of": (frozenset({"checkout"}), frozenset({"repo"})),
    "worktree_of": (frozenset({"checkout"}), frozenset({"checkout"})),
    "governed_by": (frozenset({"checkout", "repo"}), frozenset({"plan"})),
    "plans_in": (
        frozenset({"repo", "org", "workflow"}),
        frozenset({"plan_store", "repo"}),
    ),
    "deploys_to": (
        frozenset({"repo", "workflow", "service"}),
        frozenset({"server", "environment"}),
    ),
    "deploys_via": (
        frozenset({"repo", "service", "environment"}),
        frozenset({"workflow"}),
    ),
    "can_write": (frozenset({"identity"}), frozenset({"org", "repo"})),
    "can_comment": (frozenset({"identity"}), frozenset({"org", "repo"})),
    "can_review": (frozenset({"identity"}), frozenset({"org", "repo"})),
    "member_of": (frozenset({"person", "identity"}), frozenset({"org"})),
    "operates": (
        frozenset({"person", "identity"}),
        frozenset({"server", "service", "repo", "org"}),
    ),
    "runs_on": (frozenset({"service", "environment"}), frozenset({"server"})),
    "consumes": (
        frozenset({"repo", "service"}),
        frozenset({"repo", "service"}),
    ),
    "documented_in": (
        frozenset(NODE_KINDS),
        frozenset({"plan_store", "repo", "checkout"}),
    ),
    "applies_to": (
        frozenset({"rule"}),
        frozenset({
            "org", "repo", "server", "service", "environment",
            "workflow", "skill", "checkout",
        }),
    ),
}


@dataclass(frozen=True)
class Node:
    """A fact node: one entity in the life graph."""

    id: str
    kind: str
    name: str
    provenance: str
    notes: str = ""
    attrs: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Edge:
    """A fact edge: a typed relationship between two nodes."""

    kind: str
    src: str
    dst: str
    provenance: str
    notes: str = ""
    attrs: Dict[str, Any] = field(default_factory=dict)

    def key(self) -> Tuple[str, str, str]:
        """Return the identity used for dedup/merge across layers.

        Returns:
            Tuple of (kind, src, dst).
        """
        return (self.kind, self.src, self.dst)


def make_id(kind: str, key: str) -> str:
    """Build a stable node id for a kind.

    Args:
        kind: Node kind (must be in NODE_KINDS or ``x-`` prefixed).
        key: Kind-specific key. ``repo``, ``identity``, and ``checkout``
            keys are preserved verbatim; other kinds are slugified to
            lowercase.

    Returns:
        The node id, e.g. ``org:transia-rnd``.
    """
    if kind in ("repo", "identity", "checkout"):
        return f"{kind}:{key}"
    return f"{kind}:{key.strip().lower().replace(' ', '-')}"


def _is_escape_kind(kind: str) -> bool:
    return isinstance(kind, str) and kind.startswith("x-")


def _check_node(node: Node, errors: List[str], warnings: List[str]) -> None:
    if _is_escape_kind(node.kind):
        warnings.append(f"node {node.id}: non-standard kind '{node.kind}'")
    elif node.kind not in NODE_KINDS:
        errors.append(f"node {node.id}: unknown kind '{node.kind}'")

    if not node.id.startswith(f"{node.kind}:"):
        errors.append(
            f"node {node.id}: id prefix does not match kind '{node.kind}'"
        )
    if node.provenance not in PROVENANCE:
        errors.append(
            f"node {node.id}: bad provenance '{node.provenance}'"
        )
    if not node.name:
        errors.append(f"node {node.id}: empty name")
    if not isinstance(node.attrs, dict):
        errors.append(f"node {node.id}: attrs must be a mapping")


def _check_edge(
    edge: Edge,
    kind_of: Dict[str, str],
    errors: List[str],
    warnings: List[str],
) -> None:
    label = f"edge {edge.kind} {edge.src} -> {edge.dst}"
    if _is_escape_kind(edge.kind):
        warnings.append(f"{label}: non-standard kind '{edge.kind}'")
    elif edge.kind not in EDGE_KINDS:
        errors.append(f"{label}: unknown kind '{edge.kind}'")

    if edge.provenance not in PROVENANCE:
        errors.append(f"{label}: bad provenance '{edge.provenance}'")
    if not isinstance(edge.attrs, dict):
        errors.append(f"{label}: attrs must be a mapping")

    dangling = False
    for endpoint in (edge.src, edge.dst):
        if endpoint not in kind_of:
            errors.append(f"{label}: dangling endpoint '{endpoint}'")
            dangling = True
    if dangling:
        return

    rule = EDGE_ENDPOINT_RULES.get(edge.kind)
    if rule is not None:
        src_kinds, dst_kinds = rule
        src_kind, dst_kind = kind_of[edge.src], kind_of[edge.dst]
        if not _is_escape_kind(src_kind) and src_kind not in src_kinds:
            errors.append(
                f"{label}: '{edge.kind}' src must be one of "
                f"{sorted(src_kinds)}, got '{src_kind}'"
            )
        if not _is_escape_kind(dst_kind) and dst_kind not in dst_kinds:
            errors.append(
                f"{label}: '{edge.kind}' dst must be one of "
                f"{sorted(dst_kinds)}, got '{dst_kind}'"
            )


def validate(
    nodes: List[Node], edges: List[Edge]
) -> Tuple[List[str], List[str]]:
    """Validate a merged fact set.

    Duplicate node ids are only an error when they collide within the same
    provenance layer; callers pass the post-merge set, so any duplicate seen
    here is a real error.

    Args:
        nodes: Merged nodes (one entry per id).
        edges: Merged edges.

    Returns:
        Tuple (errors, warnings); empty errors means the facts are valid.
    """
    errors: List[str] = []
    warnings: List[str] = []

    seen: Dict[str, str] = {}
    for node in nodes:
        if node.id in seen:
            errors.append(f"duplicate node id '{node.id}'")
            continue
        seen[node.id] = node.kind
        _check_node(node, errors, warnings)

    for edge in edges:
        _check_edge(edge, seen, errors, warnings)

    return errors, warnings
