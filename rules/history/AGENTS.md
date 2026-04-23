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

Use Obsidian wikilinks: `[[Page Name]]`
For file references: `[[raw/path/to/file.md|display name]]`

source field in wiki documents:
## 来源
- source: [[raw/path/to/file.md]]

## Entity Types

### 实体 (entities/)

| 类型 | 模板 | 说明 |
|------|------|------|
| 人物 | person-template.md | 历史人物（皇帝、大臣、学者、将领等） |
| 地点 | place-template.md | 历史地点（都城、郡县、关隘、战场、山川等） |
| 事件 | event-template.md | 历史事件（战争、政变、改革、外交等） |

### 概念 (concepts/)

| 类型 | 模板 | 说明 |
|------|------|------|
| 制度 | institution-template.md | 制度框架（三省六部制、科举制等） |
| 官职 | official-template.md | 具体职位（宰相、尚书、刺史等） |
| 思想 | thought-template.md | 学术思想（儒家、道家、法家等） |

## Operations

- kb-ingest: Scan raw/, preprocess, output to raw/.extracted/
- kb-compile: Read extracted files, extract entities, generate wiki pages
- kb-lint: Check wiki syntax and semantics
- kb-query: Search wiki with optional raw backtracking
- kb-archive: Write synthesis reports and integrate back into wiki
- kb-status: Show dashboard (parse index.md + raw-registry.md)
