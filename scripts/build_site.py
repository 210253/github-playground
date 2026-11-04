#!/usr/bin/env python3
"""Regenerate the GitHub Pages roster from profiles/*.md.

Stdlib only. Writes docs/index.html — one card per profile (avatars from
github.com/<username>.png). The live button re-fetches this very page and
diffs the cards in the DOM, so no second data file is needed.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "profiles"
OUTPUT_HTML = ROOT / "docs" / "index.html"

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
/* a card that just arrived via live refresh flashes yellow */
.card--new { animation: newcard 2.4s ease-out; }
@keyframes newcard {
  0% { background: var(--yellow); transform: scale(0.96); }
  100% { background: #ffffff; transform: scale(1); }
}
/* an existing card whose content was swapped in by live refresh */
.card--updated { animation: updatecard 2.4s ease-out; }
@keyframes updatecard {
  0%, 45% { background: var(--yellow); }
  100% { background: #ffffff; }
}
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

/* ---------- live (stage) mode ---------- */
#live {
  position: fixed;
  top: 18px;
  right: 18px;
  z-index: 50;
  padding: 8px 16px;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ink);
  background: #ffffff;
  border: 2.5px solid var(--ink);
  border-radius: 999px;
  box-shadow: 4px 4px 0 var(--yellow);
  cursor: pointer;
}
#live:hover { background: var(--yellow); }
#live.on { background: var(--yellow); }
#live .dot {
  display: inline-block;
  width: 9px;
  height: 9px;
  margin-right: 8px;
  border-radius: 50%;
  background: var(--gray);
  vertical-align: 1px;
}
#live.on .dot {
  background: var(--ink);
  animation: pulse 1.6s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.25; }
}

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
  #live { top: 12px; right: 12px; padding: 6px 12px; font-size: 12px; }
}
"""

SCRIPT = """
(function () {
  var btn = document.getElementById('live');
  var meta = document.querySelector('header .meta');
  var grid = document.querySelector('.grid');
  var on = false, timer = null, raf = null;

  var SCROLL_SPEED = 30;    // px per second
  var BOTTOM_PAUSE = 2500;  // ms to hold at the bottom before looping
  var FETCH_EVERY = 10000;  // ms between page re-fetches

  /* ---------- endless slow scroll ---------- */
  var lastTs = 0, holdUntil = 0;
  function step(ts) {
    if (!on) { raf = null; return; }
    if (!lastTs) lastTs = ts;
    var dt = (ts - lastTs) / 1000;
    lastTs = ts;
    var doc = document.documentElement;
    var max = doc.scrollHeight - window.innerHeight;
    if (max > 0 && window.scrollY >= max - 1 && !holdUntil) {
      holdUntil = ts + BOTTOM_PAUSE;
    }
    if (holdUntil) {
      if (ts >= holdUntil) { holdUntil = 0; window.scrollTo(0, 0); }
    } else {
      window.scrollTo(0, Math.min(max, window.scrollY + SCROLL_SPEED * dt));
    }
    raf = requestAnimationFrame(step);
  }

  /* ---------- data refresh ---------- */
  function cardMap() {
    var map = {};
    grid.querySelectorAll('.card[data-user]').forEach(function (c) {
      map[c.getAttribute('data-user')] = c;
    });
    return map;
  }

  function updateCount(n) {
    if (meta) {
      meta.textContent = n + ' PROFILE' + (n === 1 ? '' : 'S') +
        ' · PROFILES/ · REBUILT BY CI' + (on ? ' · LIVE' : '');
    }
  }

  function fetchNew() {
    /* re-fetch the page itself and diff its cards against the live DOM:
       append brand-new users, and swap in edited content for existing
       ones (fix/* updates) so the stage view never goes stale */
    fetch(window.location.href, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.text() : null; })
      .then(function (text) {
        if (!text) return;
        var doc = new DOMParser().parseFromString(text, 'text/html');
        var fresh = doc.querySelectorAll('.card[data-user]');
        if (!fresh.length) return;
        var live = cardMap();
        var changed = 0;
        fresh.forEach(function (card) {
          var user = card.getAttribute('data-user');
          var current = live[user];
          if (!current) {
            var node = document.importNode(card, true);
            node.classList.add('card--new');
            grid.appendChild(node);
            changed++;
            return;
          }
          if (current.innerHTML.trim() === card.innerHTML.trim()) return;
          var updated = document.importNode(card, true);
          updated.classList.add('card--updated');
          current.replaceWith(updated);
          changed++;
        });
        if (!changed) return;
        var empty = grid.querySelector('.empty');
        if (empty) empty.remove();
        updateCount(Object.keys(cardMap()).length);
      })
      .catch(function () { /* stage safety: stay quiet on network hiccups */ });
  }

  /* ---------- the button ---------- */
  btn.addEventListener('click', function () {
    on = !on;
    btn.classList.toggle('on', on);
    btn.querySelector('.label').textContent = on ? 'LIVE' : 'AUTO PLAY';
    if (on) {
      lastTs = 0; holdUntil = 0;
      raf = requestAnimationFrame(step);
      timer = setInterval(fetchNew, FETCH_EVERY);
      fetchNew();
    } else {
      cancelAnimationFrame(raf); raf = null;
      clearInterval(timer); timer = null;
    }
    updateCount(Object.keys(cardMap()).length);
  });
})();
"""


def inline(text):
    """Escape HTML, then re-apply **bold** and `code`."""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def render_markdown(text):
    """Tiny renderer: # headings, - lists, blank-line paragraphs."""
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
        elif stripped.startswith("#"):
            flush_paragraph()
            close_list()
            out.append("<h3>%s</h3>" % inline(stripped.lstrip("#").strip()))
        elif stripped.startswith(("-", "*")):
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


def load_profiles():
    """One entry per profile: username (from the filename) + body HTML."""
    if not PROFILES.is_dir():
        return []
    entries = []
    for path in sorted(PROFILES.glob("*.md")):
        if path.name.startswith("_"):
            continue
        text = path.read_text(encoding="utf-8").strip()
        entries.append(
            {"username": path.stem, "body": render_markdown(text)}
        )
    return entries


def card_html(entry):
    username = entry["username"]
    avatar = "https://github.com/%s.png?size=112" % username
    return (
        '<section class="card" data-user="%s">\n'
        '  <img src="%s" alt="%s" loading="lazy">\n'
        '  <h2><a href="https://github.com/%s">%s</a></h2>\n'
        '  <div class="at">@%s</div>\n'
        '  %s\n'
        "</section>"
        % (username, avatar, username, username, username, username,
           entry["body"])
    )


def main():
    entries = load_profiles()

    if entries:
        cards = "\n".join(card_html(e) for e in entries)
        body_block = '<div class="grid">\n%s\n</div>' % cards
        count = "%d PROFILE%s" % (len(entries), "S" if len(entries) != 1 else "")
    else:
        body_block = (
            '<div class="grid">\n'
            '<div class="empty">No profiles yet — be the first:<br>'
            "add <code>profiles/&lt;your-github-username&gt;.md</code></div>\n"
            "</div>"
        )
        count = "0 PROFILES"

    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GitHub Playground · Profiles</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Noto+Sans+SC:wght@400;500;700;900&display=swap">
<style>%s</style>
</head>
<body>
<button id="live" type="button" aria-pressed="false">
  <span class="dot"></span><span class="label">AUTO PLAY</span>
</button>
<div class="wrap">
<header>
  <h1>GitHub <span>Playground</span></h1>
  <p class="meta">%s · PROFILES/ · REBUILT BY CI</p>
</header>
%s
<footer>
  ADD YOURSELF: FORK → PROFILES/&lt;USERNAME&gt;.MD → PULL REQUEST ·
  <a href="%s">SOURCE ON GITHUB</a>
</footer>
</div>
<script>%s</script>
</body>
</html>
""" % (STYLE, count, body_block, REPO_URL, SCRIPT)

    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_HTML.write_text(page, encoding="utf-8")
    print("wrote %s (%d profiles)"
          % (OUTPUT_HTML.relative_to(ROOT), len(entries)))


if __name__ == "__main__":
    main()

