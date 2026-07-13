"""Tests for atlas schema: kind vocabularies, Node/Edge, validate()."""

import unittest

from athenah_ai.atlas.schema import (
    EDGE_KINDS,
    NODE_KINDS,
    PROVENANCE,
    Edge,
    Node,
    make_id,
    validate,
)


def _node(id="repo:Transia-RnD/athenah-ai", kind="repo", name="athenah-ai",
          provenance="taught", **kw):
    return Node(id=id, kind=kind, name=name, provenance=provenance, **kw)


def _edge(kind="owned_by", src="repo:Transia-RnD/athenah-ai",
          dst="org:transia-rnd", provenance="taught", **kw):
    return Edge(kind=kind, src=src, dst=dst, provenance=provenance, **kw)


class TestVocabularies(unittest.TestCase):
    def test_expected_kinds_present(self):
        self.assertIn("identity", NODE_KINDS)
        self.assertIn("checkout", NODE_KINDS)
        self.assertIn("plan_store", NODE_KINDS)
        self.assertIn("owned_by", EDGE_KINDS)
        self.assertIn("worktree_of", EDGE_KINDS)
        self.assertIn("can_write", EDGE_KINDS)
        self.assertIn("applies_to", EDGE_KINDS)
        self.assertEqual(
            PROVENANCE,
            frozenset({"taught", "derived", "imported", "proposed"}),
        )


class TestMakeId(unittest.TestCase):
    def test_make_id_prefixes_kind(self):
        self.assertEqual(make_id("org", "Transia-RnD"), "org:transia-rnd")
        self.assertEqual(
            make_id("repo", "Transia-RnD/athenah-ai"),
            "repo:Transia-RnD/athenah-ai",
        )
        self.assertEqual(
            make_id("identity", "github/dangell8"), "identity:github/dangell8"
        )


class TestValidate(unittest.TestCase):
    def test_valid_minimal_graph(self):
        nodes = [_node(), _node(id="org:transia-rnd", kind="org", name="Transia")]
        errors, warnings = validate(nodes, [_edge()])
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_unknown_node_kind_is_error(self):
        errors, _ = validate([_node(kind="spaceship", id="spaceship:x")], [])
        self.assertTrue(any("spaceship" in e for e in errors))

    def test_unknown_edge_kind_is_error(self):
        nodes = [_node(), _node(id="org:transia-rnd", kind="org", name="Transia")]
        errors, _ = validate(nodes, [_edge(kind="teleports_to")])
        self.assertTrue(any("teleports_to" in e for e in errors))

    def test_x_prefixed_kind_is_warning_not_error(self):
        nodes = [
            _node(kind="x-gadget", id="x-gadget:thing", name="thing"),
            _node(),
            _node(id="org:transia-rnd", kind="org", name="Transia"),
        ]
        edges = [_edge(kind="x-zaps", src="x-gadget:thing")]
        errors, warnings = validate(nodes, edges)
        self.assertEqual(errors, [])
        self.assertTrue(any("x-gadget" in w for w in warnings))
        self.assertTrue(any("x-zaps" in w for w in warnings))

    def test_id_prefix_must_match_kind(self):
        errors, _ = validate([_node(id="repo:foo", kind="checkout")], [])
        self.assertTrue(any("repo:foo" in e for e in errors))

    def test_duplicate_id_same_layer_is_error(self):
        errors, _ = validate([_node(), _node()], [])
        self.assertTrue(any("duplicate" in e.lower() for e in errors))

    def test_dangling_edge_endpoint_is_error(self):
        errors, _ = validate([_node()], [_edge()])  # org node missing
        self.assertTrue(any("org:transia-rnd" in e for e in errors))

    def test_endpoint_rule_violation_is_error(self):
        # owned_by must be repo -> org; identity -> org violates it
        nodes = [
            _node(id="identity:github/dangell7", kind="identity", name="dangell7"),
            _node(id="org:transia-rnd", kind="org", name="Transia"),
        ]
        edges = [_edge(src="identity:github/dangell7")]
        errors, _ = validate(nodes, edges)
        self.assertTrue(any("owned_by" in e for e in errors))

    def test_capability_edge_allows_org_and_repo_targets(self):
        nodes = [
            _node(id="identity:github/dangell8", kind="identity", name="dangell8"),
            _node(id="org:transia-rnd", kind="org", name="Transia"),
            _node(),
        ]
        edges = [
            _edge(kind="can_write", src="identity:github/dangell8",
                  dst="org:transia-rnd"),
            _edge(kind="can_write", src="identity:github/dangell8",
                  dst="repo:Transia-RnD/athenah-ai"),
        ]
        errors, warnings = validate(nodes, edges)
        self.assertEqual(errors, [])

    def test_bad_provenance_is_error(self):
        errors, _ = validate([_node(provenance="guessed")], [])
        self.assertTrue(any("guessed" in e for e in errors))

    def test_proposed_provenance_is_valid(self):
        errors, _ = validate([_node(provenance="proposed")], [])
        self.assertEqual(errors, [])

    def test_applies_to_endpoint_rules(self):
        nodes = [
            _node(id="rule:ssh", kind="rule", name="SSH"),
            _node(id="server:sentinel", kind="server", name="sentinel"),
            _node(id="org:transia-rnd", kind="org", name="Transia"),
        ]
        ok = [_edge(kind="applies_to", src="rule:ssh", dst="server:sentinel")]
        errors, _ = validate(nodes, ok)
        self.assertEqual(errors, [])
        # org -> server is not a legal applies_to source
        bad = [_edge(kind="applies_to", src="org:transia-rnd",
                     dst="server:sentinel")]
        errors, _ = validate(nodes, bad)
        self.assertTrue(any("applies_to" in e for e in errors))

    def test_empty_name_is_error(self):
        errors, _ = validate([_node(name="")], [])
        self.assertTrue(any("name" in e.lower() for e in errors))


if __name__ == "__main__":
    unittest.main()
