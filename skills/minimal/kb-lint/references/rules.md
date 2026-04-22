# Lint Rules

## Syntax Rules

| Rule | Description | Severity |
|------|-------------|---------|
| Source field | Every wiki document must have `## 来源` section with `- source: [[raw/...]]` | Error |
| Wikilink balance | All `[[...]]` must have matching opening and closing | Warning |
| Title heading | File must start with `# Title` heading | Warning |

## Semantic Rules

| Rule | Description | Severity |
|------|-------------|---------|
| Template structure | Documents should follow template sections (person, place, event) | Warning |
| Orphan entries | index.md entries must point to existing wiki files | Warning |

## Auto-fixable

| Issue | Fix |
|-------|-----|
| Missing source | Add `## 来源\n- source: [[raw/PENDING]]` |
| Orphan brackets | Remove unmatched `[[` or `]]` |
