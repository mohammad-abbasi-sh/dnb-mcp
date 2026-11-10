"""Live tests — hit the real DNB SRU API. Cautious: few requests.

Run:  pytest tests/test_live.py -v
Skip: pytest -m "not live"  (or set DNB_SKIP_LIVE=1)
"""
import json
import os
import pathlib
import sys
import unittest

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dnb_mcp import server as srv

pytestmark = pytest.mark.live
SKIP = os.environ.get("DNB_SKIP_LIVE") == "1"


@pytest.mark.skipif(SKIP, reason="DNB_SKIP_LIVE=1")
class TestLive(unittest.TestCase):
    def test_search_live(self):
        out = json.loads(srv.dnb_search_books("Kafka", limit=2))
        self.assertNotIn("error", out)
        self.assertGreater(out["total_results"], 10000)
        print(f"\nLIVE search 'Kafka': {out['total_results']} total")

    def test_title_live(self):
        out = json.loads(srv.dnb_search_by_title("Briefe 1921-1922", limit=2))
        self.assertNotIn("error", out)
        self.assertGreaterEqual(out["total_results"], 1)

    def test_author_live(self):
        out = json.loads(srv.dnb_search_by_author("Kafka, Franz", limit=2))
        self.assertNotIn("error", out)
        self.assertGreater(out["total_results"], 1000)

    def test_isbn_live(self):
        out = json.loads(srv.dnb_by_isbn("9783100381682"))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 1)
        print(f"\nLIVE ISBN: {out['items'][0]['title'][:60]}")

    def test_record_live(self):
        out = json.loads(srv.dnb_get_record("1306459214"))
        self.assertNotIn("error", out)
        self.assertEqual(out["total_results"], 1)
        self.assertEqual(out["items"][0]["author"], "Kafka, Franz")

    def test_health_live(self):
        out = json.loads(srv.dnb_health())
        self.assertEqual(out["status"], "ok")
        self.assertEqual(out["http_status"], 200)
