---
name: test-web
description: Run Playwright E2E tests to verify that web app changes work correctly in a real browser. Use this skill whenever changes are pushed to a test branch, after editing front-end files (HTML, CSS, JS, TS), when the user asks to test or verify changes, or when a hook triggers it after git push. Also use it when the user says "test", "verify", "check if it works", "run tests", or "testear". Repo-agnostic: it discovers the repo's test-user setup by convention.
allowed-tools: Bash(npx playwright *), Bash(node *), Bash(env), Read, Glob, Grep, Write, Edit
argument-hint: [test-filter]
---

# Test Web — Playwright E2E Testing

Run end-to-end browser tests to verify that changes to a web app work correctly.

## How it works

This skill creates **ephemeral tests** specific to what changed, runs them in a real browser via Playwright, and cleans up when they pass. This avoids accumulating obsolete tests.

The skill is **repo-agnostic**: it does not assume any particular set of user roles. It discovers the repo's test users from the environment by convention (Step 0), then drives whatever auth/projects that repo defines. Some repos have many user types (e.g. one per role/department); others have a single user or no auth at all. Adapt to what you find — don't hardcode role names from memory.

## Workflow

### Step 0: Discover the repo's test setup

Before anything else, learn how *this* repo authenticates and names its Playwright projects. Two sources of truth — read both, don't assume:

```bash
cd "$(git rev-parse --show-toplevel)"
# Pick the web project dir if the repo is a monorepo (e.g. ./domus-hub). Otherwise use the root.

# 1. Which test users exist? Convention: each TEST_<ROLE>_EMAIL env var declares a
#    test user whose role is <role> (the suffix, lowercased). The password is shared
#    across roles in TEST_USER_PASSWORD (a role may override with TEST_<ROLE>_PASSWORD).
env | grep -E '^TEST_[A-Z0-9_]*_EMAIL=' | sed -E 's/=.*//' | sort
env | grep -q '^TEST_USER_PASSWORD=' && echo "shared password present"

# 2. How are those roles wired into Playwright? Read the config rather than guessing
#    project names — they follow the convention setup-<role> / <role>-tests / shared-tests,
#    but the config is the source of truth.
ls playwright*.config.* 2>/dev/null
```

What the convention means in practice:
- `TEST_DIRECCION_EMAIL` → role `direccion` → projects `setup-direccion` and `direccion-tests`; role-specific specs are named `direccion.*.spec.ts`.
- A repo with a single user typically exposes `TEST_USER_EMAIL` + `TEST_USER_PASSWORD` (role `user`), or has no auth at all.
- `shared.*.spec.ts` are role-agnostic specs that run under the repo's **primary role** (the highest-visibility user; configurable via `PLAYWRIGHT_PRIMARY_ROLE`, e.g. `direccion` in Domus Hub).

If `env` shows no `TEST_*_EMAIL` vars and the config has no auth setup, the app is unauthenticated — skip all the role/auth machinery below and just run the tests.

### Step 1: Understand what changed

Figure out what actually changed so the tests target real behavior instead of guesses. Prefer uncommitted work — that's usually what you're iterating on — and fall back to committed changes only when the tree is clean.

```bash
# Uncommitted changes first (staged + unstaged + untracked). Quote the globs so
# git matches them recursively across subdirectories — an unquoted *.js expands
# in the shell and only catches files in the current directory.
git status --porcelain -- '*.js' '*.html' '*.css' '*.ts'

# If nothing is uncommitted, diff the commits on this branch against the repo's
# deploy/base branch (not HEAD~1, which misses everything beyond the last commit).
# Find the base branch from the config/remote; in Domus Hub it is `cambios-en-produccion`.
# Fall back to `git diff HEAD~1` if the base branch isn't available locally.
git diff --name-only <base-branch>...HEAD -- '*.js' '*.html' '*.css' '*.ts'
```

If `$ARGUMENTS` was provided, use it as a test filter (e.g., a specific test file name or keyword) and skip the diff detection.

Then read the changed files to understand what the change is supposed to do — don't infer intent from filenames alone.

**Before creating or running any tests, tell the user in 1-2 sentences what you're about to test, and wait for their confirmation.** For example: *"I see changes to the report modal's date filter. I'll verify the modal opens, the range applies, and the task list updates. Sound right?"* Realigning now is cheap; discovering a misunderstanding after writing and running a full suite is expensive.

### Step 2: Create targeted tests

First, ground yourself in the real test setup instead of working from memory:

- **Read `tests/helpers.ts`** (or the repo's equivalent) to see which helpers actually exist and their exact signatures before you call them. Helpers get renamed or added over time — the file is the source of truth.
- **Pull selectors from the source, not from memory.** Grep the changed HTML/JS and a couple of existing tests under `tests/` for the IDs/classes you need. Hardcoded selectors go stale the moment the markup changes; the code does not.

Then create Playwright test files in `tests/temp/`. Each test should:

- Target the specific UI changes found in the diff
- Reuse the real helpers from the repo's helpers file
- Follow the patterns in existing tests under `tests/` for selector naming and modal interaction
- Be read-only by default (don't create/modify real data unless explicitly told to)
- **Name the file so it maps to the right project (this is enforced by the config's `testMatch`):**
  - Role-agnostic checks → `tests/temp/shared.verify-[feature].spec.ts` (runs as the primary role).
  - Behavior specific to one role/permission → `tests/temp/<role>.verify-[feature].spec.ts` (runs as that role). Use a role discovered in Step 0.
  - Without a matching prefix the test won't be picked up by any project.

### Step 3: Run the tests

First make sure the environment is actually ready — most "test failures" at this stage are really setup problems, and they're faster to rule out up front than to debug from a cryptic Playwright error:

```bash
# Browsers installed? (no-op if already present)
npx playwright install --with-deps chromium

# Port free? The config usually auto-starts a server (commonly :3000); a stale
# process will make every test fail to connect. Kill it if something is squatting it.
lsof -ti:3000 || echo "port free"

# Auth state present? If tests/.auth/<role>.json is missing or stale, the
# setup-<role> project regenerates it — but it needs the credentials in .env.
ls tests/.auth/ 2>/dev/null || echo "no auth yet — setup project will create it"
```

If `npx playwright install` or the auth setup fails, fix that before running tests — don't try to interpret downstream failures. A common auth failure is a missing `TEST_<ROLE>_EMAIL` / `TEST_USER_PASSWORD` — re-check Step 0.

Force the JSON reporter via CLI so the results file always exists, regardless of what the config sets. `--reporter=line,json` keeps console progress visible *and* writes the file; `PLAYWRIGHT_JSON_OUTPUT_NAME` controls where it lands (Step 4 reads exactly this path):

```bash
export PLAYWRIGHT_JSON_OUTPUT_NAME=test-results/results.json

# Role-agnostic checks (primary role). The shared-tests project's setup dependency
# authenticates automatically — no need to list it separately.
npx playwright test tests/temp/ --project=shared-tests --reporter=line,json
```

**Only run a role-specific block when the change touches role/permission behavior** — e.g. the diff mentions permission flags, role checks, or anything gated by the user's role. There's no point paying for a second auth + run when the change is role-agnostic. When it *is* relevant, run the temp test under the restricted role to verify it behaves correctly (e.g. a non-privileged user can view but not edit):

```bash
# <role> is one discovered in Step 0; the temp file is tests/temp/<role>.verify-*.spec.ts.
# The <role>-tests project's setup-<role> dependency authenticates automatically.
npx playwright test tests/temp/ --project=<role>-tests --reporter=line,json
```

### Step 4: Read and report results

Read `test-results/results.json` and present a summary table:

| Test | Status | Duration |
|------|--------|----------|
| verify-feature-name | PASS | 3.2s |

If there are failures, for each one:
1. Read the screenshot: `test-results/*/test-failed-1.png`
2. Read the error context: `test-results/*/error-context.md`
3. Explain what failed and why
4. **Diagnose where the bug actually is before touching anything.** A failure can come from two sources, and they're fixed differently:
   - **The app code is wrong** — the feature genuinely misbehaves (wrong value rendered, broken permission gate, missing element that should exist). Fix the app code.
   - **The test is wrong** — a stale selector, a race the test didn't wait for, an assertion that doesn't match correct behavior, or the wrong role for the assertion. Fix the test.
   The screenshot is the tiebreaker: if the app looks/behaves correctly but the test still failed, the test is at fault. Don't "fix" working app code to satisfy a broken test, and don't weaken a test to paper over a real app bug.
5. Apply the fix and re-run. You may edit app code directly without asking — *unless* the fix is destructive or hard to reverse (deleting code paths, schema/migration changes, touching auth or other tests). In that case, stop and confirm with the user first.
6. **Cap the loop at 3 fix attempts.** If the tests still fail after the third attempt, stop — don't keep changing code. Report what you tried, the current failure, and your best hypothesis, and hand back to the user.

### Step 5: Clean up and push

**Only run this step once all tests actually pass.** Stopping after the 3-attempt cap in Step 4 is *not* a finish line — it's a pause to fix the underlying problem and re-test. In that case do **not** clean up or push: leave `tests/temp/` in place so the failure can be reproduced and debugged, and hand back to the user.

When everything is green:

1. **Delete the `tests/temp/` directory.** The temp tests are scaffolding — they are never committed.
2. **Commit only the app-code fix, if any.** If a fix in Step 4 changed application code, commit *that* change with a clear message describing the fix. Never stage anything under `tests/temp/`. If no app code changed (tests passed on the first run), there's nothing to commit — just report success.
3. **Decide where to push based on the environment:**
   - **Claude Code on the web / cloud:** always start a *new* branch and open a pull request for the fix — never push directly. (This matches the always-new-PR workflow configured for cloud sessions.)
   - **Local / anywhere else:** ask the user which branch to push to before pushing. Do not assume a production-looking branch.

## Important notes

- **Test users are discovered by convention, not hardcoded.** `TEST_<ROLE>_EMAIL` + shared `TEST_USER_PASSWORD` define them; the Playwright config turns each into `setup-<role>` / `<role>-tests` projects automatically. Adding a user is just adding an env var — never edit the config to add a role.
- The Playwright config usually auto-starts a local server (commonly port 3000) and tests run against it, not a deployed URL.
- Auth credentials live in `.env` (gitignored); session storage states land in `tests/.auth/<role>.json` (gitignored).
- Data often loads asynchronously — use the repo's `waitForDataLoad()` (or equivalent) helper rather than fixed sleeps.
- **Repo-specific facts must be re-verified each run** (they drift): the primary role, which permission flags gate which UI, modal/close behavior, and exact selectors. For Domus Hub at time of writing: primary role is `direccion`; permissions follow a 2D `departamento × rango` model in `public/permissions.js` (e.g. `editFechaFinProgramada` is true for `direccion`/`*_gerente`, false for supervisors); modals are `#modal-overlay.open` and close via overlay click (no Escape handler); the deploy/base branch is `cambios-en-produccion`.
