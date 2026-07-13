"""End-to-end CLI tests: python -m athenah_ai.atlas against a tmp facts dir."""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

TAUGHT = """\
nodes:
  - id: org:transia-rnd
    kind: org
    name: Transia-RnD
    provenance: taught
  - id: repo:Transia-RnD/athenah-ai
    kind: repo
    name: athenah-ai
    provenance: taught
edges:
  - kind: owned_by
    src: repo:Transia-RnD/athenah-ai
    dst: org:transia-rnd
    provenance: taught
"""

BROKEN = """\
nodes:
  - id: repo:Broken/thing
    kind: repo
    name: thing
    provenance: taught
edges:
  - kind: owned_by
    src: repo:Broken/thing
    dst: org:missing
    provenance: taught
"""


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.facts_dir = tempfile.mkdtemp(prefix="atlas-cli-")
        with open(os.path.join(self.facts_dir, "repos.yaml"), "w") as f:
            f.write(TAUGHT)

    def tearDown(self):
        shutil.rmtree(self.facts_dir, ignore_errors=True)

    def _run(self, *args, env=None):
        return subprocess.run(
            [sys.executable, "-m", "athenah_ai.atlas", *args],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, "ATHENA_ATLAS_FACTS_DIR": self.facts_dir,
                 **(env or {})},
            timeout=60,
        )


class TestValidate(CliTestCase):
    def test_valid_facts_exit_zero(self):
        proc = self._run("validate")
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_broken_facts_exit_one(self):
        with open(os.path.join(self.facts_dir, "broken.yaml"), "w") as f:
            f.write(BROKEN)
        proc = self._run("validate")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("org:missing", proc.stdout + proc.stderr)


class TestTeachShowWhy(CliTestCase):
    def test_teach_edge_then_why(self):
        proc = self._run(
            "teach", "--node", "identity", "identity:github/dangell8",
            "dangell8",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        proc = self._run(
            "teach", "--edge", "can_write", "identity:github/dangell8",
            "org:transia-rnd", "--note", "PAT auth, GPG-verified commits",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        proc = self._run("why", "identity:github/dangell8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("can_write", proc.stdout)
        self.assertIn("GPG", proc.stdout)

    def test_show_node(self):
        proc = self._run("show", "repo:Transia-RnD/athenah-ai")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("owned_by", proc.stdout)

    def test_teach_invalid_edge_fails(self):
        proc = self._run(
            "teach", "--edge", "owned_by", "repo:Transia-RnD/athenah-ai",
            "org:nope",
        )
        self.assertEqual(proc.returncode, 1)


class TestSync(CliTestCase):
    def _targets_env(self):
        atlas_out = os.path.join(self.facts_dir, "out", "ATLAS.md")
        claude_out = os.path.join(self.facts_dir, "out", "CLAUDE.md")
        env = {
            "ATHENA_ATLAS_SYNC_TARGETS":
                f"atlas:{atlas_out},claude-md:{claude_out}",
        }
        return env, atlas_out, claude_out

    def test_sync_writes_all_targets(self):
        env, atlas_out, claude_out = self._targets_env()
        proc = self._run("sync", env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(atlas_out) as f:
            self.assertIn("# ATLAS", f.read())
        with open(claude_out) as f:
            self.assertIn("AUTO-GENERATED", f.read())

    def test_sync_unknown_format_fails(self):
        bogus = os.path.join(self.facts_dir, "out", "X.md")
        proc = self._run(
            "sync", env={"ATHENA_ATLAS_SYNC_TARGETS": f"bogus:{bogus}"}
        )
        self.assertEqual(proc.returncode, 1)
        self.assertFalse(os.path.exists(bogus))

    def test_teach_on_custom_facts_dir_does_not_autosync(self):
        # facts dir is overridden (a sandbox) -> teach must NOT touch targets
        env, atlas_out, claude_out = self._targets_env()
        proc = self._run(
            "teach", "--node", "org", "org:xrplf", "XRPLF", env=env
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(os.path.exists(atlas_out))
        self.assertFalse(os.path.exists(claude_out))

    def test_teach_sync_flag_forces_sync(self):
        env, atlas_out, claude_out = self._targets_env()
        proc = self._run(
            "teach", "--node", "org", "org:xrplf", "XRPLF", "--sync",
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(atlas_out) as f:
            self.assertIn("XRPLF", f.read())
        self.assertTrue(os.path.exists(claude_out))


class TestRenderAndContext(CliTestCase):
    def test_render_writes_out(self):
        out = os.path.join(self.facts_dir, "ATLAS.md")
        proc = self._run("render", "--out", out)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(out) as f:
            self.assertIn("# ATLAS", f.read())

    def test_context_unknown_cwd(self):
        proc = self._run("context", "--cwd", "/nowhere")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("not in the atlas", proc.stdout)

    def test_render_agents_md_to_stdout(self):
        proc = self._run("render", "--agents-md")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("AUTO-GENERATED", proc.stdout)
        self.assertIn("--agents-md", proc.stdout)

    def test_sync_agents_md_target(self):
        agents_out = os.path.join(self.facts_dir, "out", "AGENTS.md")
        proc = self._run(
            "sync",
            env={"ATHENA_ATLAS_SYNC_TARGETS": f"agents-md:{agents_out}"},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        with open(agents_out) as f:
            self.assertIn("--agents-md", f.read())


class TestProposeAndReview(CliTestCase):
    def _propose_box(self):
        proc = self._run(
            "teach", "--propose", "--node", "server", "server:box1", "box1",
            "--note", "agent-discovered box",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("proposed node server:box1", proc.stdout)

    def test_proposed_fact_hidden_until_accepted(self):
        self._propose_box()
        proc = self._run("render", "--claude-md")
        self.assertNotIn("box1", proc.stdout)

        proc = self._run("review")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("[1] node server:box1", proc.stdout)

        proc = self._run("review", "--accept", "1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("accepted", proc.stdout)

        proc = self._run("render", "--claude-md")
        self.assertIn("box1", proc.stdout)
        # accept stamped freshness
        proc = self._run("show", "server:box1")
        self.assertIn("verified_at", proc.stdout)

    def test_reject_deletes_the_proposal(self):
        self._propose_box()
        proc = self._run("review", "--reject", "1")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("rejected", proc.stdout)
        proc = self._run("review")
        self.assertIn("no proposed facts", proc.stdout)
        proc = self._run("show", "server:box1")
        self.assertEqual(proc.returncode, 1)

    def test_review_index_out_of_range(self):
        self._propose_box()
        proc = self._run("review", "--accept", "9")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("out of range", proc.stderr)

    def test_propose_cannot_downgrade_taught_fact(self):
        proc = self._run(
            "teach", "--propose", "--node", "org", "org:transia-rnd",
            "Transia-RnD",
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("refusing to downgrade", proc.stderr)

    def test_validate_warns_about_proposed(self):
        self._propose_box()
        proc = self._run("validate")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("proposed fact(s) awaiting", proc.stdout)


class TestTeachStampsFreshness(CliTestCase):
    def test_teach_stamps_verified_at(self):
        proc = self._run(
            "teach", "--node", "server", "server:box2", "box2",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        proc = self._run("show", "server:box2")
        self.assertIn("verified_at", proc.stdout)

    def test_explicit_verified_at_wins(self):
        proc = self._run(
            "teach", "--node", "server", "server:box3", "box3",
            "--attr", "verified_at=2020-01-01",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        proc = self._run("show", "server:box3")
        self.assertIn("2020-01-01", proc.stdout)


if __name__ == "__main__":
    unittest.main()
