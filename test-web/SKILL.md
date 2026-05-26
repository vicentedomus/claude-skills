---
name: test-web
description: Run Playwright E2E tests on Domus Hub to verify that code changes work correctly in a real browser. Use this skill whenever changes are pushed to the test branch, after editing domus-hub files (HTML, CSS, JS), when the user asks to test or verify changes, or when a hook triggers it after git push. Also use it when the user says "test", "verify", "check if it works", "run tests", or "testear".
allowed-tools: Bash(npx playwright *), Bash(node *), Read, Glob, Write, Edit
argument-hint: [test-filter]
---

# Test Web — Playwright E2E Testing for Domus Hub

Run end-to-end browser tests to verify that changes to Domus Hub work correctly.

## How it works

This skill creates **ephemeral tests** specific to what changed, runs them in a real browser via Playwright, and cleans up when they pass. This avoids accumulating obsolete tests.

## Workflow

### Step 1: Understand what changed

Figure out what actually changed so the tests target real behavior instead of guesses. Prefer uncommitted work — that's usually what you're iterating on — and fall back to committed changes only when the tree is clean.

```bash
cd "$(git rev-parse --show-toplevel)/domus-hub"

# Uncommitted changes first (staged + unstaged + untracked). Quote the globs so
# git matches them recursively across subdirectories — an unquoted *.js expands
# in the shell and only catches files in the current directory.
git status --porcelain -- '*.js' '*.html' '*.css' '*.ts'

# If nothing is uncommitted, diff the commits on this branch against the deploy
# branch (not HEAD~1, which misses everything beyond the last commit). Fall back
# to `git diff HEAD~1` if the deploy branch isn't available locally.
git diff --name-only cambios-en-produccion...HEAD -- '*.js' '*.html' '*.css' '*.ts'
```

If `$ARGUMENTS` was provided, use it as a test filter (e.g., a specific test file name or keyword) and skip the diff detection.

Then read the changed files to understand what the change is supposed to do — don't infer intent from filenames alone.

**Before creating or running any tests, tell the user in 1-2 sentences what you're about to test, and wait for their confirmation.** For example: *"I see changes to the report modal's date filter. I'll verify the modal opens, the range applies, and the task list updates. Sound right?"* Realigning now is cheap; discovering a misunderstanding after writing and running a full suite is expensive.

### Step 2: Create targeted tests

First, ground yourself in the real test setup instead of working from memory:

- **Read `tests/helpers.ts`** to see which helpers actually exist and their exact signatures before you call them. The names below are a hint, not a guarantee — the file is the source of truth, and helpers get renamed or added over time.
- **Pull selectors from the source, not from this list.** Grep the changed HTML/JS and a couple of existing tests under `tests/` for the IDs/classes you need (e.g. `grep -rn 'modal-overlay\|tbody-tareas' domus-hub/*.html domus-hub/*.js`). Hardcoded selectors in a skill go stale the moment the markup changes; the code does not.

Then create Playwright test files in `tests/temp/`. Each test should:

- Target the specific UI changes found in the diff
- Reuse the real helpers from `tests/helpers.ts` (at time of writing: `waitForDataLoad`, `switchTab`, `closeModal`)
- Follow the patterns in existing tests under `tests/` for selector naming and modal interaction
- Be read-only by default (don't create/modify real data unless explicitly told to)
- **CRITICAL**: Name files with the `shared.` prefix: `tests/temp/shared.verify-[feature].spec.ts` — this is required by the Playwright config's `testMatch` pattern (`/shared\..+\.spec\.ts/`). Without the prefix, tests won't run.

Selectors that were current at the time of writing (verify against the source before relying on them):
- Auth setup reuses `tests/.auth/maestro.json` (storageState from setup-maestro project)
- `#modal-overlay.open` to detect modals
- `.tab-btn[data-tab="X"]` to switch tabs
- Report modal is `#modal-reporte-overlay`
- Task rows are in `#tbody-tareas tr`

### Step 3: Run the tests

First make sure the environment is actually ready — most "test failures" at this stage are really setup problems, and they're faster to rule out up front than to debug from a cryptic Playwright error:

```bash
cd "$(git rev-parse --show-toplevel)/domus-hub"

# Browsers installed? (no-op if already present)
npx playwright install --with-deps chromium

# Port 3000 free? The config auto-starts a server there; a stale process will
# make every test fail to connect. Kill it if something is squatting the port.
lsof -ti:3000 || echo "port 3000 free"

# Auth state present? If tests/.auth/maestro.json is missing or stale, the
# setup-maestro project regenerates it — but it needs the credentials in .env.
ls tests/.auth/ 2>/dev/null || echo "no auth yet — setup project will create it"
```

If `npx playwright install` or the auth setup fails, fix that before running tests — don't try to interpret downstream failures.

Force the JSON reporter via CLI so the results file always exists, regardless of what `playwright.config.ts` sets. `--reporter=line,json` keeps console progress visible *and* writes the file; `PLAYWRIGHT_JSON_OUTPUT_NAME` controls where it lands (Step 4 reads exactly this path):

```bash
export PLAYWRIGHT_JSON_OUTPUT_NAME=test-results/results.json
npx playwright test tests/temp/ --project=setup-maestro --project=shared-tests --reporter=line,json
```

**Run the supervisor block only when the change touches role/permission behavior** — e.g. the diff mentions `canEdit`, role checks, or anything gated by user role. There's no point paying for a second auth + run when the change is role-agnostic. When it is relevant, verify the restricted role behaves correctly (e.g. a supervisor can view but not edit):

```bash
npx playwright test tests/temp/ --project=setup-supervisor --project=supervisor-tests --reporter=line,json
```

### Step 4: Read and report results

Read `test-results/results.json` and present a summary table:

| Test | Status | Duration |
|------|--------|----------|
| verify-feature-name | PASS | 3.2s |

If there are failures:
1. Read the screenshot: `test-results/*/test-failed-1.png`
2. Read the error context: `test-results/*/error-context.md`
3. Explain what failed and why
4. **Fix the code** (not the test) and re-run
5. Repeat until all tests pass

### Step 5: Clean up and push

Once all tests pass:
1. Delete `tests/temp/` directory
2. Commit the fix (if code was changed)
3. Push to the `cambios-en-produccion` branch

If all tests passed without needing fixes, just clean up tests/temp/ and report success.

## Important notes

- The Playwright config is at `domus-hub/playwright.config.ts` — it auto-starts a local server on port 3000
- Auth credentials are in `.env` (gitignored)
- Use `--project=setup-maestro` to authenticate before running tests
- Tests run against `http://localhost:3000` (local serve), not the Vercel URL
- The app uses Supabase Auth with roles: maestro, gerente, supervisor, proyectos
- `canEdit()` returns true only for maestro role
- Task data loads asynchronously — always use `waitForDataLoad()` from helpers
- Modals close via overlay click (no Escape handler)
