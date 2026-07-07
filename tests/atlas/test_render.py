"""Tests for atlas markdown rendering."""

import os
import unittest

from athenah_ai.atlas.graph import AtlasGraph
from athenah_ai.atlas.render import (
    render_atlas,
    render_claude_md,
    render_context,
)
from tests.atlas.test_graph import EDGES, NODES

HOME = os.path.expanduser("~")


class RenderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = AtlasGraph.from_facts(NODES, EDGES)


class TestRenderAtlas(RenderTestCase):
    def setUp(self):
        self.text = render_atlas(self.graph)

    def test_sections_present(self):
        for header in (
            "# ATLAS",
            "## Identities & Capabilities",
            "## Organizations",
            "## Repository Map",
            "## Servers & Environments",
            "## Workflows & Skills",
            "## Rules",
            "## Plan Stores",
        ):
            self.assertIn(header, self.text)

    def test_repo_table_rows(self):
        self.assertIn("~/projects/xrplf/xrpld", self.text)
        self.assertIn("XRPLF/rippled", self.text)

    def test_worktree_marked(self):
        # the lending checkout is a worktree of xrpld and must say so
        line = next(
            ln for ln in self.text.splitlines() if "xrpld-lending" in ln
        )
        self.assertIn("worktree", line)

    def test_capability_notes_rendered(self):
        self.assertIn("PAT auth, GPG-verified commits", self.text)

    def test_rule_text_rendered(self):
        self.assertIn("Never git push unless explicitly asked.", self.text)

    def test_deterministic(self):
        self.assertEqual(self.text, render_atlas(self.graph))


class TestRenderContext(RenderTestCase):
    def setUp(self):
        self.text = render_context(
            self.graph, f"{HOME}/projects/xrplf/xrpld-lending"
        )

    def test_mentions_checkout_repo_org(self):
        self.assertIn("xrpld-lending", self.text)
        self.assertIn("XRPLF/rippled", self.text)
        self.assertIn("XRPLF", self.text)

    def test_mentions_worktree_main(self):
        self.assertIn("~/projects/xrplf/xrpld", self.text)

    def test_mentions_capability(self):
        self.assertIn("dangell7", self.text)
        self.assertIn("can_write", self.text)

    def test_unknown_path_says_so(self):
        text = render_context(self.graph, "/nowhere/special")
        self.assertIn("not in the atlas", text)


class TestRenderClaudeMd(RenderTestCase):
    def setUp(self):
        self.text = render_claude_md(self.graph)

    def test_generated_header(self):
        self.assertIn("auto-generated", self.text.lower())
        self.assertIn("python -m athenah_ai.atlas", self.text)

    def test_rules_verbatim(self):
        self.assertIn("Never git push unless explicitly asked.", self.text)

    def test_identity_summary(self):
        self.assertIn("dangell8", self.text)
        self.assertIn("can_write", self.text)

    def test_scoped_context_instructions(self):
        self.assertIn("context --cwd", self.text)


if __name__ == "__main__":
    unittest.main()
