#!/usr/bin/env python3
"""CI check for profile pull requests.

Two layers of rules:

1. Repo-wide format check (always runs): every file in profiles/ is a
   valid profile — GitHub-username filename, >= MIN_CHARS of content,
   starting with a "# Title" line. Files starting with "_" are templates.

2. PR rules (when --author and --pr-files are given, i.e. on pull_request):
   a profile PR must add EXACTLY ONE new file, and it must be
   profiles/<pr-author-login>.md — named after the PR author's own
   GitHub username. Anything else is an error.

Exit code is non-zero when any rule is broken; messages carry GitHub
Actions annotations so they show up right on the PR.
"""

import argparse
import re
import sys
from pathlib import Path

USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
MIN_CHARS = 20
ROOT = Path(__file__).resolve().parent.parent
PROFILES = ROOT / "profiles"


def note_error(message):
    print("::error::%s" % message.replace("\n", " "))


def check_file(path):
    name = path.stem
    errors = []
    if not USERNAME_RE.match(name):
        errors.append(
            "%s: filename must be a GitHub username — letters, digits and "
            "hyphens only, up to 39 characters (got %r)" % (path.name, name)
        )
    text = path.read_text(encoding="utf-8").strip()
    if len(text) < MIN_CHARS:
        errors.append(
            "%s: content is too short — write at least %d characters about "
            "yourself (got %d)" % (path.name, MIN_CHARS, len(text))
        )
    if not any(line.startswith("# ") for line in text.splitlines()):
        errors.append('%s: start the file with a "# Title" line' % path.name)
    return errors


def check_repo():
    """Layer 1: every profile in the repo is well-formed."""
    if not PROFILES.is_dir():
        note_error("profiles/ directory is missing")
        return False
    files = sorted(
        p for p in PROFILES.glob("*.md") if not p.name.startswith("_")
    )
    if not files:
        print("profiles/ is empty — no profiles to check yet.")
        return True

    ok = True
    for path in files:
        for message in check_file(path):
            note_error(message)
            ok = False
        if not check_file(path):
            print("OK  %s" % path.name)
    print("Repo check: %d profile(s) scanned%s"
          % (len(files), "" if ok else " — problems found above"))
    return ok


def check_pr(author, pr_files_path):
    """Layer 2: this PR adds exactly one file — profiles/<author>.md."""
    rows = []
    for line in Path(pr_files_path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) == 2:
            rows.append((parts[0], parts[1]))
        else:
            rows.append(("changed", parts[0]))

    expected = "profiles/%s.md" % author
    errors = []

    if len(rows) != 1:
        preview = ", ".join(name for _, name in rows[:5]) or "nothing"
        errors.append(
            "a profile PR must change exactly ONE file — this one changes "
            "%d (%s). Keep the PR to your own profile only."
            % (len(rows), preview)
        )
    else:
        status, filename = rows[0]
        if filename != expected:
            errors.append(
                "wrong file: %r — your profile must be %r, named after "
                "your own GitHub username (@%s)"
                % (filename, expected, author)
            )
        if status not in ("added",):
            errors.append(
                "%s must be a NEW file (GitHub reports status %r) — each "
                "person adds exactly one profile; if it already exists, "
                "edit your own file instead of adding it again"
                % (expected, status)
            )

    for message in errors:
        note_error(message)
    if not errors:
        print("PR check: adds exactly one new file, %s — matches author "
              "@%s." % (expected, author))
    return not errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--author", default=None,
        help="GitHub login of the PR author (enables PR rules)",
    )
    parser.add_argument(
        "--pr-files", default=None,
        help="TSV file of <status>\\t<path> changed in the PR",
    )
    args = parser.parse_args()

    ok = check_repo()

    if args.author and args.pr_files:
        ok = check_pr(args.author, args.pr_files) and ok
    elif args.author or args.pr_files:
        note_error("--author and --pr-files must be given together")
        ok = False

    print("")
    print("Profiles check: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
