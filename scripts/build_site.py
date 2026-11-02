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
:root {
  --ink: #16130c;
  --muted: #7a7360;
  --paper: #fdfaf0;
  --card: #ffffff;
  --line: #e8dfc6;
  --accent: #f4c518;
  --accent-ink: #16130c;
}
@media (prefers-color-scheme: dark) {
  :root {
    --ink: #f2ecd9;
    --muted: #a89f87;
    --paper: #191610;
    --card: #211d15;
    --line: #3a342a;
    --accent: #f4c518;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: -apple-system, "Segoe UI", Roboto, "PingFang SC",
    "Noto Sans SC", "Hiragino Sans GB", sans-serif;
  background: var(--paper);
  color: var(--ink);
  line-height: 1.6;
}
.wrap { max-width: 1080px; margin: 0 auto; padding: 48px 24px 64px; }
header h1 { margin: 0 0 6px; font-size: 40px; letter-spacing: -0.5px; }
header h1 span {
  background: var(--accent);
  color: var(--accent-ink);
  padding: 0 10px;
  border-radius: 6px;
}
header p { margin: 0; color: var(--muted); }
.grid {
  margin-top: 36px;
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
}
.card {
  background: var(--card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 22px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.card img {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  float: right;
  margin-left: 12px;
}
.card h2 { margin: 0; font-size: 20px; }
.card h2 a { color: inherit; text-decoration: none; }
.card h2 a:hover { text-decoration: underline; }
.card h3 { margin: 14px 0 4px; font-size: 15px; }
.card p { margin: 6px 0; font-size: 14.5px; }
.card ul { margin: 6px 0; padding-left: 20px; font-size: 14.5px; }
.card .at { color: var(--muted); font-size: 13px; }
.empty {
  margin-top: 36px;
  padding: 28px;
  text-align: center;
  color: var(--muted);
  border: 2px dashed var(--line);
  border-radius: 14px;
}
footer {
  margin-top: 48px;
  color: var(--muted);
  font-size: 13.5px;
}
footer a { color: var(--muted); }
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
<style>%(style)s</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>GitHub <span>Playground</span></h1>
  <p>%(count)s — one file per person, living in <code>profiles/</code>. This page is rebuilt by CI on every merge.</p>
</header>
%(body)s
<footer>
  Add yourself: fork the repo, create <code>profiles/&lt;your-github-username&gt;.md</code>, open a pull request ·
  <a href="%(repo)s">source on GitHub</a>
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
