"""Tests for the atlas http-* sync targets (webhook push)."""

import argparse
import hashlib
import hmac
import json
import os
import tempfile
import unittest
from unittest import mock

from athenah_ai.atlas import __main__ as m
from athenah_ai.atlas.graph import AtlasGraph
from athenah_ai.atlas.render import render_atlas, render_claude_md
from athenah_ai.config import config
from tests.atlas.test_graph import EDGES, NODES

URL = "http://127.0.0.1:59999/v1/plugins/atlas/webhook"


class HttpSyncTestCase(unittest.TestCase):
    def setUp(self):
        self.graph = AtlasGraph.from_facts(NODES, EDGES)
        # Snapshot mutated singleton config so tests stay isolated.
        self._saved = {
            "sync_targets": config.atlas.sync_targets,
            "sync_hmac_secret": config.atlas.sync_hmac_secret,
            "sync_user_id": config.atlas.sync_user_id,
        }
        self._graph_patch = mock.patch.object(
            m, "_graph", return_value=self.graph
        )
        self._graph_patch.start()
        self.args = argparse.Namespace(facts_dir=None)

    def tearDown(self):
        self._graph_patch.stop()
        for key, value in self._saved.items():
            setattr(config.atlas, key, value)


class TestRouting(HttpSyncTestCase):
    def test_http_atlas_routes_to_atlas_renderer(self):
        config.atlas.sync_targets = f"http-atlas:{URL}"
        config.atlas.sync_hmac_secret = "testsecret"
        with mock.patch("httpx.post") as post:
            post.return_value = mock.Mock(status_code=200)
            rc = m._sync_targets(self.args)
        self.assertEqual(rc, 0)
        post.assert_called_once()
        body = json.loads(post.call_args.kwargs["content"])
        self.assertEqual(body["markdown"], render_atlas(self.graph))

    def test_http_claude_md_routes_to_claude_renderer(self):
        config.atlas.sync_targets = f"http-claude-md:{URL}"
        config.atlas.sync_hmac_secret = "testsecret"
        with mock.patch("httpx.post") as post:
            post.return_value = mock.Mock(status_code=200)
            rc = m._sync_targets(self.args)
        self.assertEqual(rc, 0)
        post.assert_called_once()
        body = json.loads(post.call_args.kwargs["content"])
        self.assertEqual(body["markdown"], render_claude_md(self.graph))

    def test_url_scheme_preserved_by_target_parse(self):
        config.atlas.sync_targets = f"http-atlas:{URL}"
        config.atlas.sync_hmac_secret = "testsecret"
        with mock.patch("httpx.post") as post:
            post.return_value = mock.Mock(status_code=200)
            m._sync_targets(self.args)
        called_url = post.call_args.args[0]
        self.assertEqual(called_url, URL)


class TestSignature(HttpSyncTestCase):
    def test_body_hash_and_signature_verify(self):
        secret = "topsecret"
        config.atlas.sync_targets = f"http-atlas:{URL}"
        config.atlas.sync_hmac_secret = secret
        config.atlas.sync_user_id = "user-123"
        with mock.patch("httpx.post") as post:
            post.return_value = mock.Mock(status_code=200)
            m._sync_targets(self.args)

        content = post.call_args.kwargs["content"]
        headers = post.call_args.kwargs["headers"]
        body = json.loads(content)
        markdown = render_atlas(self.graph)

        # hash field matches sha256 of the markdown
        self.assertEqual(
            body["hash"], hashlib.sha256(markdown.encode()).hexdigest()
        )
        self.assertEqual(body["source"], "athenah-atlas")
        self.assertEqual(body["userId"], "user-123")

        # signature is HMAC-SHA256 over the exact bytes sent
        expected = hmac.new(
            secret.encode(), content, hashlib.sha256
        ).hexdigest()
        self.assertEqual(headers["X-Atlas-Signature"], f"sha256={expected}")
        self.assertEqual(headers["Content-Type"], "application/json")

    def test_content_is_stable_sorted_compact_json(self):
        config.atlas.sync_targets = f"http-atlas:{URL}"
        config.atlas.sync_hmac_secret = "s"
        with mock.patch("httpx.post") as post:
            post.return_value = mock.Mock(status_code=200)
            m._sync_targets(self.args)
        content = post.call_args.kwargs["content"]
        body = json.loads(content)
        expected = json.dumps(
            body, separators=(",", ":"), sort_keys=True
        ).encode()
        self.assertEqual(content, expected)


class TestFailSoft(HttpSyncTestCase):
    def test_empty_secret_skips_and_file_target_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out", "ATLAS.md")
            config.atlas.sync_targets = f"http-atlas:{URL},atlas:{out}"
            config.atlas.sync_hmac_secret = ""
            with mock.patch("httpx.post") as post:
                rc = m._sync_targets(self.args)
            # http push skipped entirely
            post.assert_not_called()
            self.assertEqual(rc, 0)
            # file target still written
            with open(out) as f:
                self.assertIn("# ATLAS", f.read())

    def test_post_error_is_swallowed_and_other_targets_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "out", "ATLAS.md")
            config.atlas.sync_targets = f"http-atlas:{URL},atlas:{out}"
            config.atlas.sync_hmac_secret = "testsecret"
            with mock.patch(
                "httpx.post", side_effect=ConnectionError("refused")
            ):
                rc = m._sync_targets(self.args)
            # fail-soft: overall sync still succeeds
            self.assertEqual(rc, 0)
            # subsequent file target still written
            with open(out) as f:
                self.assertIn("# ATLAS", f.read())


if __name__ == "__main__":
    unittest.main()
