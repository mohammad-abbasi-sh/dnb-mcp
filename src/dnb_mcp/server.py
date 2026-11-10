"""MCP server: unofficial read-only access to the Deutsche
Nationalbibliothek catalogue via its official SRU API. No key, no
login. NOTE: the `mat` (material type) index returns 0 for every
German value tried, so no newspapers-only filter is offered."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from . import domain as _dom
from . import http as _http

INSTRUCTIONS = """\
Unofficial read-only MCP server for the Deutsche \
Nationalbibliothek catalogue via its official SRU API (no key, no \
login): keyword, title and author search, ISBN lookup and full \
records by DNB identifier. NOTE: the SRU `mat` (material type) \
index returns 0 for every German value tried, so no newspapers-only \
filter is offered — newspapers are still found by the keyword and \
title searches. Built by Mohammad Abbasi (mohammad-abbasi-sh) — \
https://almanibama.ir · https://mabbasi.ir — Germany MCP factory.\
"""

_SOURCE = "services.dnb.de"
_DISCLAIMER = "Unofficial read-only data from the Deutsche Nationalbibliothek SRU API; verify on dnb.de before acting on it."


def _envelope() -> dict:
    return {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": _SOURCE,
        "disclaimer": _DISCLAIMER,
    }


def _ok(payload: dict) -> str:
    return json.dumps({**_envelope(), **payload}, ensure_ascii=False)


def _err(e: Exception) -> str:
    return _ok({"error": str(e)})


mcp = FastMCP("dnb-mcp", instructions=INSTRUCTIONS)


def _search(cql: str, limit: int) -> dict:
    lim = _dom.validate_limit(limit)
    parsed = _dom.parse_search(
        _http.fetch_text(_dom.search_url(cql, maximum_records=lim)))
    return {"total_results": parsed["total_results"],
            "count": len(parsed["items"]), "items": parsed["items"]}


@mcp.tool()
def dnb_search_books(query: str, limit: int = 10) -> str:
    """Keyword search across the whole DNB catalogue (all fields).
    query: keyword or phrase, e.g. "Kafka". limit: 1..50 (default 10)."""
    try:
        q = (query or "").strip()
        if not q:
            raise ValueError("query must not be empty")
        out = _search(f"woe={q}", limit)
    except (_http.DnbMcpError, ValueError) as e:
        return _err(e)
    return _ok({"query": q, **out})


@mcp.tool()
def dnb_search_by_title(title: str, limit: int = 10) -> str:
    """Search the DNB catalogue by title. title: e.g. "Briefe 1921-1922".
    limit: 1..50 (default 10)."""
    try:
        q = (title or "").strip()
        if not q:
            raise ValueError("title must not be empty")
        out = _search(f"tit={q}", limit)
    except (_http.DnbMcpError, ValueError) as e:
        return _err(e)
    return _ok({"title": q, **out})


@mcp.tool()
def dnb_search_by_author(author: str, limit: int = 10) -> str:
    """Search the DNB catalogue by author. author: e.g. "Kafka, Franz".
    limit: 1..50 (default 10)."""
    try:
        q = (author or "").strip()
        if not q:
            raise ValueError("author must not be empty")
        out = _search(f"per={q}", limit)
    except (_http.DnbMcpError, ValueError) as e:
        return _err(e)
    return _ok({"author": q, **out})


@mcp.tool()
def dnb_by_isbn(isbn: str) -> str:
    """Look up one book by ISBN. isbn: 10 or 13 digits, dashes allowed,
    e.g. "9783100381682"."""
    try:
        key = _dom.validate_isbn(isbn)
        out = _search(f"num={key}", 1)
        if not out["items"]:
            return _ok({"isbn": key, "total_results": 0, "count": 0,
                        "items": []})
    except (_http.DnbMcpError, ValueError) as e:
        return _err(e)
    return _ok({"isbn": key, **out})


@mcp.tool()
def dnb_get_record(dnb_id: str) -> str:
    """Full record by DNB identifier. dnb_id: digits, e.g. "1306459214"
    (the ID shown on every record)."""
    try:
        key = _dom.validate_dnb_id(dnb_id)
        out = _search(f"idn={key}", 1)
        if not out["items"]:
            return _ok({"dnb_id": key, "total_results": 0, "count": 0,
                        "items": []})
    except (_http.DnbMcpError, ValueError) as e:
        return _err(e)
    return _ok({"dnb_id": key, **out})


@mcp.tool()
def dnb_health() -> str:
    """Check whether services.dnb.de is reachable right now.

    Returns status ok (HTTP 200), blocked (HTTP 403/429 — bot wall or
    rate limit) or error, plus the HTTP status and the probed URL.
    One polite request; it does not fetch any listings."""
    return _ok(_http.health_check())


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    sys.exit(main())
