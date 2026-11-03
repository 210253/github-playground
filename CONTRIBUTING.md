# Contributing to github-playground

This repository is the hands-on playground for the CPU weekly session on
GitHub. Everyone is welcome to add their profile — the whole flow works
in the browser, no tools installed.

## Add your profile

1. **Fork** this repository.
2. In your fork, open the `profiles/` directory → **Add file → Create new
   file** → name it `<your-github-username>.md`.
3. Write a short intro: start with a `# Title` line, a few lines about
   yourself. Copy `profiles/_template.md` if you like a starting point.
4. In the commit dialog choose **Create a new branch for this commit** and
   name the branch `docs/add-<your-username>` — the `docs/` prefix
   matters, see below.
5. Commit, then click **Compare & pull request** back to
   `CompPsyUnion/github-playground:main`. A clear title (for example
   `feat: add <username> to profiles`) and a two-line description are
   appreciated.
6. CI checks your PR. When it passes, the robot squash-merges it within
   seconds — and the roster page rebuilds automatically.

## The contract CI enforces

Pull requests from `docs/*` branches are validated by
`scripts/check_profiles.py` (see the run's Summary page for the report):

- the PR changes **exactly one file**;
- the file is **`profiles/<your-github-username>.md`** — named after the
  PR author's own login, and newly added (not someone else's file);
- the content is at least 20 characters and starts with a `# Title` line, for example, `# Robert He`.

Anything else fails the check with an explanation, and the robot will not
merge it.

Maintainers (maintain/admin permission) and the `PROFILE_BYPASS` list in
the workflow skip these per-PR rules; PRs from other branch prefixes are
not auto-merged and are reviewed manually.

## For maintainers

```bash
python scripts/check_profiles.py       # run the same checks locally
python scripts/build_site.py           # rebuild docs/index.html + roster
```

`docs/index.html` is regenerated and committed by CI on every merge to
`main`; you should never need to edit it by hand.
