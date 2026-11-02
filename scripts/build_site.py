#!/usr/bin/env python3
"""Regenerate docs/index.html from profiles/*.md — the GitHub Pages roster.

Stdlib only: reads every profile (files starting with "_" are templates),
renders a small Markdown subset (headings, bold, lists, paragraphs) into
escaped HTML, and writes a single self-contained page with one card per
person. Avatars come straight from github.com/<username>.png.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "profiles"
OUTPUT = ROOT / "docs" / "index.html"

REPO_URL = "https://github.com/CompPsyUnion/github-playground"

STYLE = """
/* CPU brand: yellow #f7d447 / ink #111 / white — Swiss poster style with
   blueprint dashed guides and yellow-shadow window cards (see the cpu
   Marp theme for the deck counterpart). */
:root {
  --yellow: #f7d447;
  --ink: #111111;
  --gray: #a3a3a3;
  --grid: #e3d5a8;
  --sans: 'Noto Sans SC', 'PingFang SC', 'Hiragino Sans', sans-serif;
  --display: 'Archivo Black', 'Arial Black', 'Noto Sans SC', sans-serif;
  --mono: ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: var(--sans);
  font-weight: 500;
  background: #ffffff;
  color: var(--ink);
  line-height: 1.6;
}
.wrap {
  max-width: 1080px;
  margin: 0 auto;
  padding: 56px 64px 72px;
  position: relative;
}
/* blueprint margin guides, as on every CPU slide */
.wrap::before {
  content: '';
  position: absolute;
  top: 24px;
  bottom: 24px;
  left: 28px;
  right: 28px;
  border-left: 2px dashed var(--grid);
  border-right: 2px dashed var(--grid);
  pointer-events: none;
}
header h1 {
  margin: 0 0 10px;
  font-family: var(--display);
  font-size: 44px;
  font-weight: 400;
  letter-spacing: -0.03em;
  line-height: 1.15;
}
header h1 span {
  display: inline-block;
  background: var(--yellow);
  padding: 0 14px;
  border-radius: 6px;
}
header .meta {
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #c9b96c;
}
.grid {
  margin-top: 40px;
  display: grid;
  gap: 28px;
  /* min() lets the column shrink below 290px on narrow screens,
     so phones get a single full-width column without overflow */
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 290px), 1fr));
}
/* the CPU window card: ink border + yellow offset shadow */
.card {
  background: #ffffff;
  border: 2.5px solid var(--ink);
  border-radius: 12px;
  padding: 22px 24px;
  box-shadow: 7px 7px 0 var(--yellow);
}
.card img {
  width: 56px;
  height: 56px;
  border: 2.5px solid var(--ink);
  border-radius: 50%;
  float: right;
  margin-left: 12px;
  background: var(--yellow);
}
.card h2 { margin: 0; font-size: 20px; font-weight: 900; }
.card h2 a { color: inherit; text-decoration: none; }
.card h2 a:hover { text-decoration: underline; }
.card .at {
  display: inline-block;
  margin-top: 4px;
  padding: 1px 10px;
  background: var(--yellow);
  border: 2px solid var(--ink);
  border-radius: 999px;
  font-family: var(--mono);
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.card h3 {
  margin: 14px 0 4px;
  padding-left: 10px;
  border-left: 6px solid var(--yellow);
  font-size: 15px;
  font-weight: 700;
}
.card p { margin: 6px 0; font-size: 14.5px; }
.card ul { margin: 6px 0; padding-left: 20px; font-size: 14.5px; }
.empty {
  margin-top: 40px;
  padding: 32px;
  text-align: center;
  color: var(--gray);
  border: 2px dashed var(--grid);
  border-radius: 12px;
}
footer {
  margin-top: 56px;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--gray);
}
footer a { color: var(--gray); }

/* ---------- phones ---------- */
@media (max-width: 720px) {
  .wrap { padding: 28px 20px 40px; }
  /* the blueprint guides crowd the text on a phone — let them go */
  .wrap::before { display: none; }
  header h1 { font-size: 32px; }
  .grid { margin-top: 28px; gap: 22px; }
  .card {
    padding: 18px;
    box-shadow: 5px 5px 0 var(--yellow);
  }
  footer {
    margin-top: 40px;
    letter-spacing: 0.04em;
    overflow-wrap: anywhere;
  }
}
"""


def inline(text):
    """Escape HTML, then re-apply **bold** and `code`."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def render_markdown(text):
    """Tiny renderer: # / ## / ## headings, - lists, blank-line paragraphs."""
    out = []
    paragraph = []
    list_open = False

    def flush_paragraph():
        nonlocal paragraph
        if paragraph:
            out.append("<p>%s</p>" % "<br>".join(paragraph))
            paragraph = []

    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            close_list()
        elif stripped.startswith("### "):
            flush_paragraph()
            close_list()
            out.append("<h3>%s</h3>" % inline(stripped[4:]))
        elif stripped.startswith("## "):
            flush_paragraph()
            close_list()
            out.append("<h3>%s</h3>" % inline(stripped[3:]))
        elif stripped.startswith("# "):
            flush_paragraph()
            close_list()
            out.append("<h3>%s</h3>" % inline(stripped[2:]))
        elif stripped.startswith(("-", "* ")) or stripped.startswith("- "):
            flush_paragraph()
            if not list_open:
                out.append("<ul>")
                list_open = True
            out.append("<li>%s</li>" % inline(stripped.lstrip("-* ")))
        else:
            close_list()
            paragraph.append(inline(stripped))
    flush_paragraph()
    close_list()
    return "\n".join(out)


def card_html(path):
    username = path.stem
    text = path.read_text(encoding="utf-8").strip()
    body = render_markdown(text)
    avatar = "https://github.com/%s.png?size=112" % username
    return (
        '<section class="card">\n'
        '  <img src="%s" alt="%s" loading="lazy">\n'
        '  <h2><a href="https://github.com/%s">%s</a></h2>\n'
        '  <div class="at">@%s</div>\n'
        '  %s\n'
        "</section>" % (avatar, username, username, username, username, body)
    )


def main():
    if PROFILES.is_dir():
        files = sorted(
            p for p in PROFILES.glob("*.md") if not p.name.startswith("_")
        )
    else:
        files = []

    if files:
        cards = "\n".join(card_html(p) for p in files)
        body_block = '<div class="grid">\n%s\n</div>' % cards
        count = "%d profile%s" % (len(files), "s" if len(files) != 1 else "")
    else:
        body_block = (
            '<div class="empty">No profiles yet — be the first:<br>'
            "add <code>profiles/&lt;your-github-username&gt;.md</code></div>"
        )
        count = "0 profiles"

    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub Playground · Profiles</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Noto+Sans+SC:wght@400;500;700;900&display=swap">
<style>%(style)s</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>GitHub <span>Playground</span></h1>
  <p class="meta">%(count)s · PROFILES/ · REBUILT BY CI</p>
</header>
%(body)s
<footer>
  ADD YOURSELF: FORK → PROFILES/&lt;USERNAME&gt;.MD → PULL REQUEST ·
  <a href="%(repo)s">SOURCE ON GITHUB</a>
</footer>
</div>
</body>
</html>
""" % {"style": STYLE, "count": count, "body": body_block, "repo": REPO_URL}

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print("wrote %s (%s)" % (OUTPUT.relative_to(ROOT), count))


if __name__ == "__main__":
    main()
