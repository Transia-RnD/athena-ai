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

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "athenah_ai.atlas", *args],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env={**os.environ, "ATHENA_ATLAS_FACTS_DIR": self.facts_dir},
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


if __name__ == "__main__":
    unittest.main()
