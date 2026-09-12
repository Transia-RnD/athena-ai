"""Tests for atlas markdown rendering."""

import datetime
import os
import unittest

from athenah_ai.atlas.graph import AtlasGraph
from athenah_ai.atlas.render import (
    CORE_MARKER,
    MAP_MARKER,
    render_agents_md,
    render_atlas,
    render_claude_md,
    render_context,
    render_rule_skills,
)
from athenah_ai.atlas.schema import Node
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

    def test_rule_evidence_rendered(self):
        self.assertIn("- evidence: Denis (2026-01-01)", self.text)

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

    def test_no_repo_table(self):
        self.assertNotIn("| local dir |", self.text)
        self.assertNotIn("~/projects/xrplf/xrpld-lending", self.text)
        self.assertIn("# World Map", self.text)

    def test_rule_evidence_hidden(self):
        self.assertNotIn("evidence:", self.text)
        self.assertNotIn("Denis (2026-01-01)", self.text)

    def test_server_notes_hidden_attrs_kept(self):
        self.assertIn("79.110.60.203", self.text)
        for node in self.graph.find("server"):
            if node.notes:
                self.assertNotIn(node.notes, self.text)


class TestConditionalRules(RenderTestCase):
    def test_atlas_splits_core_and_conditional(self):
        text = render_atlas(self.graph)
        self.assertIn("## Conditional Rules", text)
        self.assertIn("_when: connecting to a remote machine_", text)
        # the core rule stays in the plain Rules section
        rules_section = text.split("## Rules")[1].split(
            "## Conditional Rules"
        )[0]
        self.assertIn("Never push", rules_section)
        self.assertNotIn("SSH access", rules_section)

    def test_claude_md_points_to_rule_skills(self):
        text = render_claude_md(self.graph)
        self.assertNotIn("# Conditional Rules", text)
        self.assertNotIn("connecting to a remote machine", text)
        self.assertIn("skills named `rule-*`", text)
        # the core rule is still rendered in full
        self.assertIn("Never git push unless explicitly asked.", text)

    def test_context_marks_conditional_rules(self):
        text = render_context(
            self.graph, f"{HOME}/projects/xrplf/xrpld-lending"
        )
        self.assertIn("_when: connecting to a remote machine_", text)


class TestRuleSkills(RenderTestCase):
    def setUp(self):
        self.skills = render_rule_skills(self.graph)

    def test_one_skill_per_conditional_rule(self):
        self.assertEqual(sorted(self.skills), ["rule-ssh-access"])

    def test_description_carries_trigger(self):
        text = self.skills["rule-ssh-access"]
        self.assertIn("name: rule-ssh-access", text)
        self.assertIn(
            "description: SSH access. Applies when connecting to a remote "
            "machine.",
            text,
        )
        self.assertIn("user-invocable: false", text)

    def test_body_is_the_rule_text(self):
        text = self.skills["rule-ssh-access"]
        self.assertIn("# SSH access", text)
        self.assertIn("Load the key into ssh-agent before connecting.", text)
        self.assertIn("AUTO-GENERATED by atlas", text)


class TestProposedExcluded(RenderTestCase):
    def test_all_renders_skip_proposed_facts(self):
        for text in (
            render_atlas(self.graph),
            render_claude_md(self.graph),
            render_agents_md(self.graph),
        ):
            self.assertNotIn("Proposed/thing", text)


class TestStaleness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        nodes = list(NODES) + [
            Node(id="server:oldbox", kind="server", name="oldbox",
                 provenance="taught", notes="ancient box",
                 attrs={"verified_at": "2025-01-01"}),
            Node(id="server:freshbox", kind="server", name="freshbox",
                 provenance="taught",
                 attrs={"verified_at": "2026-07-01"}),
        ]
        cls.graph = AtlasGraph.from_facts(nodes, EDGES)
        cls.today = datetime.date(2026, 7, 13)

    def test_stale_fact_marked(self):
        text = render_atlas(self.graph, stale_after_days=90, today=self.today)
        self.assertIn("_(unverified since 2025-01-01)_", text)

    def test_fresh_and_unstamped_facts_not_marked(self):
        text = render_atlas(self.graph, stale_after_days=90, today=self.today)
        line = next(ln for ln in text.splitlines() if "freshbox" in ln)
        self.assertNotIn("unverified", line)
        line = next(
            ln for ln in text.splitlines() if "`server:sentinel`" in ln
        )
        self.assertNotIn("unverified", line)

    def test_verified_at_hidden_from_attr_listing(self):
        text = render_atlas(self.graph, stale_after_days=90, today=self.today)
        self.assertNotIn("verified_at=", text)


class TestRenderAgentsMd(RenderTestCase):
    def setUp(self):
        self.text = render_agents_md(self.graph)

    def test_matches_claude_md_body(self):
        # identical content, only the regen hint differs
        claude = render_claude_md(self.graph)
        self.assertEqual(
            self.text.split("-->", 1)[1], claude.split("-->", 1)[1]
        )

    def test_names_its_own_regen_flag(self):
        self.assertIn("--agents-md", self.text)


class TestCoreMapMarkers(RenderTestCase):
    def test_atlas_has_markers_in_order(self):
        text = render_atlas(self.graph)
        self.assertIn(CORE_MARKER, text)
        self.assertIn(MAP_MARKER, text)
        core_at = text.index(CORE_MARKER)
        map_at = text.index(MAP_MARKER)
        self.assertLess(core_at, map_at)
        core_zone = text[core_at:map_at]
        self.assertIn("## Identities & Capabilities", core_zone)
        self.assertIn("## Rules", core_zone)
        map_zone = text[map_at:]
        self.assertIn("## Repository Map", map_zone)
        self.assertNotIn("## Rules", map_zone)


if __name__ == "__main__":
    unittest.main()
