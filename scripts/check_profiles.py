#!/usr/bin/env python3
"""CI check for the profiles/ directory.

Rules (one file per person, named after their GitHub username):
- filename: <github-username>.md  (letters / digits / single hyphens, max 39 chars)
- content:  at least MIN_CHARS characters and starts with a "# Title" line
Files starting with "_" are templates and are ignored.

Prints a readable report and exits non-zero when any rule is broken.
"""

import re
import sys
from pathlib import Path

USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
MIN_CHARS = 20
PROFILES = Path(__file__).resolve().parent.parent / "profiles"


def check_file(path):
    name = path.stem
    errors = []
    if not USERNAME_RE.match(name):
        errors.append(
            "%s: filename must be your GitHub username — letters, digits and "
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


def main():
    if not PROFILES.is_dir():
        print("::error::profiles/ directory is missing")
        return 1

    files = sorted(
        p for p in PROFILES.glob("*.md") if not p.name.startswith("_")
    )
    if not files:
        print("profiles/ is empty — no profiles to check yet.")
        return 0

    all_errors = []
    for path in files:
        errors = check_file(path)
        if errors:
            for message in errors:
                print("::error file=%s::%s" % (path, message))
                all_errors.append(message)
        else:
            print("OK  %s" % path.name)

    print("")
    if all_errors:
        print("Profiles check: %d file(s) with problems:" % len(all_errors))
        for message in all_errors:
            print("  - %s" % message)
        return 1
    print("Profiles check: all %d profile(s) look good." % len(files))
    return 0


if __name__ == "__main__":
    sys.exit(main())
