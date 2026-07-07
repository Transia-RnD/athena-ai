"""CLI for the atlas personal knowledge graph.

Usage: python -m athenah_ai.atlas <command>

Commands:
    scan       rescan checkout roots into derived facts
    teach      add a taught node/edge, or bulk-import a YAML file
    why        explain the edges touching a node, with provenance
    context    print the scoped bootstrap for a working directory
    render     write ATLAS.md (or emit the generated CLAUDE.md)
    show       print one node and its neighbors
    validate   check all facts; exit 1 on errors
"""

import argparse
import os
import sys
from typing import Optional

import yaml

from athenah_ai.atlas.graph import AtlasGraph
from athenah_ai.atlas.render import (
    render_atlas,
    render_claude_md,
    render_context,
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
    return 0


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
            attrs=raw.get("attrs") or {},
        ))
    for raw in edges:
        raw.setdefault("provenance", "imported")
        store.teach_edge(Edge(
            kind=raw["kind"], src=raw["src"], dst=raw["dst"],
            provenance=raw["provenance"], notes=raw.get("notes", ""),
            attrs=raw.get("attrs") or {},
        ))
    print(f"imported {len(nodes)} nodes, {len(edges)} edges from {path}")
    return 0


def cmd_teach(args: argparse.Namespace) -> int:
    store = _store(args)
    if args.import_file:
        return _teach_import(store, args.import_file)
    if args.node:
        kind, node_id, name = args.node
        store.teach_node(Node(
            id=node_id, kind=kind, name=name, provenance="taught",
            notes=args.note or "", attrs=_parse_attrs(args.attr),
        ))
        print(f"taught node {node_id}")
        return 0
    kind, src, dst = args.edge
    store.teach_edge(Edge(
        kind=kind, src=src, dst=dst, provenance="taught",
        notes=args.note or "", attrs=_parse_attrs(args.attr),
    ))
    print(f"taught edge {kind} {src} -> {dst}")
    return 0


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
    cwd = args.cwd or os.getcwd()
    print(render_context(_graph(args), cwd), end="")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    from athenah_ai.config import config

    graph = _graph(args)
    if args.claude_md:
        text = render_claude_md(graph)
        if not args.out:
            print(text, end="")
            return 0
        out = os.path.expanduser(args.out)
    else:
        text = render_atlas(graph)
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
    store = _store(args)
    try:
        nodes, edges = store.load()
    except AtlasValidationError as exc:
        for error in exc.errors:
            print(f"ERROR: {error}")
        return 1
    for warning in store.warnings():
        print(f"WARNING: {warning}")
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
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("teach", help="add a taught fact")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--node", nargs=3, metavar=("KIND", "ID", "NAME"))
    group.add_argument("--edge", nargs=3, metavar=("KIND", "SRC", "DST"))
    group.add_argument("--import", dest="import_file", metavar="FILE")
    p.add_argument("--note", default=None)
    p.add_argument("--attr", action="append", metavar="K=V")
    p.set_defaults(func=cmd_teach)

    p = sub.add_parser("why", help="explain edges with provenance")
    p.add_argument("src")
    p.add_argument("dst", nargs="?", default=None)
    p.set_defaults(func=cmd_why)

    p = sub.add_parser("context", help="scoped bootstrap for a directory")
    p.add_argument("--cwd", default=None)
    p.set_defaults(func=cmd_context)

    p = sub.add_parser("render", help="write ATLAS.md / emit CLAUDE.md")
    p.add_argument("--out", default=None)
    p.add_argument("--claude-md", action="store_true")
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
