# Migu 脚手架项目开发指南

## 项目定位

migu 是脚手架项目，用于快速搭建 LLM-WIKI 知识库。

**注意**：
- 这是脚手架本身，不是知识库。目标是生产工具，而非直接使用。
- 本 AGENTS.md 是项目级（指导脚手架开发）。
- `rules/*/AGENTS.md` 是知识库级（安装到知识库后指导使用）。

## 概念区分

- **rules**：定义知识库 schema（目录结构、命名规范）
- **skills**：操作知识库（ingest、compile、lint 等）

## 主要目录

```
migu/           # CLI 代码（typer 命令）
skills/         # 知识库操作 skills（minimal/history）
rules/          # 知识库规则定义（minimal/history）
tests/          # pytest 测试
docs/superpowers/specs/  # 设计文档
```

## 技术栈

- Python 3.11+
- uv（包管理，替代 pip）
- typer（CLI 框架）
- pytest（测试）

## 工作原则

- **简单优先**：最小代码解决问题。不做未请求的功能、抽象或配置。
- **手术式变更**：只触碰必要代码。不重构不相关代码，匹配现有风格。

## 开发命令

```bash
uv sync                      # 安装依赖
uv run pytest                # 运行测试
uv run pytest tests/test_init.py -v  # 单文件测试
uv run migu init my-kb       # 运行 CLI
```

## 分阶段实现

项目按依赖顺序分阶段：

| 阶段 | 内容 | 产出验证 |
|------|------|---------|
| **阶段 1** | CLI init + rules minimal | `migu init my-kb` 创建知识库骨架 |
| **阶段 2** | CLI skill 命令 | `migu skill list/install/uninstall/reinstall` 可安装 skills |
| **阶段 3** | Skills minimal（6 个） | kb-ingest/compile/lint/query/archive/status 可运行 |
| **阶段 4** | history 定制 | `migu init my-kb --rules history` |

阶段 1 可独立完成并验证。阶段 2 完成后，可使用 `migu skill install` 测试 skills 效果。

## Skills 结构

每个 skill 包含：
- `SKILL.md`：agent 指令文件
- `scripts/`：辅助脚本
- `references/`：参考文档

## 安装分发配置

pyproject.toml 必须包含：

```toml
[project.scripts]
migu = "migu.cli:app"
```

支持 pipx 和 uv tool 安装。

## Spec 文档

开发前阅读：
- `docs/superpowers/specs/2026-04-17-migu-scaffold-design.md`（架构层）
- `docs/superpowers/specs/2026-04-21-skills-implementation-guide.md`（实现层）
