---
title: README.md 设计文档
created: 2026-04-27
type: spec
status: draft
version: 1.0
last_updated: 2026-04-27
changes: Initial design for README.md
---

# README.md 设计文档

> **受众声明**：本 spec 服务于 README.md 的实现者（脚手架开发者）。
>
> **核心理念**：README.md 面向知识库使用者，提供快速上手和基本信息，详细文档链接到 docs/ 目录。

---

## 1. 设计目标

### 1.1 目标受众

README.md 的主要受众是**知识库使用者**（使用 migu 命令创建和管理知识库的用户）。

其他角色的文档：
- 脚手架开发者：docs/contributing/
- 知识库开发者：docs/knowledge-base-dev/

README.md 链接到这些文档，不包含详细内容。

### 1.2 核心内容

README.md 包含：
- 快速上手
- 项目介绍
- 命令文档（概览）
- 使用约束
- 文档链接

### 1.3 长度和详细程度

**长度**：精简版（200-400 行）

理由：
- pyproject.toml 中 readme = "README.md"，过长影响 PyPI 显示
- README 面向快速上手，详细文档在 docs/
- 精简版更容易维护和更新

**命令文档**：概览形式（表格），链接到详细文档 docs/cli-reference.md

---

## 2. 结构设计

### 2.1 结构方案

采用**经典结构**（方案 A）：

```markdown
# migu

CLI scaffolder for LLM-WIKI knowledge bases.

## Installation
[安装命令]

## Quick Start
[完整示例]

## What is migu?
[项目介绍]

## Commands Overview
[命令概览表格]

## Constraints
[使用约束]

## Documentation
[文档链接]

## Contributing
[贡献者链接]
```

**推荐理由**：
- 符合开源项目 README 的常见结构，用户熟悉
- 平衡理解（项目介绍）、实践（安装+示例）、参考（命令概览）、提醒（约束）
- 符合用户从了解到使用的认知流程

### 2.2 各部分详细设计

#### Section 1: 标题和描述

```markdown
# migu

CLI scaffolder for LLM-WIKI knowledge bases.
```

**设计要点**：
- 标题简洁：`# migu`
- 一行描述：说明 migu 是什么
- 与 pyproject.toml description 一致

#### Section 2: Installation

```markdown
## Installation

Install with uv or pipx:

```bash
# uv (recommended)
uv tool install migu

# pipx
pipx install migu
```

Verify installation:

```bash
migu --version
```
```

**设计要点**：
- 提供 uv（推荐）和 pipx 两种安装方式
- uv 是项目的包管理工具，推荐一致
- 包含验证安装的命令

#### Section 3: Quick Start

```markdown
## Quick Start

Create a knowledge base and add raw files:

```bash
# Create knowledge base
migu init my-kb --rules minimal

# Add raw files (user managed)
cp ~/documents/史记-项羽本纪.md my-kb/raw/
mkdir my-kb/raw/史记
cp ~/documents/史记-高祖本纪.md my-kb/raw/史记/

# View installed skills
cd my-kb
migu skill list
```

Use skills to process your knowledge base:

```bash
# In knowledge base directory, trigger skills:
# kb-ingest   - Preprocess raw files
# kb-compile  - Extract entities, generate wiki pages
# kb-lint     - Check wiki consistency
# kb-query    - Query wiki and generate reports
# kb-archive  - Synthesize reports back to wiki
# kb-status   - Show knowledge base dashboard
```

**Note**: Skills are agent instructions. Trigger skill name in your agent session (e.g., "kb-compile" in Claude Code or similar tools).
```

**设计要点**：
- 包含完整的创建知识库流程（migu init、添加 raw 文件、migu status）
- 列出 6 个 skills 及简要说明
- 强调 skills 是 agent 指令，需要在 agent session 中触发
- 不展示完整的 skill 执行过程（避免过长）

#### Section 4: What is migu?

```markdown
## What is migu?

migu is a CLI scaffolder for creating LLM-WIKI knowledge bases. It provides:

- **Rules**: Define knowledge base schema (directory structure, naming conventions)
- **Skills**: Agent instructions for operating knowledge bases (ingest, compile, lint, query, archive, status)

**Key distinction**:

- migu is the scaffolder (produces tools), not the knowledge base (consumes tools)
- Knowledge bases are created with `migu init`, then managed by users

**Architecture** (Karpathy LLM-WIKI):

| Layer | migu Correspondence | Description |
|-------|--------------------|-------------|
| Raw sources | `raw/` directory | User-managed source files, immutable |
| Wiki | `wiki/` directory | LLM-generated structured documents |
| Schema | `AGENTS.md` + Skills | Instructions for LLM to structure wiki |

**Available rules**:

- `minimal`: Basic structure for general knowledge bases
- `history`: Customized for historical document knowledge bases

**See detailed architecture**: [docs/superpowers/specs/2026-04-17-migu-scaffold-design.md](docs/superpowers/specs/2026-04-17-migu-scaffold-design.md)
```

**设计要点**：
- 解释 migu 的定位（脚手架 vs 知识库）
- 与 Karpathy LLM-WIKI 三层架构对应
- 列出可用的 rules（minimal、history）
- 链接到详细架构文档

#### Section 5: Commands Overview

```markdown
## Commands Overview

### migu CLI commands

| Command | Description |
|---------|-------------|
| `migu init <dir> [--rules <name>]` | Create knowledge base with specified rules |
| `migu skill list <dir>` | List installed skills and versions |
| `migu skill install <name> <dir>` | Install skill to knowledge base |
| `migu skill uninstall <name> <dir>` | Remove skill from knowledge base |
| `migu skill reinstall <name> <dir>` | Reinstall skill (update or restore) |
| `migu rules list <dir>` | Check rules configuration versions |
| `migu --version` | Show version |
| `migu --help` | Show help |

### Knowledge base skills

| Skill | Description |
|-------|-------------|
| `kb-ingest` | Preprocess raw files (scan, normalize, convert PDF) |
| `kb-compile` | Extract entities, generate wiki pages (LLM-driven) |
| `kb-lint` | Check wiki consistency (syntax, semantic, fix) |
| `kb-query` | Query wiki and generate reports (standard + backtrack mode) |
| `kb-archive` | Synthesize reports, write back to wiki |
| `kb-status` | Show knowledge base dashboard |

**See detailed commands**: [docs/cli-reference.md](docs/cli-reference.md)
```

**设计要点**：
- 表格形式，简洁明了
- 分为两部分：migu CLI 命令、知识库 skills
- 每个命令一行简要描述
- 链接到详细命令文档 docs/cli-reference.md

#### Section 6: Constraints

```markdown
## Constraints

Knowledge base users should follow these constraints:

**Immutable (user managed)**:
- `raw/` directory: Source files, never modified by skills
- `output/` directory: Derived documents, user-managed

**Auto-maintained (do not edit)**:
- `raw/.extracted/` directory: kb-ingest preprocessing outputs
- `raw-registry.md`: Raw file registry (kb-ingest/kb-compile update)
- `skills-lock.json`: Skill version records

**Editable (user customizable)**:
- `AGENTS.md`: Knowledge base schema (copied from rules, can modify)

**Note**: Violating constraints may cause migu skills to malfunction. Re-run corresponding skill to restore.

**See detailed constraints**: [docs/knowledge-base-dev/constraints.md](docs/knowledge-base-dev/constraints.md)
```

**设计要点**：
- 分类列出：Immutable、Auto-maintained、Editable
- 每个类别清晰说明管理方
- 提醒违反约束的影响和恢复方式
- 链接到详细约束文档 docs/knowledge-base-dev/constraints.md

#### Section 7: Documentation

```markdown
## Documentation

**For knowledge base users** (this README covers basics):
- [docs/knowledge-base-dev/](docs/knowledge-base-dev/) - Customizing knowledge bases
- [docs/cli-reference.md](docs/cli-reference.md) - Detailed CLI commands

**For scaffold developers**:
- [docs/contributing/](docs/contributing/) - Contributing to migu

**For knowledge base developers**:
- [docs/knowledge-base-dev/](docs/knowledge-base-dev/) - Creating rules and skills

**Technical specs**:
- [docs/superpowers/specs/](docs/superpowers/specs/) - Design documents
```

**设计要点**：
- 按角色分类链接（知识库用户、脚手架开发者、知识库开发者）
- 链接到技术 specs 目录
- 强调 README 覆盖基础知识，详细文档在 docs/

#### Section 8: Contributing

```markdown
## Contributing

Interested in contributing to migu? See:

- [docs/contributing/](docs/contributing/) - Development guide, architecture, testing
```

**设计要点**：
- 简洁的链接到 docs/contributing/ 目录
- 不重复内容（详细内容在 docs/contributing/）

---

## 3. 需要创建的文档文件

README.md 链接到以下文档文件（需要在实现时创建）：

| 文件路径 | 用途 | 优先级 |
|---------|------|--------|
| docs/cli-reference.md | 详细 CLI 命令文档 | 高 |
| docs/knowledge-base-dev/constraints.md | 详细约束文档 | 高 |
| docs/contributing/README.md | 脚手架开发者指南 | 中 |
| docs/knowledge-base-dev/README.md | 知识库开发者指南 | 中 |

---

## 4. 长度预估

README.md 预估长度：

| Section | 行数 |
|---------|------|
| 标题和描述 | 3 |
| Installation | 15 |
| Quick Start | 30 |
| What is migu? | 25 |
| Commands Overview | 30 |
| Constraints | 25 |
| Documentation | 15 |
| Contributing | 5 |
| **总计** | **143-153 行** |

加上空白行和分隔符，预估 **250-350 行**，符合精简版目标。

---

## 5. 设计要点总结

**角色分离**：README 面向知识库使用者，其他角色文档在 docs/

**内容精简**：提供快速上手和基本信息，详细文档链接到 docs/

**表格概览**：命令和 skills 使用表格形式，简洁明了

**示例完整**：Quick Start 包含完整的知识库创建流程

**约束提醒**：分类列出使用约束，提醒违反约束的影响

**文档组织**：按角色分离目录（docs/contributing/、docs/knowledge-base-dev/）

---

## 6. 实现约束

**文件路径**：README.md（项目根目录）

**文件命名**：README.md（pyproject.toml 中 readme = "README.md"）

**格式规范**：使用 Markdown 格式，符合 CommonMark 规范

**链接规范**：相对路径链接，确保本地和 PyPI 都可用

---

## 附录：设计决策

### A.1 为什么选择经典结构？

理由：
- 符合开源项目 README 的常见结构，用户熟悉
- 平衡理解（项目介绍）、实践（安装+示例）、参考（命令概览）、提醒（约束）
- 符合用户从了解到使用的认知流程

### A.2 为什么命令文档使用概览形式？

理由：
- README 长度控制（200-400 行）
- 命令概览适合快速参考
- 详细命令文档在 docs/cli-reference.md

### A.3 为什么按角色分离文档目录？

理由：
- 不同角色有不同的信息需求
- 目录方式可以添加更多文件（架构、测试、扩展）
- 与现有 docs/superpowers/ 结构一致