"""Deterministic markdown rendering of the atlas.

Three products:

* ``render_atlas``     — the full ATLAS.md ("init into my life").
* ``render_context``   — scoped bootstrap for one working directory.
* ``render_claude_md`` — the generated global CLAUDE.md for Claude Code.

No LLM involved; every line is traceable to a fact, and rendering the same
graph twice yields identical bytes.
"""

from typing import List

from athenah_ai.atlas.graph import AtlasContext, AtlasGraph
from athenah_ai.atlas.schema import NODE_KINDS, Node

_REGEN_HINT = (
    "regenerate: `python -m athenah_ai.atlas render` — edit facts, "
    "not this file"
)


def _title(node: Node) -> str:
    return f"**{node.name}** (`{node.id}`)"


def _note_suffix(text: str) -> str:
    return f" — {text}" if text else ""


def _identities(graph: AtlasGraph, lines: List[str]) -> None:
    lines.append("## Identities & Capabilities")
    lines.append("")
    for kind in ("person", "identity"):
        for node in graph.find(kind):
            lines.append(f"- {_title(node)}{_note_suffix(node.notes)}")
            for cap in graph.capabilities_of(node.id):
                lines.append(
                    f"  - `{cap.kind}` → `{cap.dst}`"
                    f"{_note_suffix(cap.notes)}"
                )
            for other in graph._out(node.id, "member_of"):
                lines.append(f"  - member of `{other.id}`")
    lines.append("")


def _orgs(graph: AtlasGraph, lines: List[str]) -> None:
    lines.append("## Organizations")
    lines.append("")
    for node in graph.find("org"):
        repos = graph._in(node.id, "owned_by")
        suffix = f" — {len(repos)} repo(s)" if repos else ""
        lines.append(f"- {_title(node)}{_note_suffix(node.notes)}{suffix}")
    lines.append("")


def _checkout_row(graph: AtlasGraph, node: Node) -> str:
    repos = graph._out(node.id, "checkout_of")
    repo = repos[0].id.split(":", 1)[1] if repos else "—"
    orgs = graph._out(repos[0].id, "owned_by") if repos else []
    org = orgs[0].name if orgs else "—"
    branch = node.attrs.get("branch", "detached" if node.attrs.get(
        "detached") else "—")
    notes = []
    mains = graph._out(node.id, "worktree_of")
    if mains:
        notes.append(f"worktree of `{mains[0].attrs.get('path', mains[0].id)}`")
    if node.attrs.get("no_remote"):
        notes.append("no remote")
    if node.notes:
        notes.append(node.notes)
    path = node.attrs.get("path", node.id.split(":", 1)[1])
    return (
        f"| `{path}` | {repo} | {org} | {branch} | "
        f"{'; '.join(notes) if notes else ''} |"
    )


def _repo_map(graph: AtlasGraph, lines: List[str]) -> None:
    lines.append("## Repository Map")
    lines.append("")
    lines.append(
        "Directory location does NOT imply GitHub org — trust this table."
    )
    lines.append("")
    lines.append("| local dir | repo | org | branch | notes |")
    lines.append("|---|---|---|---|---|")
    for node in graph.find("checkout"):
        lines.append(_checkout_row(graph, node))
    known = {
        r[0].id
        for c in graph.find("checkout")
        for r in [graph._out(c.id, "checkout_of")]
        if r
    }
    orphans = [r for r in graph.find("repo") if r.id not in known]
    if orphans:
        lines.append("")
        lines.append("Repos with no local checkout:")
        for repo in orphans:
            lines.append(f"- {_title(repo)}{_note_suffix(repo.notes)}")
    lines.append("")


def _servers(graph: AtlasGraph, lines: List[str]) -> None:
    lines.append("## Servers & Environments")
    lines.append("")
    for kind in ("server", "service", "environment"):
        for node in graph.find(kind):
            attrs = ", ".join(
                f"{k}={v}" for k, v in sorted(node.attrs.items())
            )
            lines.append(
                f"- {_title(node)}{_note_suffix(node.notes)}"
                f"{' [' + attrs + ']' if attrs else ''}"
            )
            for src in graph._in(node.id, "deploys_to"):
                lines.append(f"  - `{src.id}` deploys here")
    lines.append("")


def _workflows(graph: AtlasGraph, lines: List[str]) -> None:
    lines.append("## Workflows & Skills")
    lines.append("")
    for kind in ("workflow", "skill"):
        for node in graph.find(kind):
            lines.append(f"- {_title(node)}{_note_suffix(node.notes)}")
    lines.append("")


def _rules(graph: AtlasGraph, lines: List[str]) -> None:
    lines.append("## Rules")
    lines.append("")
    for node in graph.find("rule"):
        lines.append(f"- **{node.name}**{_note_suffix(node.notes)}")
    lines.append("")


def _plan_stores(graph: AtlasGraph, lines: List[str]) -> None:
    lines.append("## Plan Stores")
    lines.append("")
    for node in graph.find("plan_store"):
        lines.append(f"- {_title(node)}{_note_suffix(node.notes)}")
        for src in graph._in(node.id, "plans_in"):
            lines.append(f"  - `{src.id}` plans here")
    lines.append("")


def _other(graph: AtlasGraph, lines: List[str]) -> None:
    extra = sorted(k for k in graph.by_kind if k not in NODE_KINDS)
    if not extra:
        return
    lines.append("## Other")
    lines.append("")
    for kind in extra:
        for node in graph.find(kind):
            lines.append(f"- {_title(node)}{_note_suffix(node.notes)}")
    lines.append("")


def render_atlas(graph: AtlasGraph) -> str:
    """Render the full ATLAS.md document.

    Args:
        graph: The atlas graph.

    Returns:
        Markdown text.
    """
    lines = [
        "# ATLAS",
        "",
        f"<!-- {_REGEN_HINT} -->",
        "",
        "The map of this human's job: identities, orgs, repos, servers, "
        "workflows, and rules. A zero-context agent should read this "
        "top-to-bottom once, then use "
        "`python -m athenah_ai.atlas context --cwd .` for any directory.",
        "",
    ]
    _identities(graph, lines)
    _orgs(graph, lines)
    _repo_map(graph, lines)
    _servers(graph, lines)
    _workflows(graph, lines)
    _rules(graph, lines)
    _plan_stores(graph, lines)
    _other(graph, lines)
    return "\n".join(lines).rstrip() + "\n"


def _context_lines(graph: AtlasGraph, ctx: AtlasContext) -> List[str]:
    lines = []
    checkout = ctx.checkout
    path = checkout.attrs.get("path", checkout.id.split(":", 1)[1])
    branch = checkout.attrs.get("branch")
    intro = f"You are in `{path}`"
    if branch:
        intro += f" (branch `{branch}`)"
    if ctx.main_checkout is not None and ctx.main_checkout.id != checkout.id:
        main_path = ctx.main_checkout.attrs.get(
            "path", ctx.main_checkout.id.split(":", 1)[1]
        )
        intro += f", a worktree of `{main_path}`"
    lines.append(intro + ".")
    lines.append("")

    if ctx.repo is not None:
        repo_line = f"Repository: `{ctx.repo.id.split(':', 1)[1]}`"
        if ctx.org is not None:
            repo_line += f", owned by **{ctx.org.name}** (`{ctx.org.id}`)"
        lines.append(repo_line + f".{_note_suffix(ctx.repo.notes)}")
        lines.append("")

    if ctx.worktrees:
        lines.append("Sibling worktrees of the same repo:")
        for wt in ctx.worktrees:
            lines.append(
                f"- `{wt.attrs.get('path', wt.id)}` "
                f"(branch `{wt.attrs.get('branch', '?')}`)"
            )
        lines.append("")

    if ctx.capabilities:
        lines.append("Who can act here:")
        for cap in ctx.capabilities:
            lines.append(
                f"- `{cap.src}`: `{cap.kind}` → `{cap.dst}`"
                f"{_note_suffix(cap.notes)}"
            )
        lines.append("")

    if ctx.plan_stores:
        for store in ctx.plan_stores:
            lines.append(
                f"Plans live in **{store.name}** (`{store.id}`)"
                f"{_note_suffix(store.notes)}."
            )
        lines.append("")
    if ctx.workflows:
        for wf in ctx.workflows:
            lines.append(
                f"Deploys via **{wf.name}** (`{wf.id}`)"
                f"{_note_suffix(wf.notes)}."
            )
        lines.append("")
    if ctx.servers:
        for server in ctx.servers:
            lines.append(
                f"Deploy target: **{server.name}** (`{server.id}`)"
                f"{_note_suffix(server.notes)}."
            )
        lines.append("")
    if ctx.rules:
        lines.append("Rules in force here:")
        for rule in ctx.rules:
            lines.append(f"- **{rule.name}**{_note_suffix(rule.notes)}")
        lines.append("")
    return lines


def render_context(graph: AtlasGraph, cwd: str) -> str:
    """Render the scoped bootstrap for one working directory.

    Args:
        graph: The atlas graph.
        cwd: Path to contextualize.

    Returns:
        Markdown text; explains itself when the path is unknown.
    """
    ctx = graph.context_for(cwd)
    if ctx.checkout is None:
        return (
            f"`{cwd}` is not in the atlas. Run "
            "`python -m athenah_ai.atlas scan` to index new checkouts, or "
            "teach facts about it explicitly.\n"
        )
    return "\n".join(_context_lines(graph, ctx)).rstrip() + "\n"


def render_claude_md(graph: AtlasGraph) -> str:
    """Render the generated global CLAUDE.md.

    Args:
        graph: The atlas graph.

    Returns:
        Markdown text for ~/.claude/CLAUDE.md.
    """
    lines = [
        "<!-- AUTO-GENERATED by atlas (athenah-ai). Do not hand-edit: "
        "teach facts via `python -m athenah_ai.atlas teach ...` or edit "
        "the YAML under athenah_ai/atlas/facts/, then regenerate with "
        "`python -m athenah_ai.atlas render --claude-md`. -->",
        "",
        "# Rules",
        "",
    ]
    for node in graph.find("rule"):
        lines.append(f"- **{node.name}**{_note_suffix(node.notes)}")
    lines += ["", "# Identities", ""]
    for kind in ("person", "identity"):
        for node in graph.find(kind):
            lines.append(f"- {_title(node)}{_note_suffix(node.notes)}")
            for cap in graph.capabilities_of(node.id):
                lines.append(
                    f"  - `{cap.kind}` → `{cap.dst}`"
                    f"{_note_suffix(cap.notes)}"
                )
    lines += ["", "# World Map", ""]
    _repo_map(graph, lines)
    _servers(graph, lines)
    _plan_stores(graph, lines)
    lines += [
        "# Atlas",
        "",
        "This file is rendered from a queryable knowledge graph. From any "
        "directory, get the scoped picture (repo, org, who can act, how "
        "it deploys):",
        "",
        "```bash",
        "python -m athenah_ai.atlas context --cwd .",
        "```",
        "",
        "Other queries: `show <id>`, `why <src> [dst]`, `scan`, "
        "`validate`. Teach it new facts with `teach`.",
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"
