"""Domain logic: shape DNB SRU (MARC21-xml) responses into compact
dicts (stdlib only).

Data source: the Deutsche Nationalbibliothek SRU API
(https://services.dnb.de/sru/dnb) — free, no key, no login.
CQL indexes used (from the API's own explain response, verified
2026-11-10): woe (all terms), tit (title), per (person/author),
num (number — incl. ISBN), idn (DNB identifier).

NOT offered: a newspapers-only search — the `mat` (material type)
index returns 0 for every German value tried (Bücher, Zeitschriften,
Zeitung, Zeitungen, Online-Ressource), so no reliable newspaper
filter exists; newspapers are still found by the keyword/title
searches. Dublin Core recordSchema is unsupported ("Unknown schema
for retrieval") — MARC21-xml only.
"""
from __future__ import annotations

import re
import urllib.parse
import xml.etree.ElementTree as ET

BASE = "https://services.dnb.de/sru/dnb"

SRW = "{http://www.loc.gov/zing/srw/}"
M = "{http://www.loc.gov/MARC21/slim}"

_ISBN_RE = re.compile(r"^[\d-]{10,17}[0-9Xx]$")


def validate_limit(limit: int) -> int:
    if not 1 <= limit <= 50:
        raise ValueError(f"limit out of range: {limit} (expected 1..50)")
    return limit


def validate_isbn(isbn: str) -> str:
    key = (isbn or "").strip().replace(" ", "")
    if not _ISBN_RE.match(key) or not 10 <= len(key.replace("-", "")) <= 13:
        raise ValueError(f"invalid ISBN: {isbn!r} "
                         "(expected 10 or 13 digits, dashes allowed)")
    return key


def validate_dnb_id(dnb_id: str) -> str:
    key = (dnb_id or "").strip()
    if not key.isdigit():
        raise ValueError(f"invalid DNB identifier: {dnb_id!r} "
                         "(expected digits, e.g. \"1306459214\")")
    return key


def search_url(query: str, maximum_records: int = 10) -> str:
    params = {
        "operation": "searchRetrieve",
        "version": "1.1",
        "query": query,
        "recordSchema": "MARC21-xml",
        "maximumRecords": str(maximum_records),
    }
    return BASE + "?" + urllib.parse.urlencode(params)


def _subs(record, tag, code):
    return [s.text.strip() for df in record.findall(f"{M}datafield[@tag='{tag}']")
            for s in df.findall(f"{M}subfield[@code='{code}']")
            if (s.text or "").strip()]


def _first(record, tag, code):
    vals = _subs(record, tag, code)
    return vals[0] if vals else ""


def _compact(record) -> dict:
    title = _first(record, "245", "a")
    subtitle = _first(record, "245", "b")
    if subtitle:
        title = f"{title} : {subtitle}"
    author = _first(record, "100", "a") or _first(record, "110", "a")
    return {
        "dnb_id": (record.findtext(f"{M}controlfield[@tag='001']") or "").strip(),
        "title": title,
        "author": author,
        "contributors": _subs(record, "700", "a")[:3],
        "year": _first(record, "264", "c"),
        "publisher": _first(record, "264", "b"),
        "place": _first(record, "264", "a"),
        "edition": _first(record, "250", "a"),
        "isbn": _first(record, "020", "a"),
        "language": _first(record, "041", "a"),
        "pages": _first(record, "300", "a"),
        "subjects": _subs(record, "653", "a")[:5],
        "url": _first(record, "856", "u"),
    }


def parse_search(text: str) -> dict:
    """Parse an SRU searchRetrieve response -> {total_results, items}."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise ValueError(f"invalid SRU response: {e}") from e
    diag = root.find(f"{SRW}diagnostics")
    if diag is not None:
        details = diag.findtext(".//{http://www.loc.gov/zing/srw/diagnostic/}details") or ""
        msg = diag.findtext(".//{http://www.loc.gov/zing/srw/diagnostic/}message") or ""
        raise ValueError(f"DNB SRU error: {details} ({msg})".strip())
    total = root.findtext(f"{SRW}numberOfRecords")
    try:
        total_n = int(total or "0")
    except ValueError:
        total_n = 0
    items = []
    for rec in root.findall(f"{SRW}records/{SRW}record"):
        data = rec.find(f"{SRW}recordData/{M}record")
        if data is not None:
            items.append(_compact(data))
    return {"total_results": total_n, "items": items}
