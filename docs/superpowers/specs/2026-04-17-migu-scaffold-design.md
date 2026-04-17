---
title: Migu 脚架项目设计文档
created: 2026-04-17
type: spec
status: draft
version: 1.0
---

# Migu 脚架项目设计文档

## 1. 项目定位

migu 是一个独立的手架项目（Git 管理），用于快速搭建 LLM-WIKI 知识库。

**核心能力：**
- 通过 CLI 在指定目录创建知识库实例
- 提供不同类型的知识库规则（minimal、history）
- 提供知识库操作的 skills（kb-ingest、kb-lint、kb-query）
- 管理知识库实例中的 skills 安装/更新

**用户视角：**
```bash
migu init my-kb --rules history    # 创建历史知识库
migu skill list my-kb              # 查看已安装的 skills
migu skill reinstall kb-ingest my-kb  # 更新某个 skill
```

---

## 2. 目录结构

### 2.1 migu 项目结构

```
migu/                          # 项目根目录（独立仓库）
├── pyproject.toml             # uv 包管理配置
├── README.md                  # 项目文档
├── .python-version            # Python 版本锁定（3.11）
│
├── migu/                      # CLI 代码目录
│   ├── __init__.py            # 版本信息
│   ├── __main__.py            # CLI 入口
│   ├── cli.py                 # typer app 主命令
│   ├── init/                  # init 命令模块
│   │   ├── __init__.py
│   │   ├── creator.py         # 知识库创建逻辑
│   │   └── rules.py           # 规则处理逻辑
│   └── skill/                 # skill 命令模块
│       ├── __init__.py
│       ├── manager.py         # skill 管理逻辑
│       └── installer.py       # skill 安装/卸载逻辑
│
├── skills/                    # 知识库操作 skills（按类型分组）
│   common/                    # 通用 skill 实现
│   │   kb-lint/               # Wiki 检查
│   │   │   SKILL.md           # lint 规则和流程
│   │   │   scripts/           # lint 专属脚本
│   │   │   │   lint.py
│   │   │   │   syntax.py      # 语法检查
│   │   │   │   semantic.py    # 语义检查
│   │   │   │   fix.py         # 自动修复
│   │   │   references/
│   │   │       rules.md
│   │   │
│   │   kb-query/              # Wiki 查询
│   │   │   SKILL.md
│   │   │   references/
│   │   │       intent-patterns.md
│   │   │       templates/
│   │   │
│   │   kb-ingest/             # 最小导入（minimal 规则使用）
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   validate_batch.py
│   │   │   │   generate_pinyin.py
│   │   │   │   detect_kangxi.py
│   │   │   references/
│   │   │       templates/
│   │
│   history/                   # 历史知识库定制
│   │   kb-ingest/             # 历史文档导入
│   │   │   SKILL.md           # 人物/地点/事件提取规则
│   │   │   scripts/
│   │   │   │   validate_batch.py
│   │   │   │   generate_pinyin.py
│   │   │   │   detect_kangxi.py
│   │   │   │   extract_entities.py
│   │   │   references/
│   │   │       templates/
│   │   │       │   common.md
│   │   │       │   person-template.md
│   │   │       │   place-template.md
│   │   │       │   event-template.md
│   │   │       │   institution-template.md
│   │   │       │   synthesis-template.md
│   │   │       entity-patterns.md
│   │
│   scripts/                   # skill 内部共享脚本
│   │   unicode/
│   │   │   normalize.py
│   │   │   kangxi.py
│   │   pinyin/
│   │       generate.py
│
├── rules/                     # 知识库规则定义
│   minimal/                   # 最小结构规则（默认）
│   │   AGENTS.md
│   │   structure.json
│   │   skills.json
│   │
│   history/                   # 历史知识库规则
│   │   AGENTS.md
│   │   structure.json
│   │   skills.json
│
└── tests/                     # 测试用例
    ├── test_cli.py
    ├── test_init.py
    ├── test_skill.py
    ├── integration/
    └── skills/
        ├── test_kb_ingest_common.py
        └── test_kb_ingest_history.py
```

### 2.2 知识库实例结构

```
<target-dir>/                  # 知识库实例
├── AGENTS.md                  # 知识库 schema（从 rules 复制）
├── index.md                   # wiki 文档索引
├── log.md                     # 操作日志
├── raw-registry.md            # raw 文件注册表
│
├── raw/                       # 不可变源文件
│  史记/
│     本纪/
│     列传/
│   ...
│
├── wiki/                      # LLM 维护的文档
│   entities/
│   concepts/
│   synthesis/
│
├── output/                    # 输出产物
│
└── .agents/                   # 程序化文件
    skills/
      kb-ingest/
      kb-lint/
      kb-query/
    skills-lock.json           # skill 版本记录
```

---

## 3. Skills 组织原则

### 3.1 按类型分组

- `skills/common/`：通用 skill（kb-lint、kb-query、kb-ingest）
- `skills/history/`：历史知识库定制（kb-ingest 的历史版本）

### 3.2 职责分离

每个 skill 自包含，职责单一：

| skill | 职责 | scripts |
|-------|------|---------|
| kb-lint | Wiki 检查（语法、语义） | lint.py, syntax.py, semantic.py, fix.py |
| kb-query | Wiki 查询 | 无（依赖 references） |
| kb-ingest | 导入 raw 文件到 wiki | validate_batch.py, generate_pinyin.py, detect_kangxi.py |

**无 shared skill**：共用代码按职责归属到对应 skill，而非创建模糊的共享容器。

### 3.3 common 作为兜底

- `rules/*/skills.json` 配置 skill 来源
- 如果某类型不需要定制，使用 `source: common`
- 如果某类型需要定制，使用 `source: history`（或其他类型）

---

## 4. Rules 规则定义

### 4.1 rules 目录组织

与 skills 目录组织一致：按类型分组。

```
rules/
  minimal/     # 最小知识库规则
  history/     # 历史知识库规则
```

### 4.2 配置文件

#### AGENTS.md

知识库 schema，定义：
- 目录结构
- 命名规范
- 引用格式
- 操作规则

#### structure.json

定义目录结构和初始文件：

```json
{
  "directories": {
    "raw": {},
    "wiki": {
      "entities": {
        "people": {},
        "places": {},
        "events": {}
      },
      "concepts": {
        "institutions": {},
        "ideas": {}
      },
      "synthesis": {}
    },
    "output": {}
  },
  "files": {
    "index.md": {"content": "# Wiki Index\n"},
    "log.md": {"content": "# Knowledge Base Log\n"},
    "raw-registry.md": {"content": "# Raw File Registry\n\n| 文件 | 类型 | 摘要 | 状态 | 编译产物 | 最近处理日期 |\n|------|------|------|------|----------|-------------|\n"}
  }
}
```

#### skills.json

定义安装哪些 skills：

```json
{
  "skills": [
    {
      "name": "kb-ingest",
      "source": "history",
      "version": "1.0"
    },
    {
      "name": "kb-lint",
      "source": "common",
      "version": "1.0"
    },
    {
      "name": "kb-query",
      "source": "common",
      "version": "1.0"
    }
  ]
}
```

minimal 的 skills.json：

```json
{
  "skills": [
    {
      "name": "kb-ingest",
      "source": "common",
      "version": "1.0"
    },
    {
      "name": "kb-lint",
      "source": "common",
      "version": "1.0"
    },
    {
      "name": "kb-query",
      "source": "common",
      "version": "1.0"
    }
  ]
}
```

---

## 5. CLI 命令设计

### 5.1 migu init

```bash
migu init <target-dir> [--rules <rules-name>]
```

**参数：**
- `<target-dir>`：知识库目标目录（必需）
- `--rules`：规则名称（minimal、history），默认 minimal

**执行流程：**
1. 检查 `<target-dir>` 是否存在
2. 创建目录结构（根据 rules/*/structure.json）
3. 复制 rules/*/AGENTS.md → `<target-dir>/AGENTS.md`
4. 安装 skills：
   - 复制 `skills/<source>/<name>` → `<target-dir>/.agents/skills/<name>`
   - 创建 skills-lock.json
5. 创建初始文件（index.md、log.md、raw-registry.md）

**输出示例：**
```
✓ Created knowledge base structure in my-kb/
✓ Generated AGENTS.md (rules: history)
✓ Installed 3 skills: kb-ingest (from history), kb-lint, kb-query
```

### 5.2 migu skill

```bash
migu skill install <skill-name> <target-dir>
migu skill uninstall <skill-name> <target-dir>
migu skill reinstall <skill-name> <target-dir>
migu skill install-all <target-dir>
migu skill reinstall-all <target-dir>
migu skill list <target-dir>
```

**migu skill install：**
- 根据 skills-lock.json 查找 skill 的 source
- 复制 `skills/<source>/<name>` → `<target-dir>/.agents/skills/<name>`
- 更新 skills-lock.json

**migu skill list：**
- 只列出知识库相关的 skills（kb-ingest、kb-lint、kb-query）
- 显示 name、source、version

**输出示例：**
```
Installed skills in my-kb/:
  kb-ingest    ✓ installed (v1.0, from history)
  kb-lint      ✓ installed (v1.0, from common)
  kb-query     ✓ installed (v1.0, from common)
```

### 5.3 版本命令

```bash
migu --version        # 显示版本
migu --help           # 显示帮助
```

---

## 6. 知识库文件

### 6.1 index.md

wiki 文档索引，kb-ingest 创建 wiki 页面时更新。

格式由 AGENTS.md 定义。

### 6.2 log.md

操作日志，每次操作后追加。

格式：`## [YYYY-MM-DD] operation | details`

### 6.3 raw-registry.md

raw 文件注册表，kb-ingest 自动更新。

**表格格式：**

```markdown
# Raw File Registry

| 文件 | 类型 | 摘要 | 状态 | 编译产物 | 最近处理日期 |
|------|------|------|------|----------|-------------|
| [[raw/史记/本纪/高祖本纪.md\|史记·本纪·高祖本纪]] | markdown | 记载刘邦生平及汉朝建立 | 已导入 | [[liu-bang\|刘邦]] | 2026-04-17 |
| [[raw/史记/assets/刘邦画像.png\|刘邦画像]] | image | 刘邦画像（汉代） | 已导入 | [[liu-bang\|刘邦]]（引用） | 2026-04-16 |
| [[raw/史记/本纪/项羽本纪.md\|史记·本纪·项羽本纪]] | markdown | - | 未处理 | - | - |
```

**字段说明：**

| 字段 | 说明 | 示例 |
|------|------|------|
| 文件 | raw 文件路径（wikilink，需转义 `\|`） | `[[raw/史记/本纪/高祖本纪.md\|史记·本纪·高祖本纪]]` |
| 类型 | 文件格式 | markdown、pdf、image |
| 摘要 | 内容摘要（可选） | 记载刘邦生平及汉朝建立 |
| 状态 | 处理状态 | 未处理、已导入、部分导入 |
| 编译产物 | 生成的 wiki 页面 | `[[liu-bang\|刘邦]]` |
| 最近处理日期 | 最后处理时间 | 2026-04-17（未处理时为 `-`） |

### 6.4 skills-lock.json

安装时记录 skill 版本信息：

```json
{
  "rules": "history",
  "installed_at": "2026-04-17T10:00:00",
  "migu_version": "1.0",
  "skills": [
    {
      "name": "kb-ingest",
      "source": "history",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    },
    {
      "name": "kb-lint",
      "source": "common",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    },
    {
      "name": "kb-query",
      "source": "common",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    }
  ]
}
```

---

## 7. kb-ingest 自动更新 raw-registry.md

### 7.1 执行流程

1. **遍历 raw/ 目录**：检测是否有新文件
2. **对比 raw-registry.md**：找出未记录的文件
3. **添加新条目**：
   - 文件：wikilink 格式
   - 类型：根据文件扩展名判断（.md → markdown, .pdf → pdf, .png → image）
   - 摘要：初始为 `-`（待补充）
   - 状态：未处理
   - 编译产物：`-`
   - 最近处理日期：`-`
4. **导入处理**：读取 raw 文件，创建 wiki 页面
5. **更新条目**：
   - 状态：已导入
   - 编译产物：生成的 wiki 页面（wikilink 格式）
   - 最近处理日期：当前日期（YYYY-MM-DD）

### 7.2 状态定义

| 状态 | 说明 |
|------|------|
| 未处理 | raw 文件已添加，但未导入到 wiki |
| 已导入 | raw 文件已导入，wiki 页面已创建 |
| 部分导入 | raw 文件部分导入（如只提取了部分实体） |

### 7.3 类型判断

根据文件扩展名：

| 扩展名 | 类型 |
|--------|------|
| .md | markdown |
| .txt | text |
| .pdf | pdf |
| .png, .jpg, .gif | image |
| 其他 | unknown |

---

## 8. 技术栈

- **Python 3.11+**
- **uv**：包管理和依赖管理
- **typer**：CLI 框架
- **rich**：终端输出格式化

---

## 9. Git 管理

migu 是 Git 管理的独立仓库：
- skills 和 rules 的变更可追溯
- 用户可通过 `git pull` 更新 migu
- migu 版本号与 git tag 对应

---

## 10. 扩展设计

未来可添加：
- 新的 rules 类型（tech、legal 等）
- 新的 skills（kb-export、kb-sync 等）
- migu upgrade 命令（更新 migu 本身）

---

## 11. 关键设计决策

### 11.1 skills 按类型分组（vs 按功能分组）

**选择：按类型分组（common/history）**

理由：
- 与 rules 目录组织一致
- common 作为兜底，减少重复
- 类型专属 skill 可覆盖 common 实现

### 11.2 scripts 放在 skill 内部（vs 根目录）

**选择：放在 skill 内部**

理由：
- skill 自包含，复制即安装
- 无需额外的 scripts.config 配置
- 共用代码按职责归属（validation → kb-lint）

### 11.3 无 shared skill

**选择：按职责划分，不创建 shared skill**

理由：
- shared 违反职责分离原则
- validation 归属 kb-lint（lint 的核心职责）
- kb-ingest 不依赖其他 skill

### 11.4 raw-registry.md 自动维护

**选择：kb-ingest 自动更新**

理由：
- 减少用户维护负担
- 保证信息准确性
- 处理状态可追踪

---

## 12. 文件命名规范

| 文件 | 命名规则 |
|------|----------|
| skill 目录 | `<skill-name>`（无类型后缀） |
| skills.json 配置 | 通过 `source` 字段指定来源 |
| raw-registry.md wikilink | 使用 `\|` 转义符号 |

---

## 13. 约束

- raw/ 目录不可变（用户管理）
- AGENTS.md 可修改（用户定制）
- skills-lock.json 自动维护（不手动修改）
- raw-registry.md 自动维护（kb-ingest 更新）