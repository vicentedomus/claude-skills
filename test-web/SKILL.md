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

Analyze the recent changes to determine what needs testing:

```bash
cd "$(git rev-parse --show-toplevel)/domus-hub" && git diff HEAD~1 --name-only -- *.js *.html *.css
```

If no argument was provided, also check `git diff --cached` and `git status` for uncommitted changes.

If `$ARGUMENTS` was provided, use it as a test filter (e.g., a specific test file name or keyword).

### Step 2: Create targeted tests

Based on the diff, create Playwright test files in `tests/temp/`. Each test should:

- Target specific UI changes found in the diff
- Use existing helpers from `tests/helpers.ts` (waitForDataLoad, switchTab, closeModal)
- Follow the patterns in existing tests under `tests/` for selector naming and modal interaction
- Be read-only by default (don't create/modify real data unless explicitly told to)
- **CRITICAL**: Name files with `shared.` prefix: `tests/temp/shared.verify-[feature].spec.ts` — this is required by the Playwright config's `testMatch` pattern (`/shared\..+\.spec\.ts/`). Without the prefix, tests won't run.

Reference the existing test patterns:
- Auth setup reuses `tests/.auth/maestro.json` (storageState from setup-maestro project)
- Use `#modal-overlay.open` to detect modals
- Use `.tab-btn[data-tab="X"]` to switch tabs
- Report modal is `#modal-reporte-overlay`
- Task rows are in `#tbody-tareas tr`

### Step 3: Run the tests

```bash
cd "$(git rev-parse --show-toplevel)/domus-hub"
npx playwright test tests/temp/ --project=setup-maestro --project=shared-tests
```

If testing role-specific behavior (maestro vs supervisor), also run:
```bash
npx playwright test tests/temp/ --project=setup-supervisor --project=supervisor-tests
```

Also run core tests to make sure nothing broke:
```bash
npx playwright test tests/core/ --project=setup-maestro --project=shared-tests
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
