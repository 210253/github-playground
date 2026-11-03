# github-playground

The hands-on playground for the CPU weekly session **GitHub Beyond the Code** — everyone opens their first pull request here.

## Add yourself (browser only, no install)

1. **Fork** this repository.
2. In your fork, open the `profiles/` directory → **Add file → Create new file** → name it `<your-github-username>.md`.
3. Start with a `# Title` line and write a few lines about yourself (copy `profiles/_template.md` if you like).
4. Commit on a **new branch** named `docs/add-<your-username>` (the commit dialog offers "Create a new branch"), then **Compare & pull request** back to `CompPsyUnion/github-playground:main`.
5. The CI bot checks your profile and squash-merges it automatically — the roster page below rebuilds on merge.

Already merged once? Update your intro on a `fix/<your-username>` branch — same flow, but the PR must modify your own existing file. See [CONTRIBUTING.md](./CONTRIBUTING.md) for the details.

## The rules (enforced by CI)

The workflow in `.github/workflows/ci.yml` runs `scripts/check_profiles.py` on every PR. The strict per-PR rules apply **only to PRs from `docs/*` (first-time add) or `fix/*` (update your own) branches**, and are skipped for maintainers (maintain/admin permission) and the `PROFILE_BYPASS` list in the workflow:

- a profile PR must change **exactly one file**, and it must be **`profiles/<your-github-username>.md`** — named after the PR author's own login (case-sensitive), nobody else's;
- `docs/*` PRs must **add** that file; `fix/*` PRs must **modify** it;
- the file needs at least 20 characters of content, starting with a `# Title` line;
- files beginning with `_` are templates and are ignored;
- anything else in the PR (extra files, wrong name, wrong verb) fails the check.

**`docs/*` and `fix/*` PRs that pass are merged automatically** — CI squash-merges them within seconds, no human clicking needed. Maintainer PRs from other branches are merged manually. A merge rebuilds the roster page below.

## The roster page

<https://comppsyunion.github.io/github-playground/> — one card per profile, avatars straight from `github.com/<username>.png`.
