# Migu 脚手架项目开发指南

## 项目定位

migu 是脚手架项目，用于快速搭建 LLM-WIKI 知识库。
**注意**：这是脚手架本身，不是知识库。目标是生产工具，而非直接使用。

## 目录结构

```
migu/
├── migu/           # CLI 代码（typer 命令）
├── skills/         # 知识库操作 skills（minimal/history）
├── rules/          # 知识库规则定义（minimal/history）
├── tests/          # pytest 测试
└── docs/superpowers/specs/  # 设计文档
```

## 技术栈

- Python 3.11+
- uv（包管理）
- typer（CLI 框架）
- rich（终端输出）
- pytest（测试）

## 开发命令

```bash
uv sync                      # 安装依赖
uv run pytest                # 运行测试
uv run pytest tests/test_init.py -v  # 单文件测试
uv run migu init my-kb       # 开发时运行 CLI
```

## 安装分发

支持两种方式：

```bash
# pipx（推荐给已有 pipx 的用户）
pipx install migu
pipx install git+https://github.com/xxx/migu.git

# uv tool（推荐给使用 uv 的用户）
uv tool install migu
uv tool install git+https://github.com/xxx/migu.git
```

需要在 pyproject.toml 配置：

```toml
[project.scripts]
migu = "migu.cli:app"
```

## Skills 结构

每个 skill 包含：
- `SKILL.md`：agent 指令文件
- `scripts/`：辅助脚本
- `references/`：参考文档

## Spec 文档

主要设计文档：
- `docs/superpowers/specs/2026-04-17-migu-scaffold-design.md`：架构层（目录结构、契约边界、CLI 设计）
- `docs/superpowers/specs/2026-04-21-skills-implementation-guide.md`：实现层（各 skill 流程步骤）

开发前先阅读 scaffold-design 理解架构边界。

## 开发流程

使用 superpowers skills：
1. 阅读 spec → 理解架构
2. writing-plans → 创建实施计划
3. subagent-driven-development → 执行计划
4. test-driven-development → TDD 实现
