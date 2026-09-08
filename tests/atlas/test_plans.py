"""Tests for the plan-store scanner."""
import os
import tempfile
import unittest

from athenah_ai.atlas.plans import PlanScanner, parse_repos
from athenah_ai.atlas.schema import Node


def _checkout(path, remote, branch):
    return Node(id=f"checkout:{path}", kind="checkout", name=os.path.basename(path),
                provenance="derived", attrs={"path": path, "remote": remote, "branch": branch})


class TestParseRepos(unittest.TestCase):
    def test_comma_and_branch(self):
        self.assertEqual(parse_repos("xrplf/xrpld-amm @ dangell7/amm-curves, XRPLF/rippled @ develop"),
                         [("xrplf/xrpld-amm", "dangell7/amm-curves"), ("XRPLF/rippled", "develop")])

    def test_plus_and_parenthetical(self):
        self.assertEqual(parse_repos("xrplf/xrpld-loadtester (worktree) + xrplf/xrpld-lab"),
                         [("xrplf/xrpld-loadtester", ""), ("xrplf/xrpld-lab", "")])

    def test_comment_and_trailer(self):
        self.assertEqual(parse_repos(" - XRPLF/xrplf-unl-validator   # vlwatch\n - dangell7/amendment-dashboard @ main — ~/projects/xrplf/amendment-dashboard"),
                         [("XRPLF/xrplf-unl-validator", ""), ("dangell7/amendment-dashboard", "main")])
        self.assertEqual(parse_repos("xrplf/xrpld (spec phase); ~/projects/xrplf/xrpl-reserves-static"),
                         [("xrplf/xrpld", ""), ("xrplf/xrpl-reserves-static", "")])

    def test_none(self):
        self.assertEqual(parse_repos("none yet (proposal)"), [])
        self.assertEqual(parse_repos(None), [])


class TestPlanScanner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.tmp, "work", "amm"))
        os.makedirs(os.path.join(self.tmp, "_outbound", "old"))
        with open(os.path.join(self.tmp, "work", "amm", "plan.md"), "w") as f:
            f.write('---\ntitle: "AMM plan"\nstatus: "Active"\nupdated: "2026-09-08"\n'
                    'repos: "xrplf/xrpld-amm @ dangell7/amm-curves, XRPLF/rippled @ dangell7/clob, XRPLF/xrpl.js"\n---\n# AMM\n- [ ] x\n')
        with open(os.path.join(self.tmp, "work", "amm", "notes.md"), "w") as f:
            f.write("# no frontmatter\n")
        with open(os.path.join(self.tmp, "_outbound", "old", "plan.md"), "w") as f:
            f.write('---\nrepos: "xrplf/xrpld-amm"\n---\n')
        self.known = [
            _checkout("~/projects/xrplf/xrpld-amm", "https://github.com/Transia-RnD/rippled.git", "dangell7/amm-curves"),
            _checkout("~/projects/xrplf/xrpld-clob", "https://github.com/XRPLF/rippled.git", "dangell7/clob"),
            _checkout("~/projects/xrplf/xrpld", "https://github.com/XRPLF/rippled.git", "develop"),
            Node(id="repo:XRPLF/xrpl.js", kind="repo", name="xrpl.js", provenance="derived"),
        ]

    def test_nodes_and_edges(self):
        nodes, edges = PlanScanner().scan([self.tmp], self.known)
        self.assertEqual([n.kind for n in nodes], ["plan"])
        plan = nodes[0]
        self.assertTrue(plan.id.endswith("/work/amm/plan.md"))
        self.assertEqual(plan.attrs["status"], "Active")
        dsts = {(e.src, e.kind) for e in edges}
        self.assertIn(("checkout:~/projects/xrplf/xrpld-amm", "governed_by"), dsts)   # by directory
        self.assertIn(("checkout:~/projects/xrplf/xrpld-clob", "governed_by"), dsts)  # by slug + branch
        self.assertIn(("repo:XRPLF/xrpl.js", "governed_by"), dsts)                    # slug, no branch -> repo
        self.assertNotIn(("checkout:~/projects/xrplf/xrpld", "governed_by"), dsts)    # other branch untouched
        self.assertEqual(len(edges), 3)

    def test_outbound_skipped_and_boxes_counted(self):
        nodes, _ = PlanScanner().scan([self.tmp], self.known)
        self.assertFalse(any("_outbound" in n.id for n in nodes))
        self.assertEqual((nodes[0].attrs["boxes_done"], nodes[0].attrs["boxes_open"]), (0, 1))


if __name__ == "__main__":
    unittest.main()
