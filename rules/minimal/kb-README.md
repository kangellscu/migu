---
version: 1.0
---
# 知识库使用指南

## 知识库是什么

本知识库基于三层架构：

| 层级 | 目录 | 说明 |
|------|------|------|
| **Raw sources** | `raw/` | 你添加的源文件，不可变 |
| **Wiki** | `wiki/` | LLM 生成的结构化文档，可累积 |
| **Schema** | `AGENTS.md` | 告诉 LLM 如何结构化 wiki |

核心理念：wiki 是**持久化可累积产物**——每次 compile 添加新内容，知识库逐渐丰富。

## 目录结构

```
.
├── raw/                # 源文件（你管理）
│   ├── .extracted/     # 预处理产物（自动生成）
│   └── ...             # 你的文件
├── wiki/               # 结构化文档（LLM 生成）
│   ├── entities/       # 实体页面
│   ├── concepts/       # 概念页面
│   └── synthesis/      # 分析页面
├── output/             # 衍生文档（你管理）
├── raw-registry.md     # 文件注册表（自动维护）
├── index.md            # 文档索引（自动维护）
├── log.md              # 操作日志（自动维护）
└── AGENTS.md           # 知识库 schema（可定制）
```

## 快速上手

**Step 1: 添加源文件**

```bash
# 将你的文件放入 raw/ 目录
cp ~/documents/史记-项羽本纪.md raw/
mkdir raw/史记
cp ~/documents/史记-高祖本纪.md raw/史记/
```

**Step 2: 预处理（kb-ingest）**

在知识库目录，触发 skill：
```
kb-ingest
```

Agent 会扫描 raw/，预处理文件，更新 raw-registry.md。

**Step 3: 提取内容（kb-compile）**

触发 skill：
```
kb-compile
```

Agent 会读取文件，提取实体/概念，生成 wiki 页面。

**Step 4: 查看状态**

触发 skill：
```
kb-status
```

查看知识库仪表盘。

## Skills 工作流程

| Skill | 作用 | 触发时机 |
|-------|------|---------|
| **kb-ingest** | 预处理 raw 文件 | 添加新文件后 |
| **kb-compile** | 提取实体/概念，生成 wiki | ingest 后 |
| **kb-lint** | 检查 wiki 语法/语义 | compile 后 |
| **kb-query** | 搜索 wiki，生成报告 | 需要查询时 |
| **kb-archive** | 生成分析页面，回写 wiki | query 后 |
| **kb-status** | 显示知识库状态 | 需要查看时 |

**典型工作流程**：
```
添加 raw 文件 → kb-ingest → kb-compile → kb-lint → kb-query → kb-archive
```

**Skills 使用方式**：Skills 是 agent 指令。在 Claude Code 或类似工具中，直接触发 skill 名称（如 "kb-compile"），agent 会加载指令并执行。

## 使用约束

**✓ 可以修改**：
- `raw/` - 添加、删除你的源文件
- `output/` - 创建衍生文档
- `AGENTS.md` - 定制知识库 schema

**✗ 不要修改**：
- `raw/.extracted/` - kb-ingest 自动维护
- `wiki/` - kb-compile 自动生成
- `raw-registry.md` - skills 自动更新
- `index.md` - skills 自动更新
- `log.md` - skills 自动追加

**违反约束**：可能导致 skills 功能异常。重新运行对应 skill 可恢复。

## 示例：完整流程

```bash
# 1. 添加 raw 文件
mkdir raw/史记
cp ~/documents/史记-项羽本纪.md raw/史记/
cp ~/documents/史记-高祖本纪.md raw/史记/

# 2. 在知识库目录，触发 skills（agent session 中）
kb-ingest      # 预处理
kb-compile     # 提取实体（项羽、刘邦、萧何等）
kb-lint        # 检查 wiki
kb-status      # 查看状态

# 3. 查询知识库
kb-query "刘邦的主要功绩有哪些？"

# 4. 生成分析页面
kb-archive     # 将 query 报告整合到 wiki
```