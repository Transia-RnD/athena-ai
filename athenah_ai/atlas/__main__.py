"""CLI for the atlas personal knowledge graph.

Usage: python -m athenah_ai.atlas <command>

Commands:
    scan       rescan checkout roots into derived facts
    teach      add a taught node/edge, or bulk-import a YAML file
               (--propose marks the fact for human review; renders skip it)
    review     list proposed facts; --accept N / --reject N
    why        explain the edges touching a node, with provenance
    context    print the scoped bootstrap for a working directory
    render     write ATLAS.md (or emit CLAUDE.md / AGENTS.md)
    sync       re-render every configured consumer (CLAUDE.md, ATLAS.md...)
    show       print one node and its neighbors
    validate   check all facts; exit 1 on errors, warn on stale facts

teach and scan auto-sync when operating on the default facts dir; a
--facts-dir/env override is treated as a sandbox and skips it
(force with --sync, suppress with --no-sync).
"""

import argparse
import datetime
import hashlib
import hmac
import json
import os
import sys
from typing import Optional

import yaml

from athenah_ai.atlas.graph import AtlasGraph
from athenah_ai.atlas.render import (
    render_agents_md,
    render_atlas,
    render_claude_md,
    render_context,
    stale_since,
)
from athenah_ai.atlas.scanner import AtlasScanner
from athenah_ai.atlas.schema import Edge, Node
from athenah_ai.atlas.store import AtlasValidationError, FactStore


def _store(args: argparse.Namespace) -> FactStore:
    from athenah_ai.config import config

    return FactStore(args.facts_dir or config.atlas.facts_dir)


def _graph(args: argparse.Namespace) -> AtlasGraph:
    return AtlasGraph.from_store(_store(args))


def _parse_attrs(pairs) -> dict:
    attrs = {}
    for pair in pairs or []:
        key, _, value = pair.partition("=")
        attrs[key] = yaml.safe_load(value) if value else True
    return attrs


def _post_target(url: str, markdown: str) -> None:
    """POST rendered atlas markdown to a remote webhook (fail-soft).

    Skips with a warning when no HMAC secret is configured, and swallows any
    transport/HTTP error so a failed push never aborts the sync or other
    targets.

    Args:
        url: Destination webhook URL.
        markdown: Rendered markdown to push.
    """
    from athenah_ai.config import config

    secret = config.atlas.sync_hmac_secret
    if not secret:
        print(
            "WARNING: ATLAS_WEBHOOK_SECRET is not set; skipping http push "
            f"to {url}",
            file=sys.stderr,
        )
        return

    digest = hashlib.sha256(markdown.encode()).hexdigest()
    generated_at = datetime.datetime.now(
        datetime.timezone.utc
    ).isoformat().replace("+00:00", "Z")
    body = {
        "markdown": markdown,
        "hash": digest,
        "generatedAt": generated_at,
        "source": "athenah-atlas",
        "userId": config.atlas.sync_user_id,
    }
    body_bytes = json.dumps(
        body, separators=(",", ":"), sort_keys=True
    ).encode()
    signature = hmac.new(
        secret.encode(), body_bytes, hashlib.sha256
    ).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Atlas-Signature": f"sha256={signature}",
    }
    try:
        import httpx

        response = httpx.post(
            url,
            content=body_bytes,
            headers=headers,
            timeout=config.http.default_timeout,
        )
        print(
            f"pushed {url} ({len(body_bytes)} bytes, "
            f"status {response.status_code})"
        )
    except Exception as err:  # fail-soft: never break sync/scan/teach
        print(f"WARNING: atlas push to {url} failed: {err}", file=sys.stderr)


def _sync_targets(args: argparse.Namespace) -> int:
    from athenah_ai.config import config

    targets = config.atlas.sync_targets_list()
    renderers = {
        "atlas": render_atlas,
        "claude-md": render_claude_md,
        "agents-md": render_agents_md,
        "http-atlas": render_atlas,
        "http-claude-md": render_claude_md,
        "http-agents-md": render_agents_md,
    }
    for fmt, _ in targets:
        if fmt not in renderers:
            print(f"ERROR: unknown sync target format '{fmt}'",
                  file=sys.stderr)
            return 1
    graph = _graph(args)
    stale_days = config.atlas.stale_after_days
    for fmt, out in targets:
        rendered = renderers[fmt](graph, stale_after_days=stale_days)
        if fmt.startswith("http-"):
            _post_target(out, rendered)
            continue
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w") as f:
            f.write(rendered)
        print(f"synced {out}")
    return 0


def _should_autosync(args: argparse.Namespace) -> bool:
    if getattr(args, "sync", None) is not None:
        return args.sync
    from athenah_ai.config import AtlasConfig, config

    default_dir = AtlasConfig.__dataclass_fields__["facts_dir"].default
    facts_dir = args.facts_dir or config.atlas.facts_dir
    return os.path.expanduser(facts_dir) == default_dir


def cmd_scan(args: argparse.Namespace) -> int:
    from athenah_ai.config import config

    roots = args.roots or config.atlas.scan_roots_list()
    scanner = AtlasScanner(depth=config.atlas.scan_depth)
    if args.dry_run:
        nodes, edges = scanner.scan(roots)
        print(f"would write {len(nodes)} nodes, {len(edges)} edges "
              f"from roots: {', '.join(roots)}")
        return 0
    nodes, edges = scanner.run(_store(args), roots)
    print(f"scanned {len(nodes)} nodes, {len(edges)} edges "
          f"from roots: {', '.join(roots)}")
    if _should_autosync(args):
        return _sync_targets(args)
    return 0


def _today() -> str:
    return datetime.date.today().isoformat()


def _stamped(attrs: dict) -> dict:
    """Return attrs with verified_at defaulted to today (explicit wins)."""
    stamped = dict(attrs or {})
    stamped.setdefault("verified_at", _today())
    return stamped


def _teach_import(store: FactStore, path: str) -> int:
    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}
    nodes = data.get("nodes") or []
    edges = data.get("edges") or []
    for raw in nodes:
        raw.setdefault("provenance", "imported")
        store.teach_node(Node(
            id=raw["id"], kind=raw["kind"], name=raw["name"],
            provenance=raw["provenance"], notes=raw.get("notes", ""),
            attrs=_stamped(raw.get("attrs")),
        ))
    for raw in edges:
        raw.setdefault("provenance", "imported")
        store.teach_edge(Edge(
            kind=raw["kind"], src=raw["src"], dst=raw["dst"],
            provenance=raw["provenance"], notes=raw.get("notes", ""),
            attrs=_stamped(raw.get("attrs")),
        ))
    print(f"imported {len(nodes)} nodes, {len(edges)} edges from {path}")
    return 0


def cmd_teach(args: argparse.Namespace) -> int:
    store = _store(args)
    provenance = "proposed" if args.propose else "taught"
    if args.import_file:
        result = _teach_import(store, args.import_file)
    elif args.node:
        kind, node_id, name = args.node
        store.teach_node(Node(
            id=node_id, kind=kind, name=name, provenance=provenance,
            notes=args.note or "", attrs=_stamped(_parse_attrs(args.attr)),
        ))
        print(f"{provenance} node {node_id}")
        result = 0
    else:
        kind, src, dst = args.edge
        store.teach_edge(Edge(
            kind=kind, src=src, dst=dst, provenance=provenance,
            notes=args.note or "", attrs=_stamped(_parse_attrs(args.attr)),
        ))
        print(f"{provenance} edge {kind} {src} -> {dst}")
        result = 0
    if result == 0 and _should_autosync(args):
        return _sync_targets(args)
    return result


def _fact_label(fact) -> str:
    if isinstance(fact, Node):
        return f"node {fact.id} ({fact.kind}) — {fact.name}"
    return f"edge {fact.kind} {fact.src} -> {fact.dst}"


def cmd_review(args: argparse.Namespace) -> int:
    store = _store(args)
    facts = store.proposed()
    if not facts:
        print("no proposed facts awaiting review")
        return 0

    index = args.accept if args.accept is not None else args.reject
    if index is None:
        for i, fact in enumerate(facts, start=1):
            notes = getattr(fact, "notes", "")
            suffix = f" — {' '.join(notes.split())}" if notes else ""
            print(f"[{i}] {_fact_label(fact)}{suffix}")
        print(
            f"\n{len(facts)} proposed fact(s). Accept with "
            "`review --accept N`, discard with `review --reject N`."
        )
        return 0

    if not 1 <= index <= len(facts):
        print(f"ERROR: index {index} out of range 1..{len(facts)}",
              file=sys.stderr)
        return 1
    fact = facts[index - 1]

    if args.accept is not None:
        attrs = {**fact.attrs, "verified_at": _today()}
        if isinstance(fact, Node):
            store.teach_node(Node(
                id=fact.id, kind=fact.kind, name=fact.name,
                provenance="taught", notes=fact.notes, attrs=attrs,
            ))
        else:
            store.teach_edge(Edge(
                kind=fact.kind, src=fact.src, dst=fact.dst,
                provenance="taught", notes=fact.notes, attrs=attrs,
            ))
        print(f"accepted {_fact_label(fact)}")
    else:
        store.remove(fact)
        print(f"rejected {_fact_label(fact)}")

    if _should_autosync(args):
        return _sync_targets(args)
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    return _sync_targets(args)


def cmd_why(args: argparse.Namespace) -> int:
    graph = _graph(args)
    rows = graph.why(args.src, args.dst)
    if not rows:
        print(f"no edges touch {args.src}"
              + (f" and {args.dst}" if args.dst else ""))
        return 0
    for edge, provenance, source in rows:
        origin = f" [{provenance}" + (f", {source}]" if source else "]")
        print(f"{edge.kind}: {edge.src} -> {edge.dst}{origin}"
              + (f" — {edge.notes}" if edge.notes else ""))
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    from athenah_ai.config import config

    cwd = args.cwd or os.getcwd()
    print(
        render_context(
            _graph(args), cwd,
            stale_after_days=config.atlas.stale_after_days,
        ),
        end="",
    )
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    from athenah_ai.config import config

    graph = _graph(args)
    stale_days = config.atlas.stale_after_days
    if args.claude_md or args.agents_md:
        renderer = render_claude_md if args.claude_md else render_agents_md
        text = renderer(graph, stale_after_days=stale_days)
        if not args.out:
            print(text, end="")
            return 0
        out = os.path.expanduser(args.out)
    else:
        text = render_atlas(graph, stale_after_days=stale_days)
        out = os.path.expanduser(args.out or config.atlas.render_out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(text)
    print(f"wrote {out}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    graph = _graph(args)
    node = graph.node(args.id)
    if node is None:
        print(f"unknown node: {args.id}")
        return 1
    print(f"{node.id}  ({node.kind}, {node.provenance})")
    print(f"name: {node.name}")
    if node.notes:
        print(f"notes: {node.notes}")
    for key, value in sorted(node.attrs.items()):
        print(f"  {key}: {value}")
    for kind, others in sorted(graph.neighbors(node.id).items()):
        for direction, other in others:
            arrow = "->" if direction == "out" else "<-"
            print(f"{kind} {arrow} {other}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    from athenah_ai.config import config

    store = _store(args)
    try:
        nodes, edges = store.load()
    except AtlasValidationError as exc:
        for error in exc.errors:
            print(f"ERROR: {error}")
        return 1
    for warning in store.warnings():
        print(f"WARNING: {warning}")
    cutoff = datetime.date.today() - datetime.timedelta(
        days=config.atlas.stale_after_days
    )
    for node in nodes:
        since = stale_since(node, cutoff)
        if since:
            print(f"WARNING: {node.id} unverified since {since}")
    proposed = store.proposed()
    if proposed:
        print(
            f"WARNING: {len(proposed)} proposed fact(s) awaiting "
            "`review`"
        )
    print(f"OK: {len(nodes)} nodes, {len(edges)} edges")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the atlas argument parser.

    Returns:
        Configured ArgumentParser with subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="python -m athenah_ai.atlas",
        description="Personal job/life knowledge graph.",
    )
    parser.add_argument("--facts-dir", default=None,
                        help="facts directory override")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("scan", help="rescan roots into derived facts")
    p.add_argument("--roots", nargs="*", default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--sync", action=argparse.BooleanOptionalAction,
                   default=None, help="force/suppress re-render of targets")
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("teach", help="add a taught fact")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--node", nargs=3, metavar=("KIND", "ID", "NAME"))
    group.add_argument("--edge", nargs=3, metavar=("KIND", "SRC", "DST"))
    group.add_argument("--import", dest="import_file", metavar="FILE")
    p.add_argument("--note", default=None)
    p.add_argument("--attr", action="append", metavar="K=V")
    p.add_argument("--propose", action="store_true",
                   help="mark for human review; renders skip it until "
                        "accepted (agents suggesting facts use this)")
    p.add_argument("--sync", action=argparse.BooleanOptionalAction,
                   default=None, help="force/suppress re-render of targets")
    p.set_defaults(func=cmd_teach)

    p = sub.add_parser("review", help="list/accept/reject proposed facts")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--accept", type=int, metavar="N",
                       help="promote proposed fact N to taught")
    group.add_argument("--reject", type=int, metavar="N",
                       help="delete proposed fact N")
    p.add_argument("--sync", action=argparse.BooleanOptionalAction,
                   default=None, help="force/suppress re-render of targets")
    p.set_defaults(func=cmd_review)

    p = sub.add_parser(
        "sync", help="re-render every configured consumer output"
    )
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("why", help="explain edges with provenance")
    p.add_argument("src")
    p.add_argument("dst", nargs="?", default=None)
    p.set_defaults(func=cmd_why)

    p = sub.add_parser("context", help="scoped bootstrap for a directory")
    p.add_argument("--cwd", default=None)
    p.set_defaults(func=cmd_context)

    p = sub.add_parser(
        "render", help="write ATLAS.md / emit CLAUDE.md or AGENTS.md"
    )
    p.add_argument("--out", default=None)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--claude-md", action="store_true")
    group.add_argument("--agents-md", action="store_true")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("show", help="print one node and its neighbors")
    p.add_argument("id")
    p.set_defaults(func=cmd_show)

    p = sub.add_parser("validate", help="check facts; exit 1 on errors")
    p.set_defaults(func=cmd_validate)
    return parser


def main(argv: Optional[list] = None) -> int:
    """Run the atlas CLI.

    Args:
        argv: Argument list override (defaults to sys.argv[1:]).

    Returns:
        Process exit code.
    """
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except AtlasValidationError as exc:
        for error in exc.errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
