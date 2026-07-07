"""Scanner: derive checkout/repo/org facts from local git checkouts.

Walks the configured roots, records every git checkout (including
worktrees, which are grouped under their main checkout), and rewrites the
machine-owned ``derived/`` fact files. Taught facts are never touched, so
hand-taught knowledge always survives a rescan.
"""

import datetime
import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple

from athenah_ai.atlas.graph import to_tilde
from athenah_ai.atlas.schema import Edge, Node, make_id
from athenah_ai.atlas.store import FactStore

_SKIP_DIRS = {
    "node_modules", ".venv", "venv", "target", "build", "dist", ".next",
    "__pycache__",
}

_REMOTE_PATTERNS = (
    # git@github.com:Owner/name.git (host aliases like github.com-x allowed)
    re.compile(r"^[\w.-]+@[\w.-]+:(?P<slug>[\w.-]+/[\w.-]+?)(\.git)?/?$"),
    # https://github.com/Owner/name(.git) or ssh://git@host/Owner/name
    re.compile(
        r"^(https?|ssh)://([\w.-]+@)?[\w.-]+/(?P<slug>[\w.-]+/[\w.-]+?)"
        r"(\.git)?/?$"
    ),
)


def parse_remote(url: str) -> Optional[str]:
    """Extract ``Owner/name`` from a git remote URL.

    Args:
        url: Remote URL in ssh or https form.

    Returns:
        The ``Owner/name`` slug, or None when unparseable.
    """
    url = (url or "").strip()
    for pattern in _REMOTE_PATTERNS:
        match = pattern.match(url)
        if match:
            return match.group("slug")
    return None


class AtlasScanner:
    """Discovers git checkouts and emits derived atlas facts."""

    def __init__(self, depth: int = 4, timeout: int = 5):
        """Initialize the scanner.

        Args:
            depth: Max directory depth below each root.
            timeout: Per-git-command timeout in seconds.
        """
        self.depth = depth
        self.timeout = timeout

    def _git(self, path: str, *args: str) -> Optional[str]:
        try:
            proc = subprocess.run(
                ["git", "-C", path, *args],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        if proc.returncode != 0:
            return None
        return proc.stdout.strip()

    def _find_checkouts(self, root: str) -> List[str]:
        root = os.path.realpath(os.path.expanduser(root))
        if not os.path.isdir(root):
            return []
        found = []
        base_depth = root.count(os.sep)
        for dirpath, dirnames, filenames in os.walk(root, topdown=True):
            if os.path.exists(os.path.join(dirpath, ".git")):
                found.append(dirpath)
                dirnames[:] = []
                continue
            if dirpath.count(os.sep) - base_depth >= self.depth:
                dirnames[:] = []
                continue
            dirnames[:] = [
                d for d in dirnames
                if not d.startswith(".") and d not in _SKIP_DIRS
            ]
        return sorted(found)

    def _inspect(self, path: str) -> Optional[dict]:
        git_dir = self._git(path, "rev-parse", "--git-dir")
        common_dir = self._git(path, "rev-parse", "--git-common-dir")
        if git_dir is None or common_dir is None:
            return None
        git_dir = os.path.realpath(os.path.join(path, git_dir))
        common_dir = os.path.realpath(os.path.join(path, common_dir))
        if "/modules/" in git_dir:
            # submodule checkout: record as a plain checkout, never a worktree
            common_dir = git_dir

        info = {
            "path": path,
            "is_worktree": git_dir != common_dir,
            "main_path": os.path.dirname(common_dir),
            "branch": self._git(path, "rev-parse", "--abbrev-ref", "HEAD"),
            "remote": self._git(
                path, "config", "--get", "remote.origin.url"
            ),
            "has_claude_md": os.path.isfile(os.path.join(path, "CLAUDE.md")),
            "has_tasks_dir": os.path.isdir(os.path.join(path, "tasks")),
        }
        return info

    def scan(self, roots: List[str]) -> Tuple[List[Node], List[Edge]]:
        """Scan roots and build derived facts.

        Args:
            roots: Directories to walk for git checkouts.

        Returns:
            Tuple (nodes, edges) — checkout/repo/org nodes with
            checkout_of / worktree_of / owned_by edges, all derived.
        """
        infos = []
        for root in roots:
            for path in self._find_checkouts(root):
                info = self._inspect(path)
                if info is not None:
                    infos.append(info)

        today = datetime.date.today().isoformat()
        nodes: Dict[str, Node] = {}
        edges: Dict[Tuple[str, str, str], Edge] = {}
        checkout_id_by_path: Dict[str, str] = {}

        for info in infos:
            tilde = to_tilde(info["path"])
            checkout_id_by_path[info["path"]] = f"checkout:{tilde}"

        for info in infos:
            cid = checkout_id_by_path[info["path"]]
            attrs = {
                "path": to_tilde(info["path"]),
                "last_seen": today,
            }
            branch = info["branch"]
            if branch == "HEAD":
                attrs["detached"] = True
            elif branch:
                attrs["branch"] = branch
            if info["has_claude_md"]:
                attrs["has_claude_md"] = True
            if info["has_tasks_dir"]:
                attrs["has_tasks_dir"] = True
            if info["is_worktree"]:
                attrs["is_worktree"] = True
            if info["remote"]:
                attrs["remote"] = info["remote"]
            else:
                attrs["no_remote"] = True
            nodes[cid] = Node(
                id=cid,
                kind="checkout",
                name=os.path.basename(info["path"]),
                provenance="derived",
                attrs=attrs,
            )

            slug = parse_remote(info["remote"] or "")
            if slug:
                repo_id = make_id("repo", slug)
                org_id = make_id("org", slug.split("/", 1)[0])
                if repo_id not in nodes:
                    nodes[repo_id] = Node(
                        id=repo_id,
                        kind="repo",
                        name=slug.split("/", 1)[1],
                        provenance="derived",
                    )
                if org_id not in nodes:
                    nodes[org_id] = Node(
                        id=org_id,
                        kind="org",
                        name=slug.split("/", 1)[0],
                        provenance="derived",
                    )
                for edge in (
                    Edge(kind="checkout_of", src=cid, dst=repo_id,
                         provenance="derived"),
                    Edge(kind="owned_by", src=repo_id, dst=org_id,
                         provenance="derived"),
                ):
                    edges[edge.key()] = edge

            if info["is_worktree"]:
                main_id = checkout_id_by_path.get(info["main_path"])
                if main_id:
                    edge = Edge(kind="worktree_of", src=cid, dst=main_id,
                                provenance="derived")
                    edges[edge.key()] = edge

        return (
            sorted(nodes.values(), key=lambda n: n.id),
            sorted(edges.values(), key=lambda e: e.key()),
        )

    def run(
        self, store: FactStore, roots: Optional[List[str]] = None
    ) -> Tuple[List[Node], List[Edge]]:
        """Scan and persist derived facts into a store.

        Args:
            store: Target fact store.
            roots: Roots override; defaults to config.atlas scan roots.

        Returns:
            The (nodes, edges) that were written.
        """
        if roots is None:
            from athenah_ai.config import config

            roots = config.atlas.scan_roots_list()
        nodes, edges = self.scan(roots)
        checkout_nodes = [n for n in nodes if n.kind == "checkout"]
        checkout_edges = [
            e for e in edges if e.kind in ("checkout_of", "worktree_of")
        ]
        other_nodes = [n for n in nodes if n.kind != "checkout"]
        other_edges = [e for e in edges if e.kind == "owned_by"]
        store.write_derived("checkouts", checkout_nodes, checkout_edges)
        store.write_derived("repos", other_nodes, other_edges)
        return nodes, edges
