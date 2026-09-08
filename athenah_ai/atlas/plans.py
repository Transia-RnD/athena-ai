"""Plan scanner: derive plan nodes and governed_by edges from plan-store frontmatter.

A plan store is a checkout (see ``AtlasConfig.plan_store_roots``) whose markdown
files carry YAML frontmatter with a ``repos:`` field: comma-separated
``<owner>/<repo> @ <branch>`` items. ``<owner>/<repo>`` is either a checkout
directory under the projects root (``xrplf/xrpld-amm``) or a GitHub slug
(``XRPLF/rippled``). Each such file becomes a derived ``plan`` node; each item
that resolves to a known checkout (by directory, or by remote slug plus branch)
becomes a ``governed_by`` edge from the checkout to the plan. A slug with no
matching checkout falls back to an edge from the ``repo`` node when one exists.
"""
import os
import re
from typing import Dict, Iterable, List, Optional, Tuple

import yaml

from athenah_ai.atlas.schema import Edge, Node
from athenah_ai.atlas.scanner import parse_remote

SCAN_DIRS = ("work", "content")
SKIP_DIRS = {".git", "archive", "_outbound", "node_modules"}
NONE_WORDS = ("none", "(none", "n/a")
DASHES = ("-", "—")


def _tilde(path: str) -> str:
    home = os.path.expanduser("~")
    return "~" + path[len(home):] if path.startswith(home) else path


def parse_frontmatter(text: str) -> Optional[dict]:
    """Return the YAML frontmatter dict, or None when the file has none."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def parse_repos(value) -> List[Tuple[str, str]]:
    """Split a ``repos:`` value into (ref, branch) pairs; tolerant of lists, '+', parentheticals."""
    if value is None:
        return []
    if isinstance(value, list):
        items = [str(v) for v in value]
    else:
        text = str(value)
        if text.strip().lower().startswith(NONE_WORDS):
            return []
        text = re.sub(r"\([^)]*\)", "", text)
        items = re.split(r",|;|\n|\s\+\s|(?:^|\s)-\s", text)
    out = []
    for item in items:
        item = re.split(r"\s#|\s—\s", item)[0].strip().strip("-").strip()
        if not item or item in DASHES or item.lower().startswith(NONE_WORDS):
            continue
        ref, _, branch = item.partition("@")
        ref, branch = ref.strip().strip("`"), branch.strip().strip("`")
        ref = re.sub(r"^~/projects/", "", ref).rstrip("/")
        if ref:
            out.append((ref, branch))
    return out


class PlanScanner:
    """Derives plan nodes and governed_by edges from plan-store frontmatter."""

    def _plan_files(self, root: str) -> Iterable[str]:
        root = os.path.expanduser(root)
        starts = [os.path.join(root, d) for d in SCAN_DIRS if os.path.isdir(os.path.join(root, d))]
        if not starts:
            starts = [root]
        for start in starts:
            for dirpath, dirnames, filenames in os.walk(start):
                dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
                for fn in sorted(filenames):
                    if fn.endswith(".md"):
                        yield os.path.join(dirpath, fn)

    @staticmethod
    def _index(known: List[Node]):
        by_dir: Dict[str, Node] = {}
        by_slug_branch: Dict[Tuple[str, str], List[Node]] = {}
        repo_ids = set()
        for n in known:
            if n.kind == "repo":
                repo_ids.add(n.id)
            if n.kind != "checkout":
                continue
            path = n.attrs.get("path", "")
            parts = path.rstrip("/").split("/")
            if len(parts) >= 2:
                by_dir["/".join(parts[-2:])] = n
            slug = parse_remote(n.attrs.get("remote", "") or "")
            branch = n.attrs.get("branch", "")
            if slug:
                by_slug_branch.setdefault((slug.lower(), branch), []).append(n)
        return by_dir, by_slug_branch, repo_ids

    def scan(self, roots: List[str], known: List[Node]) -> Tuple[List[Node], List[Edge]]:
        """Scan plan stores and resolve their repos: items against known checkout and repo nodes."""
        by_dir, by_slug_branch, repo_ids = self._index(known)
        nodes: Dict[str, Node] = {}
        edges: Dict[Tuple[str, str, str], Edge] = {}
        for root in roots:
            root_abs = os.path.expanduser(root)
            store = os.path.basename(root_abs.rstrip("/"))
            for path in self._plan_files(root):
                try:
                    with open(path, encoding="utf-8") as f:
                        fm = parse_frontmatter(f.read())
                except OSError:
                    continue
                if not fm or "repos" not in fm:
                    continue
                items = parse_repos(fm.get("repos"))
                if not items:
                    continue
                rel = os.path.relpath(path, root_abs)
                pid = f"plan:{store}/{rel}"
                attrs = {"path": _tilde(path), "store": store}
                for k in ("status", "updated", "title"):
                    if fm.get(k):
                        attrs[k] = str(fm[k])
                nodes[pid] = Node(id=pid, kind="plan", name=str(fm.get("title") or os.path.basename(rel)),
                                  provenance="derived", attrs=attrs)
                for ref, branch in items:
                    targets: List[str] = []
                    if ref in by_dir:
                        targets.append(by_dir[ref].id)
                    elif branch and (ref.lower(), branch) in by_slug_branch:
                        targets += [n.id for n in by_slug_branch[(ref.lower(), branch)]]
                    else:
                        rid = f"repo:{ref}"
                        match = next((r for r in repo_ids if r.lower() == rid.lower()), None)
                        if match:
                            targets.append(match)
                    for t in targets:
                        e = Edge(kind="governed_by", src=t, dst=pid, provenance="derived")
                        edges[e.key()] = e
        return (sorted(nodes.values(), key=lambda n: n.id),
                sorted(edges.values(), key=lambda e: e.key()))
