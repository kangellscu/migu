---
version: "1.0"
---
# Knowledge Base Schema (Minimal)

Generic knowledge base schema per Karpathy LLM-WIKI pattern.
Domain-specific types defined in derived rules (history, legal, etc.).

## Directory Structure

- `raw/`: Raw source files (user managed, immutable)
- `raw/.extracted/`: Processed files from kb-ingest
- `raw-registry.md`: Raw file registry (root level)
- `index.md`: Knowledge base index (root level)
- `log.md`: Operation log (root level)
- `wiki/`: LLM-generated structured documents
  - `entities/`: Entity pages
  - `concepts/`: Concept pages
  - `synthesis/`: Analysis pages
- `output/`: User-generated derivative documents

## Wiki Page Types

Per Karpathy LLM-WIKI, wiki contains:
- **Primary pages** (kb-compile): entity pages, concept pages, summaries
- **Analysis pages** (kb-archive): synthesis, comparisons, overview

Entity/concept types are domain-specific. Minimal provides base structure.
Analysis pages stored in wiki/synthesis/, distinguished by frontmatter type:
```
---
type: synthesis | comparison | overview
---
```

kb-archive writes analysis pages directly to wiki/synthesis/.

## Naming Conventions

- Wiki pages: Title case, no file extension in wikilinks. E.g., `[[EntityName]]`
- Raw files: Preserve original naming. E.g., `raw/path/to/file.md`
- Extracted files: Mirror raw structure under `raw/.extracted/`

## Reference Format

Use Obsidian wikilinks:
```
[[PageName]]
```

For file references:
```
[[raw/<your-path>|<display-name>]]
```

Wiki pages must include source field:
```
## 来源
- source: [[raw/path/to/source.md]]
```

## Operations

- kb-ingest: Scan raw/, preprocess, output to raw/.extracted/
- kb-compile: Read files, extract entities/concepts, generate wiki pages
- kb-lint: Check wiki syntax and semantics
- kb-query: Search wiki with optional raw backtracking
- kb-archive: Generate synthesis/comparison/overview, integrate into wiki
- kb-status: Show dashboard