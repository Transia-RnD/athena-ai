"""Tests for atlas FactStore: YAML round-trip, layering, teach()."""

import os
import shutil
import tempfile
import unittest

from athenah_ai.atlas.schema import Edge, Node
from athenah_ai.atlas.store import AtlasValidationError, FactStore

TAUGHT_REPOS = """\
nodes:
  - id: repo:Transia-RnD/athenah-ai
    kind: repo
    name: athenah-ai
    provenance: taught
    notes: Core AI indexing library.
    attrs:
      pinned: true
edges:
  - kind: owned_by
    src: repo:Transia-RnD/athenah-ai
    dst: org:transia-rnd
    provenance: taught
    notes: taught ownership
"""

TAUGHT_ORGS = """\
nodes:
  - id: org:transia-rnd
    kind: org
    name: Transia-RnD
    provenance: taught
"""

DERIVED_REPOS = """\
nodes:
  - id: repo:Transia-RnD/athenah-ai
    kind: repo
    name: athenah-ai (scanned)
    provenance: derived
    attrs:
      last_seen: "2026-07-06"
      pinned: false
edges:
  - kind: owned_by
    src: repo:Transia-RnD/athenah-ai
    dst: org:transia-rnd
    provenance: derived
"""


class StoreTestCase(unittest.TestCase):
    def setUp(self):
        self.facts_dir = tempfile.mkdtemp(prefix="atlas-facts-")
        os.makedirs(os.path.join(self.facts_dir, "derived"))

    def tearDown(self):
        shutil.rmtree(self.facts_dir, ignore_errors=True)

    def _write(self, rel, content):
        path = os.path.join(self.facts_dir, rel)
        with open(path, "w") as f:
            f.write(content)
        return path


class TestLoad(StoreTestCase):
    def test_round_trip_taught_facts(self):
        self._write("repos.yaml", TAUGHT_REPOS)
        self._write("orgs.yaml", TAUGHT_ORGS)
        store = FactStore(self.facts_dir)
        nodes, edges = store.load()
        by_id = {n.id: n for n in nodes}
        repo = by_id["repo:Transia-RnD/athenah-ai"]
        self.assertEqual(repo.kind, "repo")
        self.assertEqual(repo.notes, "Core AI indexing library.")
        self.assertEqual(repo.attrs["pinned"], True)
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0].kind, "owned_by")

    def test_invalid_facts_raise_with_file_name(self):
        self._write("repos.yaml", TAUGHT_REPOS)  # org node missing -> dangling
        store = FactStore(self.facts_dir)
        with self.assertRaises(AtlasValidationError) as ctx:
            store.load()
        self.assertIn("org:transia-rnd", str(ctx.exception))

    def test_source_file_is_tracked(self):
        self._write("repos.yaml", TAUGHT_REPOS)
        self._write("orgs.yaml", TAUGHT_ORGS)
        store = FactStore(self.facts_dir)
        nodes, edges = store.load()
        repo = next(n for n in nodes if n.id.startswith("repo:"))
        self.assertEqual(store.source_of(repo), "repos.yaml")
        self.assertEqual(store.source_of(edges[0]), "repos.yaml")


class TestMerge(StoreTestCase):
    def setUp(self):
        super().setUp()
        self._write("repos.yaml", TAUGHT_REPOS)
        self._write("orgs.yaml", TAUGHT_ORGS)
        self._write(os.path.join("derived", "repos.yaml"), DERIVED_REPOS)

    def test_taught_wins_name_notes_provenance(self):
        nodes, _ = FactStore(self.facts_dir).load()
        repo = next(n for n in nodes if n.id.startswith("repo:"))
        self.assertEqual(repo.name, "athenah-ai")
        self.assertEqual(repo.notes, "Core AI indexing library.")
        self.assertEqual(repo.provenance, "taught")

    def test_attrs_merge_derived_under_taught(self):
        nodes, _ = FactStore(self.facts_dir).load()
        repo = next(n for n in nodes if n.id.startswith("repo:"))
        # derived-only key flows through
        self.assertEqual(repo.attrs["last_seen"], "2026-07-06")
        # taught key overrides derived
        self.assertEqual(repo.attrs["pinned"], True)

    def test_duplicate_edge_across_layers_keeps_taught(self):
        _, edges = FactStore(self.facts_dir).load()
        owned = [e for e in edges if e.kind == "owned_by"]
        self.assertEqual(len(owned), 1)
        self.assertEqual(owned[0].provenance, "taught")
        self.assertEqual(owned[0].notes, "taught ownership")


class TestWriteDerived(StoreTestCase):
    def test_write_derived_rewrites_only_its_file(self):
        self._write("repos.yaml", TAUGHT_REPOS)
        taught_path = self._write("orgs.yaml", TAUGHT_ORGS)
        with open(taught_path, "rb") as f:
            taught_before = f.read()

        store = FactStore(self.facts_dir)
        node = Node(
            id="checkout:~/projects/transia/athenah-ai",
            kind="checkout",
            name="athenah-ai",
            provenance="derived",
            attrs={"path": "~/projects/transia/athenah-ai"},
        )
        edge = Edge(
            kind="checkout_of",
            src=node.id,
            dst="repo:Transia-RnD/athenah-ai",
            provenance="derived",
        )
        store.write_derived("checkouts", [node], [edge])
        store.write_derived("checkouts", [node], [edge])  # idempotent

        with open(taught_path, "rb") as f:
            self.assertEqual(f.read(), taught_before)
        nodes, edges = store.load()
        self.assertIn(node.id, {n.id for n in nodes})
        self.assertIn("checkout_of", {e.kind for e in edges})

    def test_write_derived_is_deterministic(self):
        store = FactStore(self.facts_dir)
        self._write("repos.yaml", TAUGHT_REPOS)
        self._write("orgs.yaml", TAUGHT_ORGS)
        n1 = Node(id="checkout:~/a", kind="checkout", name="a",
                  provenance="derived")
        n2 = Node(id="checkout:~/b", kind="checkout", name="b",
                  provenance="derived")
        store.write_derived("checkouts", [n2, n1], [])
        path = os.path.join(self.facts_dir, "derived", "checkouts.yaml")
        with open(path, "rb") as f:
            first = f.read()
        store.write_derived("checkouts", [n1, n2], [])
        with open(path, "rb") as f:
            self.assertEqual(f.read(), first)


class TestTeach(StoreTestCase):
    def setUp(self):
        super().setUp()
        self._write("repos.yaml", TAUGHT_REPOS)
        self._write("orgs.yaml", TAUGHT_ORGS)

    def test_teach_node_appends_and_reloads(self):
        store = FactStore(self.facts_dir)
        store.teach_node(
            Node(id="org:xrplf", kind="org", name="XRPLF", provenance="taught")
        )
        nodes, _ = FactStore(self.facts_dir).load()
        self.assertIn("org:xrplf", {n.id for n in nodes})

    def test_teach_edge_appends_and_reloads(self):
        store = FactStore(self.facts_dir)
        store.teach_node(
            Node(id="identity:github/dangell8", kind="identity",
                 name="dangell8", provenance="taught")
        )
        store.teach_edge(
            Edge(kind="can_write", src="identity:github/dangell8",
                 dst="org:transia-rnd", provenance="taught",
                 notes="PAT auth, GPG-verified commits")
        )
        _, edges = FactStore(self.facts_dir).load()
        caps = [e for e in edges if e.kind == "can_write"]
        self.assertEqual(len(caps), 1)
        self.assertIn("GPG", caps[0].notes)

    def test_teach_invalid_fact_refuses_without_writing(self):
        store = FactStore(self.facts_dir)
        before = sorted(os.listdir(self.facts_dir))
        with self.assertRaises(AtlasValidationError):
            store.teach_edge(
                Edge(kind="owned_by", src="repo:Transia-RnD/athenah-ai",
                     dst="org:nonexistent", provenance="taught")
            )
        self.assertEqual(sorted(os.listdir(self.facts_dir)), before)
        # reload still valid
        FactStore(self.facts_dir).load()


if __name__ == "__main__":
    unittest.main()
