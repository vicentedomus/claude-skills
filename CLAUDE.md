# claude-skills

This repo stores Claude Code skills for use across sessions.

## Structure

Each skill lives in its own top-level folder named after the skill:

```
<skill-name>/
  SKILL.md        ← required: skill definition loaded by Claude Code
  ...             ← any additional assets, references, scripts
```

Example:
```
test-web/
  SKILL.md
huashu-design/
  SKILL.md
  assets/
  references/
  scripts/
```

## Installing a new skill

```bash
npx skills add <github-owner>/<repo>
```

After installation, if the tool placed the skill under `.agents/skills/<name>/`, move it to the root:

```bash
git mv .agents/skills/<name> <name>
# remove .agents/ if now empty
git rm -r .agents/
```

Commit, push to a branch, open a PR, and merge to main.

## skills-lock.json

Managed automatically by `npx skills`. Do not edit manually.
