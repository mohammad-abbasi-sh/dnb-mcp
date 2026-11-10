# dnb-mcp 📚

mcp-name: io.github.mohammad-abbasi-sh/dnb-mcp

Inoffizieller **nur lesender** MCP-Server für **[services.dnb.de](https://www.dnb.de)** — Katalog der Deutschen Nationalbibliothek über die offizielle SRU-API: Stichwort-, Titel- und Autorensuche, ISBN- und DNB-ID-Abfrage. Kein Schlüssel, kein Login. Kein Schlüssel, keine Anmeldung.

> Gebaut von Mohammad Abbasi als Teil der "Germany MCP factory". Nicht mit services.dnb.de verbunden.

## Für KI-Agenten

Zur MCP-Client-Konfiguration hinzufügen (stdio):

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

Oder lokal starten: `python -m dnb_mcp.server` (benötigt `mcp<2`, `httpx`).

## Tools

| Tool | Beschreibung |
|------|-------------|
| `dnb_search_books` | Stichwortsuche im DNB-Katalog |
| `dnb_search_by_title` | Titelsuche im DNB-Katalog |
| `dnb_search_by_author` | Autorensuche im DNB-Katalog |
| `dnb_by_isbn` | Ein Buch per ISBN nachschlagen |
| `dnb_get_record` | Vollständiger Datensatz per DNB-ID |
| `dnb_health` | Erreichbarkeitsprüfung (ok / blocked / error) — eine höfliche Anfrage |

## Entwicklung

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## Lizenz

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
