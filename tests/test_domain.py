"""Offline tests — parse real captured DNB SRU responses, no network."""
import json
import pathlib
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))

from dnb_mcp import domain as dom
from dnb_mcp import server as srv

FIX = pathlib.Path(__file__).resolve().parent / "fixtures"


def _read(name):
    return (FIX / name).read_text(encoding="utf-8")


class TestValidation(unittest.TestCase):
    def test_isbn(self):
        self.assertEqual(dom.validate_isbn("9783100381682"), "9783100381682")
        self.assertEqual(dom.validate_isbn("978-3-10-038168-2"), "978-3-10-038168-2")
        for bad in ["", "123", "abcdefghij", "97831003816822"]:
            with self.assertRaises(ValueError, msg=bad):
                dom.validate_isbn(bad)

    def test_dnb_id(self):
        self.assertEqual(dom.validate_dnb_id("1306459214"), "1306459214")
        for bad in ["", "abc", "12a34"]:
            with self.assertRaises(ValueError, msg=bad):
                dom.validate_dnb_id(bad)

    def test_limit(self):
        self.assertEqual(dom.validate_limit(10), 10)
        with self.assertRaises(ValueError):
            dom.validate_limit(0)
        with self.assertRaises(ValueError):
            dom.validate_limit(51)


class TestFixtures(unittest.TestCase):
    def test_search_tit(self):
        out = dom.parse_search(_read("search-tit-kafka.xml"))
        self.assertEqual(out["total_results"], 6044)
        self.assertEqual(len(out["items"]), 2)
        first = out["items"][0]
        self.assertEqual(first["dnb_id"], "1306459214")
        self.assertEqual(first["title"], "Briefe 1921-1922 : Band 5 (Kommentierte Ausgabe)")
        self.assertEqual(first["author"], "Kafka, Franz")
        self.assertEqual(first["isbn"], "9783100381682")
        self.assertEqual(first["year"], "2027")
        self.assertEqual(first["publisher"], "S. FISCHER")
        self.assertEqual(first["language"], "ger")
        self.assertIn("Briefe", first["subjects"])

    def test_search_per(self):
        out = dom.parse_search(_read("search-per-kafka.xml"))
        self.assertEqual(out["total_results"], 7159)
        self.assertEqual(len(out["items"]), 2)

    def test_search_woe(self):
        out = dom.parse_search(_read("search-woe-kafka.xml"))
        self.assertEqual(out["total_results"], 13292)
        self.assertEqual(len(out["items"]), 1)

    def test_by_isbn(self):
        out = dom.parse_search(_read("by-isbn.xml"))
        self.assertEqual(out["total_results"], 1)
        self.assertEqual(out["items"][0]["dnb_id"], "1306459214")

    def test_get_record(self):
        out = dom.parse_search(_read("get-record.xml"))
        self.assertEqual(out["total_results"], 1)
        self.assertEqual(out["items"][0]["title"],
                         "Briefe 1921-1922 : Band 5 (Kommentierte Ausgabe)")

    def test_diagnostic_raises(self):
        bad = ('<searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/">'
               '<diagnostics xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/">'
               '<diag:diagnostic><diag:details>Unsupported index</diag:details>'
               '<diag:message>isb</diag:message></diag:diagnostic></diagnostics>'
               '</searchRetrieveResponse>')
        with self.assertRaises(ValueError):
            dom.parse_search(bad)

    def test_bad_xml(self):
        with self.assertRaises(ValueError):
            dom.parse_search("<searchRetrieveResponse><unclosed")


class TestServerOffline(unittest.TestCase):
    def test_search_mock(self):
        with mock.patch("dnb_mcp.http.fetch_text",
                        return_value=_read("search-tit-kafka.xml")):
            out = json.loads(srv.dnb_search_by_title("Briefe", limit=2))
        self.assertEqual(out["total_results"], 6044)
        self.assertEqual(out["count"], 2)
        self.assertIn("fetched_at", out)
        self.assertEqual(out["source"], "services.dnb.de")

    def test_isbn_mock(self):
        with mock.patch("dnb_mcp.http.fetch_text",
                        return_value=_read("by-isbn.xml")):
            out = json.loads(srv.dnb_by_isbn("9783100381682"))
        self.assertEqual(out["total_results"], 1)
        self.assertEqual(out["items"][0]["author"], "Kafka, Franz")

    def test_bad_isbn(self):
        out = json.loads(srv.dnb_by_isbn("abc"))
        self.assertIn("error", out)

    def test_empty_query(self):
        out = json.loads(srv.dnb_search_books("", limit=3))
        self.assertIn("error", out)


if __name__ == "__main__":
    unittest.main()
