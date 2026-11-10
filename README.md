# dnb-mcp 📚

mcp-name: io.github.mohammad-abbasi-sh/dnb-mcp

Unofficial **read-only** MCP server for **[services.dnb.de](https://www.dnb.de)** — Deutsche Nationalbibliothek catalogue via its official SRU API: keyword, title and author search, ISBN and DNB-ID lookup. No key, no login. No key, no login.

> Built by Mohammad Abbasi as part of the "Germany MCP factory". Not affiliated with services.dnb.de.

## For AI agents

Add to your MCP client config (stdio):

```json
{
  "mcpServers": {
    "dnb": {
      "command": "uvx",
      "args": ["dnb-mcp==0.1.0"]
    }
  }
}
```

Or run locally: `python -m dnb_mcp.server` (needs `mcp<2`, `httpx`).

## Tools

| Tool | Description |
|------|-------------|
| `dnb_search_books` | Keyword search across the DNB catalogue — `query`, `limit` 1..50 |
| `dnb_search_by_title` | Title search — `title`, `limit` 1..50 |
| `dnb_search_by_author` | Author search — `author` (e.g. "Kafka, Franz"), `limit` 1..50 |
| `dnb_by_isbn` | Look up one book by ISBN — `isbn` (13 or 10 digits, with or without dashes) |
| `dnb_get_record` | Full record by DNB identifier — `dnb_id` (e.g. "1306459214") |
| `dnb_health` | Reachability probe (ok / blocked / error) — one polite request |

## Notes

- All data comes from the **Deutsche Nationalbibliothek SRU API** (free, no key, no login).
- Indexes used (from the API's own explain response): `woe` (all terms), `tit` (title), `per` (person/author), `num` (number incl. ISBN), `idn` (DNB identifier).
- There is **no newspapers-only filter**: the `mat` (material type) index returns 0 for every German value tried (Bücher, Zeitschriften, Zeitung, Zeitungen, Online-Ressource), so no newspapers-only tool is offered; newspapers are still found by the keyword and title searches.
- Dublin Core recordSchema is unsupported by the API — MARC21-xml only.

Tests: 20/20 green (14 offline + 6 live, 2026-11-10).

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## License

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
