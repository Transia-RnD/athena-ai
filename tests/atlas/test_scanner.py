"""Tests for the atlas scanner against real temporary git repos."""

import os
import shutil
import subprocess
import tempfile
import unittest

from athenah_ai.atlas.scanner import AtlasScanner, parse_remote
from athenah_ai.atlas.schema import Node
from athenah_ai.atlas.store import FactStore


def _git(cwd, *args):
    subprocess.run(
        ["git", "-C", cwd, *args],
        check=True,
        capture_output=True,
        env={**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null",
             "GIT_CONFIG_SYSTEM": "/dev/null",
             "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"},
    )


class TestParseRemote(unittest.TestCase):
    def test_ssh_form(self):
        self.assertEqual(
            parse_remote("git@github.com:Transia-RnD/athenah-ai.git"),
            "Transia-RnD/athenah-ai",
        )

    def test_ssh_alias_form(self):
        self.assertEqual(
            parse_remote("git@github.com-athenah:Transia-RnD/athenah-ai.git"),
            "Transia-RnD/athenah-ai",
        )

    def test_https_form(self):
        self.assertEqual(
            parse_remote("https://github.com/XRPLF/rippled"),
            "XRPLF/rippled",
        )
        self.assertEqual(
            parse_remote("https://github.com/XRPLF/rippled.git"),
            "XRPLF/rippled",
        )

    def test_unparseable_returns_none(self):
        self.assertIsNone(parse_remote("not-a-remote"))


class ScannerTestCase(unittest.TestCase):
    def setUp(self):
        self.root = os.path.realpath(tempfile.mkdtemp(prefix="atlas-scan-"))

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def _make_repo(self, name, remote=None):
        path = os.path.join(self.root, name)
        os.makedirs(path)
        _git(path, "init", "-q", "-b", "main")
        with open(os.path.join(path, "README.md"), "w") as f:
            f.write(name)
        _git(path, "add", ".")
        _git(path, "commit", "-q", "-m", "init", "--no-gpg-sign")
        if remote:
            _git(path, "remote", "add", "origin", remote)
        return path

    def _scan(self):
        nodes, edges = AtlasScanner(depth=4).scan([self.root])
        return nodes, edges


class TestScan(ScannerTestCase):
    def test_repo_with_ssh_remote(self):
        path = self._make_repo(
            "athenah-ai", "git@github.com:Transia-RnD/athenah-ai.git"
        )
        nodes, edges = self._scan()
        ids = {n.id for n in nodes}
        self.assertIn("repo:Transia-RnD/athenah-ai", ids)
        self.assertIn("org:transia-rnd", ids)
        checkout = next(n for n in nodes if n.kind == "checkout")
        self.assertEqual(
            os.path.realpath(os.path.expanduser(checkout.attrs["path"])),
            path,
        )
        self.assertEqual(checkout.attrs["branch"], "main")
        kinds = {(e.kind, e.src, e.dst) for e in edges}
        self.assertIn(
            ("checkout_of", checkout.id, "repo:Transia-RnD/athenah-ai"),
            kinds,
        )
        self.assertIn(
            ("owned_by", "repo:Transia-RnD/athenah-ai", "org:transia-rnd"),
            kinds,
        )
        self.assertTrue(all(n.provenance == "derived" for n in nodes))

    def test_worktree_groups_under_main_checkout(self):
        main = self._make_repo(
            "xrpld", "git@github.com:XRPLF/rippled.git"
        )
        wt = os.path.join(self.root, "xrpld-lending")
        _git(main, "worktree", "add", "-q", wt, "-b", "lending")

        nodes, edges = self._scan()
        checkouts = {n.id: n for n in nodes if n.kind == "checkout"}
        self.assertEqual(len(checkouts), 2)
        wt_id = next(i for i in checkouts if i.endswith("xrpld-lending"))
        main_id = next(
            i for i in checkouts
            if i.endswith("xrpld") and not i.endswith("xrpld-lending")
        )
        self.assertTrue(checkouts[wt_id].attrs["is_worktree"])
        triples = {(e.kind, e.src, e.dst) for e in edges}
        self.assertIn(("worktree_of", wt_id, main_id), triples)
        self.assertIn(("checkout_of", wt_id, "repo:XRPLF/rippled"), triples)
        self.assertIn(("checkout_of", main_id, "repo:XRPLF/rippled"), triples)
        # exactly one repo node for both checkouts
        self.assertEqual(
            len([n for n in nodes if n.kind == "repo"]), 1
        )

    def test_repo_without_remote(self):
        self._make_repo("scratch")
        nodes, edges = self._scan()
        checkout = next(n for n in nodes if n.kind == "checkout")
        self.assertTrue(checkout.attrs["no_remote"])
        self.assertEqual([n for n in nodes if n.kind == "repo"], [])
        # no dangling edges
        ids = {n.id for n in nodes}
        for e in edges:
            self.assertIn(e.src, ids)
            self.assertIn(e.dst, ids)

    def test_claude_md_and_tasks_flags(self):
        path = self._make_repo("flagged", "git@github.com:X/y.git")
        open(os.path.join(path, "CLAUDE.md"), "w").close()
        os.makedirs(os.path.join(path, "tasks"))
        nodes, _ = self._scan()
        checkout = next(n for n in nodes if n.kind == "checkout")
        self.assertTrue(checkout.attrs["has_claude_md"])
        self.assertTrue(checkout.attrs["has_tasks_dir"])


class TestScannerStoreIntegration(ScannerTestCase):
    def setUp(self):
        super().setUp()
        self.facts_dir = tempfile.mkdtemp(prefix="atlas-facts-")

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.facts_dir, ignore_errors=True)

    def test_taught_note_survives_rescan(self):
        self._make_repo(
            "athenah-ai", "git@github.com:Transia-RnD/athenah-ai.git"
        )
        store = FactStore(self.facts_dir)
        scanner = AtlasScanner(depth=4)
        scanner.run(store, [self.root])

        store.teach_node(
            Node(id="repo:Transia-RnD/athenah-ai", kind="repo",
                 name="athenah-ai", provenance="taught",
                 notes="Core AI indexing library.")
        )
        scanner.run(store, [self.root])  # rescan

        nodes, _ = store.load()
        repo = next(n for n in nodes if n.kind == "repo")
        self.assertEqual(repo.notes, "Core AI indexing library.")
        self.assertEqual(repo.provenance, "taught")

    def test_deleted_checkout_disappears_after_rescan(self):
        path = self._make_repo("gone", "git@github.com:X/gone.git")
        store = FactStore(self.facts_dir)
        scanner = AtlasScanner(depth=4)
        scanner.run(store, [self.root])
        nodes, _ = store.load()
        self.assertTrue(any(n.kind == "checkout" for n in nodes))

        shutil.rmtree(path)
        scanner.run(store, [self.root])
        nodes, _ = store.load()
        self.assertEqual([n for n in nodes if n.kind == "checkout"], [])


if __name__ == "__main__":
    unittest.main()
