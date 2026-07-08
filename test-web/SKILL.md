---
name: test-web
description: Run Playwright E2E tests to verify that web app changes work correctly in a real browser. Invoke this skill in exactly two situations, and no others — (1) the user explicitly asks for a web test / test-web / to "testear la web" (or clearly asks to run a browser/E2E test); or (2) Claude has proposed an end-to-end (E2E) browser test and the user agreed to it. Do NOT auto-invoke merely because front-end files (HTML, CSS, JS, TS) were edited, because a branch was pushed, or because a hook fired — a file change or push alone is never a trigger. Repo-agnostic: it discovers the repo's test-user setup by convention.
allowed-tools: Bash(npx playwright *), Bash(node *), Bash(env), Bash(git *), Bash(npm ci), Bash(npm install), Bash(npm run *), Bash(lsof *), Bash(ls *), Bash(cat *), Bash(curl *), Read, Glob, Grep, Write, Edit
argument-hint: [test-filter]
---

# Test Web — Playwright E2E Testing

Run end-to-end browser tests to verify that changes to a web app work correctly.

## How it works

This skill creates **ephemeral tests** specific to what changed, runs them in a real browser via Playwright, and **always deletes them** when done — pass or fail-then-fixed. Tests are never graduated to a permanent suite; the repo keeps no `.spec.ts` that this skill authored. This keeps every run targeted and avoids accumulating obsolete tests.

**The only thing that persists between runs are gotchas** — hard-won facts that make future runs faster. They come in **two tiers** (see "Sistema de gotchas en dos niveles" below): general environment gotchas that ship with the skill, and repo-specific gotchas that live in the consuming repo. The skill reads both at the start (Step 0) and proposes saving newly-discovered ones at the end (Step 5).

The skill is **repo-agnostic**: it does not assume any particular set of user roles. It discovers the repo's test users from the environment by convention (Step 0), then drives whatever auth/projects that repo defines. Some repos have many user types (e.g. one per role/department); others have a single user or no auth at all. Adapt to what you find — don't hardcode role names from memory.

## Sistema de gotchas en dos niveles

Un *gotcha* es un hecho no-obvio que costó descubrir y que acelera (o desbloquea) las próximas corridas. Se guardan en dos lugares según su alcance:

1. **Gotchas generales del entorno** → [`references/gotchas.md`](references/gotchas.md), **parte de la skill**. Aplican a cualquier repo detrás del proxy de Claude Code on the web (cert MITM, browser no ruteado por el proxy CONNECT-only, static-vs-bundler, versión de Chromium). Ya están documentados ahí; consúltalos cuando el entorno falle, y **añade uno nuevo** solo si es genuinamente general (no específico de un repo).
2. **Gotchas específicos del repo** → `tests/QA-NOTES.md` **en el repo consumidor** (no en esta skill). Cosas que solo valen para *ese* repo: rol primario, qué permisos gatean qué UI, selectores y comportamiento de modales, branch base/deploy, qué deps CDN carga, el nombre de su knob TLS. La skill **lee este archivo en el Paso 0** y **propone añadirle** lo que aprenda en el Paso 5. Si no existe, lo crea al guardar el primer gotcha.

Regla para clasificar: *"¿esto sería cierto en otro repo detrás del mismo proxy?"* Sí → general (skill). No, solo aplica a este repo → `tests/QA-NOTES.md`.

## Workflow

### Step 0: Discover the repo's test setup and read the gotchas

**First, read both gotcha sources** — they may already answer the exact problem you're about to hit, saving a full debug cycle:

```bash
cd "$(git rev-parse --show-toplevel)"
# 1. General environment gotchas (ship with the skill): proxy/TLS/bundler/Chromium.
#    Path is relative to the skill's install dir (e.g. .claude/skills/test-web/).
#    If you can't resolve it, they're summarized in Step 3 and "Important notes".
cat references/gotchas.md 2>/dev/null || echo "read the skill's references/gotchas.md"

# 2. Repo-specific gotchas (live in the consuming repo). Absent on first-ever run.
cat tests/QA-NOTES.md 2>/dev/null || echo "no repo gotchas yet — Step 5 will offer to create it"
```

Treat what you find as the current truth, but **re-verify repo-specific facts each run** — they drift (see Step 5 on keeping `tests/QA-NOTES.md` honest).

Then learn how *this* repo authenticates and names its Playwright projects. Two sources of truth — read both, don't assume:

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

**Derive tests from the expected behavior, not just the diff.** The diff tells you *what* lines changed; QA cares about *what the change should guarantee*. State the **acceptance criterion** in one sentence (infer it from the change, the PR/issue, or ask the user if it's ambiguous) — e.g. *"a supervisor can open the report but the date field is read-only"*. Each test in Step 2 verifies a criterion, so a green run maps to a satisfied requirement rather than just "the code ran".

**Before creating or running any tests, tell the user in 1-2 sentences what you're about to test, and wait for their confirmation.** For example: *"I see changes to the report modal's date filter. I'll verify the modal opens, the range applies, and the task list updates. Sound right?"* Realigning now is cheap; discovering a misunderstanding after writing and running a full suite is expensive.

### Step 2: Create targeted tests

First, ground yourself in the real test setup instead of working from memory:

- **Read `tests/helpers.ts`** (or the repo's equivalent) to see which helpers actually exist and their exact signatures before you call them. Helpers get renamed or added over time — the file is the source of truth.
- **Pull selectors from the source, not from memory.** Grep the changed HTML/JS and a couple of existing tests under `tests/` for the IDs/classes you need. Hardcoded selectors go stale the moment the markup changes; the code does not.

Then create Playwright test files in `tests/temp/`. Each test should:

- Target the specific UI changes found in the diff
- **Name the test after the acceptance criterion it verifies, not the feature** — e.g. `test('AC: supervisor sees the date field read-only', …)`. A failing test then names the broken guarantee, not just a file.
- Reuse the real helpers from the repo's helpers file
- Follow the patterns in existing tests under `tests/` for selector naming and modal interaction
- **Cover the relevant negative / edge case, not only the happy path.** When the change has a meaningful failure mode, add at least one case for it: invalid input rejected, a denied permission actually blocked, an empty/zero state rendered correctly. The happy path proves it *can* work; the negative case proves it *fails safely*.
- **Be read-only by default** (don't create/modify real data unless explicitly told to). When a test *must* mutate data, it has to be self-cleaning so it doesn't pollute the shared environment: use identifiable test data (a fixed prefix + timestamp, e.g. `qa-temp-<ts>`), delete what it created in `afterEach`/`afterAll`, and stay idempotent so a re-run starts from a clean slate.
- **Name the file so it maps to the right project (this is enforced by the config's `testMatch`):**
  - Role-agnostic checks → `tests/temp/shared.verify-[feature].spec.ts` (runs as the primary role).
  - Behavior specific to one role/permission → `tests/temp/<role>.verify-[feature].spec.ts` (runs as that role). Use a role discovered in Step 0.
  - Without a matching prefix the test won't be picked up by any project.

### Step 3: Run the tests

First make sure the environment is actually ready — most "test failures" at this stage are really setup problems, and they're faster to rule out up front than to debug from a cryptic Playwright error:

```bash
# Dependencies installed? A fresh clone — especially Claude Code on the web, which
# clones clean every session — has no node_modules, so Playwright can't even load
# the config and dies with "Cannot find module '@playwright/test'". Install first.
[ -d node_modules ] || npm ci || npm install

# Browsers installed? (no-op if already present). ORDER MATTERS: install npm deps
# *before* this. Deps pin the Playwright version; installing the browser first and
# then running `npm ci` swaps Playwright to a different version whose browser build
# is now missing ("Executable doesn't exist at .../chrome-headless-shell-XXXX").
npx playwright install --with-deps chromium

# Port free? The config usually auto-starts a server (commonly :3000); a stale
# process will make every test fail to connect. Kill it if something is squatting it.
lsof -ti:3000 || echo "port free"

# Auth state present? If tests/.auth/<role>.json is missing or stale, the
# setup-<role> project regenerates it — but it needs the credentials in .env.
ls tests/.auth/ 2>/dev/null || echo "no auth yet — setup project will create it"
```

If `npx playwright install` or the auth setup fails, fix that before running tests — don't try to interpret downstream failures. A common auth failure is a missing `TEST_<ROLE>_EMAIL` / `TEST_USER_PASSWORD` — re-check Step 0.

**If the environment itself blocks the app from booting** — the `setup-<role>` project hangs on a *hidden* `#login-form` / a stuck splash, or a failure screenshot shows the app rendered but `#app.visible` timed out — it's almost never bad credentials. It's one of the general environment gotchas, all diagnosed by symptom in [`references/gotchas.md`](references/gotchas.md):

- **`ERR_CERT_AUTHORITY_INVALID` / `<lib> is not defined` in the console** → CDN deps fail cert validation behind the MITM proxy (gotcha 1). Fix: the repo's TLS knob (`export PLAYWRIGHT_IGNORE_TLS=1`) or the helper below.
- **`ERR_CONNECTION_CLOSED` for CDN/backend hosts *even with* TLS-ignore** → the browser isn't routed through the CONNECT-only proxy (gotcha 2). Fix: drop in [`assets/playwright.remote-env.ts`](assets/playwright.remote-env.ts) and wire it into the config (below); it's the same fix every repo behind this proxy needs, and it also covers the Chromium version-mismatch (gotcha 4).
- **App fully rendered but both `#app.visible` and `#login-form` time out, with 404s for `/config.js`-style paths or a `video/mp2t` MIME error** → a static `webServer` can't boot a bundler app (gotcha 3). Fix: start the repo's real bundler preview yourself and let `reuseExistingServer: true` adopt it.

```ts
// Wiring for assets/playwright.remote-env.ts (gated by detection — no-op in local/CI):
import { ignoreTLS, remoteLaunchOptions } from './playwright.remote-env';
// ...
use: {
  ignoreHTTPSErrors: ignoreTLS,
  launchOptions: { ...(remoteLaunchOptions() || {}) },
},
```

Read `references/gotchas.md` for the full symptom→cause→fix of each, plus what *looks* like the fix but doesn't work. Also check the repo's `tests/QA-NOTES.md` — a past run may have already recorded which of these this repo needs.

Force the JSON reporter via CLI so the results file always exists, regardless of what the config sets. `--reporter=line,json` keeps console progress visible *and* writes the file; `PLAYWRIGHT_JSON_OUTPUT_NAME` controls where it lands (Step 4 reads exactly this path). Two more flags pull their weight on every run:

- `--trace=retain-on-failure --video=retain-on-failure` — keep a full **trace** (DOM snapshots, network, console) and a **video** only for tests that fail. The trace viewer is the single fastest way to see *why* an E2E broke, far beyond a lone screenshot, and "on-failure" keeps green runs cheap.
- `--retries=2` — re-run a failing test up to twice. This is how QA separates a **real failure** (fails every time) from a **flaky** one (passes on retry). It does not paper over bugs: a test that only passes on retry is reported as flaky in Step 4, not as clean green.

```bash
export PLAYWRIGHT_JSON_OUTPUT_NAME=test-results/results.json

# Role-agnostic checks (primary role). The shared-tests project's setup dependency
# authenticates automatically — no need to list it separately.
npx playwright test tests/temp/ --project=shared-tests \
  --reporter=line,json --trace=retain-on-failure --video=retain-on-failure --retries=2
```

**Only run a role-specific block when the change touches role/permission behavior** — e.g. the diff mentions permission flags, role checks, or anything gated by the user's role. There's no point paying for a second auth + run when the change is role-agnostic. When it *is* relevant, run the temp test under the restricted role to verify it behaves correctly (e.g. a non-privileged user can view but not edit):

```bash
# <role> is one discovered in Step 0; the temp file is tests/temp/<role>.verify-*.spec.ts.
# The <role>-tests project's setup-<role> dependency authenticates automatically.
npx playwright test tests/temp/ --project=<role>-tests \
  --reporter=line,json --trace=retain-on-failure --video=retain-on-failure --retries=2
```

### Step 4: Read and report results

Read `test-results/results.json` and present a summary table. Use the JSON's per-test `status`/`retries` to tell a clean pass from a flaky one — a test whose final result is `passed` but that has a non-empty retry history **passed only on retry** and must be reported as **FLAKY**, not PASS:

| Test | Status | Duration |
|------|--------|----------|
| AC: range filter updates list | PASS | 3.2s |
| AC: supervisor cannot edit date | FLAKY (passed on retry 2) | 8.1s |

A flaky test is not a green light: it points at a race or unstable selector. Note it for the user and stabilize it if it's cheap. A test that only passes on retry hasn't verified its acceptance criterion deterministically — treat the criterion as unproven until the test is stable.

If there are failures, for each one:
1. Read the screenshot: `test-results/*/test-failed-1.png`
2. Read the error context: `test-results/*/error-context.md`
3. Open the trace for the full picture when the screenshot isn't enough: `npx playwright show-trace test-results/*/trace.zip` (DOM snapshots, network, console timeline) — the fastest way to pinpoint *where* an E2E broke.
4. Explain what failed and why
5. **Diagnose where the bug actually is before touching anything.** A failure can come from two sources, and they're fixed differently:
   - **The app code is wrong** — the feature genuinely misbehaves (wrong value rendered, broken permission gate, missing element that should exist). Fix the app code.
   - **The test is wrong** — a stale selector, a race the test didn't wait for, an assertion that doesn't match correct behavior, or the wrong role for the assertion. Fix the test.
   The screenshot/trace is the tiebreaker: if the app looks/behaves correctly but the test still failed, the test is at fault. Don't "fix" working app code to satisfy a broken test, and don't weaken a test to paper over a real app bug.
6. Apply the fix and re-run. You may edit app code directly without asking — *unless* the fix is destructive or hard to reverse (deleting code paths, schema/migration changes, touching auth or other tests). In that case, stop and confirm with the user first.
7. **Cap the loop at 3 fix attempts.** If the tests still fail after the third attempt, stop — don't keep changing code. Report what you tried, the current failure, and your best hypothesis, and hand back to the user.

### Step 5: Save gotchas, clean up, and push

**Only run this step once all tests actually pass.** Stopping after the 3-attempt cap in Step 4 is *not* a finish line — it's a pause to fix the underlying problem and re-test. In that case do **not** clean up or push: leave `tests/temp/` in place so the failure can be reproduced and debugged, and hand back to the user.

When everything is green:

1. **Propose saving any gotcha you learned this run — this is the skill's memory, and the only thing that persists.** Since no tests are kept, gotchas are how the *next* run gets faster. If during this run you discovered a non-obvious fact — the exact selector for a modal, which permission flag gates a UI element, the primary role, the base/deploy branch, which CDN deps this app loads, the name of the repo's TLS knob, an async-load quirk — offer to record it. Classify it first (see "Sistema de gotchas en dos niveles"):
   - **Repo-specific** (true only for this repo) → append it to `tests/QA-NOTES.md` in the consuming repo. Create the file if it doesn't exist (a short Markdown doc, grouped by topic: roles, permissions, selectors, server/build, environment). Keep entries terse and factual; if a note contradicts what you re-verified this run, **update it rather than stacking a second version** — stale gotchas are worse than none.
   - **General environment** (would be true for any repo behind this proxy) → these are rare and usually already in the skill's `references/gotchas.md`. Only if you hit a genuinely new one, tell the user it belongs in the skill itself (a change to `test-web/references/gotchas.md`), not in the repo — don't silently write repo-local notes for it.

   Default to offering; let the user confirm before writing. A run that discovered nothing new saves nothing — that's fine.
2. **Delete everything under `tests/temp/`.** Every test this skill wrote is scaffolding and is never committed or graduated — remove the directory so nothing under `tests/temp/` is ever staged. The repo keeps no `.spec.ts` authored by this skill.
3. **Commit the app-code fix and any gotcha note.** If a fix in Step 4 changed application code, commit *that* with a clear message describing the fix; include the `tests/QA-NOTES.md` update from (1) in the same commit (or its own commit if there was no code fix). Never stage anything under `tests/temp/`. If nothing changed and no gotcha was recorded (tests passed on the first run), there's nothing to commit — just report success.
4. **Decide where to push based on the environment:**
   - **Claude Code on the web / cloud:** always start a *new* branch and open a pull request for the fix — never push directly. (This matches the always-new-PR workflow configured for cloud sessions.)
   - **Local / anywhere else:** ask the user which branch to push to before pushing. Do not assume a production-looking branch.

## Important notes

- **E2E is the tip of the testing pyramid — reach for it last, not first.** Browser tests are the slowest and most fragile rung; they earn their cost only when verifying a real UI flow end to end. If the change is pure logic (a calculation, a formatter, a permission predicate, a data transform), a unit or integration test pins it faster and more reliably — prefer pushing the verification down to that level and reserve this skill for behavior that genuinely needs a rendered browser.
- **Test users are discovered by convention, not hardcoded.** `TEST_<ROLE>_EMAIL` + shared `TEST_USER_PASSWORD` define them; the Playwright config turns each into `setup-<role>` / `<role>-tests` projects automatically. Adding a user is just adding an env var — never edit the config to add a role.
- The Playwright config usually auto-starts a local server (commonly port 3000) and tests run against it, not a deployed URL.
- **Remote-env proxy routing (Claude Code on the web).** If the app loads CDN deps or calls an external backend from the browser, and you see `ERR_CONNECTION_CLOSED` (even with TLS-ignore) so the app never boots, the browser isn't routed through the env's CONNECT-only proxy. Drop in `assets/playwright.remote-env.ts` and wire it into the config (see Step 3 and [`references/gotchas.md`](references/gotchas.md), gotcha 2). It's gated by detection, so it's safe to leave committed — a no-op in local/CI. This supersedes setting `PLAYWRIGHT_IGNORE_TLS` by hand: the helper autodetects the proxy and also pins `executablePath` to the pre-installed Chromium.
- Auth credentials live in `.env` (gitignored); session storage states land in `tests/.auth/<role>.json` (gitignored).
- Data often loads asynchronously — use the repo's `waitForDataLoad()` (or equivalent) helper rather than fixed sleeps.
- **Repo-specific facts live in the repo's `tests/QA-NOTES.md`, not in this skill, and must be re-verified each run** (they drift): the primary role, which permission flags gate which UI, modal/close behavior, exact selectors, the base/deploy branch, which TLS knob the repo uses. Read that file in Step 0 and keep it honest in Step 5 — don't memorize these facts here. *Example of what a repo's `QA-NOTES.md` might hold* (Domus Hub, illustrative — verify against the live repo): primary role `direccion`; permissions follow a 2D `departamento × rango` model in `public/permissions.js` (e.g. `editFechaFinProgramada` true for `direccion`/`*_gerente`, false for supervisors); modals are `#modal-overlay.open`, close via overlay click (no Escape handler); deploy/base branch `cambios-en-produccion`; run `npm ci` before `npx playwright install` and `export PLAYWRIGHT_IGNORE_TLS=1` so CDN `<script>` deps don't fail cert validation behind the MITM proxy.
