# dnb-mcp 📚

mcp-name: io.github.mohammad-abbasi-sh/dnb-mcp

سرور MCP غیررسمی و **فقط‌خواندنی** برای **[services.dnb.de](https://www.dnb.de)** — کاتالوگ کتابخانه ملی آلمان از طریق API رسمی SRU: جست‌وجوی کلیدواژه، عنوان و نویسنده، جست‌وجو با ISBN و شناسهٔ DNB. بدون کلید، بدون ورود. بدون کلید، بدون ورود.

> ساختهٔ محمد عباسی، بخشی از «کارخانهٔ MCP آلمان». وابسته به services.dnb.de نیست.

## برای ایجنت‌های هوش مصنوعی

به پیکربندی MCP کلاینت اضافه کنید (stdio):

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

یا به‌صورت محلی اجرا کنید: `python -m dnb_mcp.server` (نیازمند `mcp<2` و `httpx`).

## ابزارها

| ابزار | توضیح |
|------|-------|
| `dnb_search_books` | جست‌وجوی کلیدواژه در کاتالوگ DNB |
| `dnb_search_by_title` | جست‌وجو در کاتالوگ DNB با عنوان |
| `dnb_search_by_author` | جست‌وجو در کاتالوگ DNB با نویسنده |
| `dnb_by_isbn` | یافتن یک کتاب با ISBN |
| `dnb_get_record` | رکورد کامل با شناسهٔ DNB |
| `dnb_health` | بررسی دسترس‌پذیری (ok / blocked / error) — یک درخواست مؤدبانه |

## توسعه

```bash
python3 -m venv .venv && .venv/bin/pip install "mcp<2" httpx pytest
.venv/bin/pip install -e .
.venv/bin/python -m pytest tests/ -q
```

## لایسنس

MIT

---

Built by [Mohammad Abbasi](https://github.com/mohammad-abbasi-sh) — [Almanibama](https://almanibama.ir) · [mabbasi.ir](https://mabbasi.ir)
