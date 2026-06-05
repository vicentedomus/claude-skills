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

## Maintain the README skills index

`README.md` carries a table of every skill in the repo. **Whenever a skill is
added, renamed, or removed, update that table in the same PR** — don't leave it
for later. For each new skill, the row should include:

- The skill name linked to its folder (e.g. `[battlemap](battlemap/)`)
- A **one-line purpose**, distilled from the skill's `SKILL.md` frontmatter
  `description` (don't paste the full description — trim to one readable line)
- Any **cross-skill dependency** worth flagging (e.g. `halo-session-prep`
  requires `dnd-worldbuilder` installed alongside)
- Any MCP server the skill requires, if non-obvious

This applies regardless of how the skill arrived: migrated from another
location, installed via `npx skills`, or written from scratch in this repo.
Keep the table alphabetical for easy scanning.

## skills-lock.json

Managed automatically by `npx skills`. Do not edit manually.
