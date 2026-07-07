"""Tests for AtlasGraph queries over an in-memory fixture world."""

import os
import unittest

from athenah_ai.atlas.graph import AtlasGraph
from athenah_ai.atlas.schema import Edge, Node


def _n(id, kind, name, **kw):
    return Node(id=id, kind=kind, name=name, provenance="taught", **kw)


def _e(kind, src, dst, **kw):
    return Edge(kind=kind, src=src, dst=dst, provenance="taught", **kw)


HOME = os.path.expanduser("~")

NODES = [
    _n("person:denis", "person", "Denis Angell"),
    _n("identity:github/dangell7", "identity", "dangell7"),
    _n("identity:github/dangell8", "identity", "dangell8"),
    _n("org:transia-rnd", "org", "Transia-RnD"),
    _n("org:xrplf", "org", "XRPLF"),
    _n("repo:XRPLF/rippled", "repo", "rippled"),
    _n("repo:Transia-RnD/xrpl-guides", "repo", "xrpl-guides"),
    _n("checkout:~/projects/xrplf/xrpld", "checkout", "xrpld",
       attrs={"path": "~/projects/xrplf/xrpld", "branch": "develop"}),
    _n("checkout:~/projects/xrplf/xrpld-lending", "checkout", "xrpld-lending",
       attrs={"path": "~/projects/xrplf/xrpld-lending", "branch": "lending"}),
    _n("plan_store:xrpl-guides", "plan_store", "xrpl-guides"),
    _n("server:sentinel", "server", "sentinel",
       attrs={"ip": "79.110.60.203"}),
    _n("workflow:deploy-alphanet", "workflow", "deploy-alphanet"),
    _n("rule:never-push", "rule", "Never push",
       notes="Never git push unless explicitly asked."),
]

EDGES = [
    _e("member_of", "person:denis", "org:transia-rnd"),
    _e("operates", "identity:github/dangell7", "org:xrplf"),
    _e("can_write", "identity:github/dangell8", "org:transia-rnd",
       notes="PAT auth, GPG-verified commits"),
    _e("can_comment", "identity:github/dangell7", "org:xrplf"),
    _e("can_write", "identity:github/dangell7", "repo:XRPLF/rippled"),
    _e("owned_by", "repo:XRPLF/rippled", "org:xrplf"),
    _e("owned_by", "repo:Transia-RnD/xrpl-guides", "org:transia-rnd"),
    _e("checkout_of", "checkout:~/projects/xrplf/xrpld",
       "repo:XRPLF/rippled"),
    _e("checkout_of", "checkout:~/projects/xrplf/xrpld-lending",
       "repo:XRPLF/rippled"),
    _e("worktree_of", "checkout:~/projects/xrplf/xrpld-lending",
       "checkout:~/projects/xrplf/xrpld"),
    _e("plans_in", "repo:XRPLF/rippled", "plan_store:xrpl-guides"),
    _e("deploys_via", "repo:XRPLF/rippled", "workflow:deploy-alphanet"),
    _e("deploys_to", "repo:XRPLF/rippled", "server:sentinel"),
]


class GraphTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = AtlasGraph.from_facts(NODES, EDGES)


class TestWhoOwns(GraphTestCase):
    def test_by_repo_id(self):
        org = self.graph.who_owns("repo:XRPLF/rippled")
        self.assertEqual(org.id, "org:xrplf")

    def test_by_owner_slash_name(self):
        org = self.graph.who_owns("Transia-RnD/xrpl-guides")
        self.assertEqual(org.id, "org:transia-rnd")

    def test_by_path(self):
        org = self.graph.who_owns(f"{HOME}/projects/xrplf/xrpld-lending")
        self.assertEqual(org.id, "org:xrplf")

    def test_unknown_returns_none(self):
        self.assertIsNone(self.graph.who_owns("repo:Nobody/nothing"))


class TestResolveCwd(GraphTestCase):
    def test_exact_path(self):
        cid = self.graph.resolve_cwd(f"{HOME}/projects/xrplf/xrpld")
        self.assertEqual(cid, "checkout:~/projects/xrplf/xrpld")

    def test_subdirectory_resolves(self):
        cid = self.graph.resolve_cwd(
            f"{HOME}/projects/xrplf/xrpld-lending/src/xrpld"
        )
        self.assertEqual(cid, "checkout:~/projects/xrplf/xrpld-lending")

    def test_unknown_path_returns_none(self):
        self.assertIsNone(self.graph.resolve_cwd("/nonexistent/elsewhere"))


class TestContextFor(GraphTestCase):
    def setUp(self):
        self.ctx = self.graph.context_for(
            f"{HOME}/projects/xrplf/xrpld-lending"
        )

    def test_checkout_repo_org(self):
        self.assertEqual(
            self.ctx.checkout.id, "checkout:~/projects/xrplf/xrpld-lending"
        )
        self.assertEqual(self.ctx.repo.id, "repo:XRPLF/rippled")
        self.assertEqual(self.ctx.org.id, "org:xrplf")

    def test_sibling_worktrees_and_main(self):
        self.assertEqual(
            self.ctx.main_checkout.id, "checkout:~/projects/xrplf/xrpld"
        )

    def test_capabilities_include_repo_and_org_level(self):
        caps = {(e.kind, e.src) for e in self.ctx.capabilities}
        # repo-level capability
        self.assertIn(("can_write", "identity:github/dangell7"), caps)
        # org-level capability inherited to repo context
        self.assertIn(("can_comment", "identity:github/dangell7"), caps)

    def test_plan_store_workflow_server(self):
        self.assertIn(
            "plan_store:xrpl-guides", [n.id for n in self.ctx.plan_stores]
        )
        self.assertIn(
            "workflow:deploy-alphanet", [n.id for n in self.ctx.workflows]
        )
        self.assertIn("server:sentinel", [n.id for n in self.ctx.servers])


class TestQueries(GraphTestCase):
    def test_capabilities_of(self):
        caps = self.graph.capabilities_of("identity:github/dangell8")
        self.assertEqual(len(caps), 1)
        self.assertEqual(caps[0].kind, "can_write")
        self.assertIn("GPG", caps[0].notes)

    def test_find_globs_and_sorts(self):
        hits = self.graph.find("checkout", "xrpld*")
        self.assertEqual(
            [n.id for n in hits],
            [
                "checkout:~/projects/xrplf/xrpld",
                "checkout:~/projects/xrplf/xrpld-lending",
            ],
        )

    def test_neighbors_grouped_by_kind(self):
        groups = self.graph.neighbors("repo:XRPLF/rippled")
        self.assertIn("owned_by", groups)
        self.assertIn("checkout_of", groups)

    def test_why_explains_edges(self):
        rows = self.graph.why(
            "identity:github/dangell8", "org:transia-rnd"
        )
        self.assertEqual(len(rows), 1)
        edge, provenance, source = rows[0]
        self.assertEqual(edge.kind, "can_write")
        self.assertEqual(provenance, "taught")

    def test_rules_listed(self):
        rules = self.graph.find("rule", "*")
        self.assertEqual(rules[0].id, "rule:never-push")


if __name__ == "__main__":
    unittest.main()
