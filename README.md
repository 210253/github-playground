# github-playground

The hands-on playground for the CPU weekly session **GitHub Beyond the Code** — everyone opens their first pull request here.

## Add yourself (browser only, no install)

1. **Fork** this repository.
2. In your fork, open the `profiles/` directory → **Add file → Create new file** → name it `<your-github-username>.md`.
3. Start with a `# Title` line and write a few lines about yourself (copy `profiles/_template.md` if you like).
4. Commit on a **new branch** (the commit dialog offers "Create a new branch"), then **Compare & pull request** back to `CompPsyUnion/github-playground:main`.
5. The CI bot checks your profile; after review it gets merged — and the roster page below rebuilds automatically.

## The rules (enforced by CI)

The workflow in `.github/workflows/ci.yml` runs `scripts/check_profiles.py` on every PR. The strict per-PR rules apply **only to PRs from `docs/*` branches**, and are skipped for maintainers (maintain/admin permission) and the `PROFILE_BYPASS` list in the workflow:

- a profile PR must change **exactly one file**, and it must be **`profiles/<your-github-username>.md`** — named after the PR author's own login, newly added (not modifying someone else's file);
- the file needs at least 20 characters of content, starting with a `# Title` line;
- files beginning with `_` are templates and are ignored;
- anything else in the PR (extra files, wrong name, existing file) fails the check.

**`docs/*` PRs that pass are merged automatically** — CI squash-merges them within seconds, no human clicking needed. Maintainer PRs from other branches are merged manually. A merge rebuilds the roster page below.

## The roster page

<https://comppsyunion.github.io/github-playground/> — one card per profile, avatars straight from `github.com/<username>.png`.

Two ways this page is served:

- **Upstream (automatic):** Pages source is set to *GitHub Actions* — every merge to `main` makes CI build and deploy the site directly. Nothing to click, ever.
- **Your fork (manual, classroom exercise):** `docs/index.html` is also committed to the repo, so in your own fork you can go to **Settings → Pages → Deploy from a branch → `main` / `/docs`** and get your own copy of the site.
