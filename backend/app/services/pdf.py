"""Render Markdown plan to printable HTML and request PDF from pdf-service."""
from __future__ import annotations

import html as html_lib

import httpx

from app.config import settings


PRINT_CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #0B132B; background: #ffffff;
  font-size: 11pt; line-height: 1.55;
}
.page { padding: 0; }
.cover {
  background: linear-gradient(135deg, #8B5CF6 0%, #F43F5E 100%);
  color: white;
  padding: 60px 50px;
  border-radius: 0 0 24px 24px;
  margin-bottom: 32px;
}
.cover .brand { font-size: 14pt; letter-spacing: 6px; opacity: .85; }
.cover h1 { font-size: 30pt; margin: 18px 0 10px; line-height: 1.05; }
.cover .meta { font-size: 11pt; opacity: .9; }
main { padding: 0 50px 60px; }
h1 { color: #0B132B; font-size: 22pt; margin: 28px 0 12px; }
h2 {
  font-size: 16pt; margin: 28px 0 8px;
  background: linear-gradient(90deg,#8B5CF6,#F43F5E);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
h3 { font-size: 13pt; margin: 18px 0 6px; color: #0B132B; }
p { margin: 8px 0; }
ul, ol { padding-left: 22px; }
li { margin: 4px 0; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 24px 0; }
strong { color: #0B132B; }
code { background: #f3f4f6; padding: 1px 6px; border-radius: 4px; font-size: 10pt; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; }
th, td { border: 1px solid #e5e7eb; padding: 6px 10px; text-align: left; font-size: 10pt; }
th { background: #f9fafb; }
.footer {
  position: running(footer); font-size: 8pt; color: #94a3b8;
  text-align: center; padding: 8px 0;
}
@page { size: A4; margin: 16mm 14mm 18mm 14mm; }
"""


def _markdown_to_html(md: str) -> str:
    """Минимальный MD→HTML без зависимостей: заголовки, списки, жирный, hr, инлайн-код."""
    lines = md.splitlines()
    out: list[str] = []
    in_list: str | None = None  # 'ul' | 'ol' | None

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            close_list()
            out.append("")
            continue
        if line.startswith("### "):
            close_list()
            out.append(f"<h3>{_inline(line[4:])}</h3>")
            continue
        if line.startswith("## "):
            close_list()
            out.append(f"<h2>{_inline(line[3:])}</h2>")
            continue
        if line.startswith("# "):
            close_list()
            out.append(f"<h1>{_inline(line[2:])}</h1>")
            continue
        if line.strip() == "---":
            close_list()
            out.append("<hr/>")
            continue
        m = line.lstrip()
        indent = len(line) - len(m)
        if m.startswith("- ") or m.startswith("* "):
            if in_list != "ul":
                close_list()
                out.append("<ul>")
                in_list = "ul"
            out.append(f"<li>{_inline(m[2:])}</li>")
            continue
        if m[:2].isdigit() or (m[:1].isdigit() and m[1:2] == "."):
            # ordered list "1. foo"
            dot = m.find(". ")
            if dot != -1 and m[:dot].isdigit():
                if in_list != "ol":
                    close_list()
                    out.append("<ol>")
                    in_list = "ol"
                out.append(f"<li>{_inline(m[dot+2:])}</li>")
                continue
        close_list()
        out.append(f"<p>{_inline(line)}</p>")
        _ = indent  # not used currently
    close_list()
    return "\n".join(out)


def _inline(s: str) -> str:
    s = html_lib.escape(s, quote=False)
    # **bold**
    while "**" in s:
        idx1 = s.find("**")
        idx2 = s.find("**", idx1 + 2)
        if idx2 == -1:
            break
        s = s[:idx1] + "<strong>" + s[idx1 + 2 : idx2] + "</strong>" + s[idx2 + 2 :]
    # _italic_  (simple)
    # `code`
    while "`" in s:
        i1 = s.find("`")
        i2 = s.find("`", i1 + 1)
        if i2 == -1:
            break
        s = s[:i1] + "<code>" + s[i1 + 1 : i2] + "</code>" + s[i2 + 1 :]
    return s


def build_print_html(content_md: str, startup_name: str, region: str) -> str:
    body = _markdown_to_html(content_md)
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"/>
<title>RuDapt — {html_lib.escape(startup_name)}</title>
<style>{PRINT_CSS}</style>
</head><body>
<div class="page">
  <div class="cover">
    <div class="brand">RUDAPT · STARTUP LOCALIZATION AI</div>
    <h1>{html_lib.escape(startup_name)} → {html_lib.escape(region)}</h1>
    <div class="meta">Бизнес-план локализации</div>
  </div>
  <main>{body}</main>
</div>
</body></html>"""


async def render_pdf(html: str) -> bytes:
    url = settings.PDF_SERVICE_URL.rstrip("/") + "/render"
    headers = {}
    if settings.PDF_SERVICE_TOKEN:
        headers["X-PDF-Token"] = settings.PDF_SERVICE_TOKEN
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json={"html": html}, headers=headers)
        r.raise_for_status()
        return r.content
