---
version: "1.0"
---
# Knowledge Base Schema

## Directory Structure

- `raw/`: Raw source files (user managed, immutable)
- `raw/.extracted/`: Processed files from kb-ingest
- `wiki/`: LLM-generated structured documents
  - `entities/`: Person, place, organization pages
  - `concepts/`: Concept pages
  - `synthesis/`: Analysis and synthesis pages
- `output/`: User-generated derivative documents

## Naming Conventions

- Wiki pages: Title case, no file extension in wikilinks. E.g., `[[刘邦]]`
- Raw files: Preserve original naming structure. E.g., `raw/史记/本纪/高祖本纪.md`
- Extracted files: Mirror raw directory structure under `raw/.extracted/`

## Reference Format

Use Obsidian wikilinks:
```
[[PageName]]
```

For file references:
```
[[raw/<your-path>|<display-name>]]
```

source field in wiki documents:
```
## 来源
- source: [[raw/<your-path>]]
```

## Operations

- kb-ingest: Scan raw/, preprocess, output to raw/.extracted/
- kb-compile: Read extracted files, extract entities, generate wiki pages
- kb-lint: Check wiki syntax and semantics
- kb-query: Search wiki with optional raw backtracking
- kb-archive: Write synthesis reports and integrate back into wiki
- kb-status: Show dashboard (parse index.md + raw-registry.md)
