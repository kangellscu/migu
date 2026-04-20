---
title: Migu 脚架项目设计文档
created: 2026-04-17
type: spec
status: draft
version: 2.0
---

# Migu 脚架项目设计文档

## 1. 项目定位

migu 是一个独立的脚手架项目（Git 管理），用于快速搭建 LLM-WIKI 知识库。

**核心能力：**
- 通过 CLI 在指定目录创建知识库实例
- 提供不同类型的知识库规则（minimal、history）
- 提供知识库操作的 skills（kb-ingest、kb-compile、kb-lint、kb-query、kb-archive、kb-status）
- 管理知识库实例中的 skills 安装/更新

**用户视角：**
```bash
migu init my-kb --rules history    # 创建历史知识库
migu skill list my-kb              # 查看已安装的 skills
migu skill reinstall kb-compile my-kb  # 更新某个 skill
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
│       ├── installer.py       # skill 安装/卸载逻辑
│       └── version_checker.py # 版本检测逻辑
│
├── skills/                    # 知识库操作 skills（按类型分组）
│   minimal/                   # 基础 skill 实现
│   │   kb-ingest/             # 预处理
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   scan_raw.py
│   │   │   │   validate_batch.py
│   │   │   │   normalize_markdown.py
│   │   │   │   convert_pdf.py
│   │   │   references/
│   │   │       templates/
│   │   │
│   │   kb-compile/            # 编译（完全 LLM）
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   read_file.py       # 根据产物路径读取文件
│   │   │   │   update_registry.py # 更新 raw-registry.md
│   │   │   references/
│   │   │       templates/         # 约束 wiki 输出格式
│   │   │       │   person-template.md
│   │   │       │   place-template.md
│   │   │       │   event-template.md
│   │   │
│   │   kb-lint/               # Wiki 检查
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   lint.py
│   │   │   │   syntax.py
│   │   │   │   semantic.py
│   │   │   │   fix.py
│   │   │   references/
│   │   │       rules.md
│   │   │
│   │   kb-query/              # Wiki 查询（含回溯模式）
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   search_wiki.py     # 搜索 wiki 目录
│   │   │   references/
│   │   │       intent-patterns.md # 查询意图模式 + 回溯关键词
│   │   │       templates/
│   │   │       │   report-template.md  # report 输出模板
│   │   │
│   │   kb-archive/            # 回写（有机融入）
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   read_report.py     # 读取 report
│   │   │   │   create_synthesis.py # 创建 synthesis 文件
│   │   │   │   update_entity.py   # 有机融入回写
│   │   │   references/
│   │   │       templates/
│   │   │       │   synthesis-template.md # synthesis 报告模板
│   │   │
│   │   kb-status/             # 仪表盘
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   read_registry.py    # 解析 raw-registry.md
│   │   │   │   read_index.py      # 解析 index.md
│   │   │   │   format_dashboard.py # 格式化仪表盘输出
│   │
│   history/                   # 历史知识库定制
│   │   kb-compile/            # 历史文档编译（完全 LLM）
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   read_file.py       # 根据产物路径读取文件
│   │   │   │   update_registry.py # 更新 raw-registry.md
│   │   │   references/
│   │   │       templates/         # 历史文档定制模板
│   │   │       │   person-template.md
│   │   │       │   place-template.md
│   │   │       │   event-template.md
│   │   │       │   institution-template.md
│   │   │       │   synthesis-template.md
│   │   │       entity-patterns.md
│
├── rules/                     # 知识库规则定义
│   minimal/                   # 基础结构规则（完整）
│   │   AGENTS.md
│   │   structure.json
│   │   skills.json
│   │   templates/
│   │       index.md
│   │       log.md
│   │       raw-registry.md
│   │
│   history/                   # 历史知识库规则（继承 + 覆盖 minimal）
│   │   AGENTS.md              # 覆盖
│   │   skills.json            # 完整覆盖
│   │   # structure.json → 继承 minimal
│   │   templates/
│   │       index.md           # 覆盖（如有差异）
│   │       # log.md → 继承 minimal
│   │       # raw-registry.md → 继承 minimal
│
└── tests/                     # 测试用例
    ├── test_cli.py
    ├── test_init.py
    ├── test_skill.py
    ├── integration/
    └── skills/
        ├── test_kb_ingest.py
        ├── test_kb_compile.py
        └── test_kb_status.py
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
│   .extracted/                # kb-ingest 处理后的文件
│   │   史记/
│   │     本纪/
│   │       高祖本纪.md         # 规范化后的 markdown
│   │       项羽本纪.md
│   │   某书/
│   │     chapter1.md          # PDF 转换的 markdown
│   │     images/
│   │       fig1.png           # PDF 提取的图片
│   史记/
│     本纪/
│       高祖本纪.md             # 原始 markdown
│     assets/
│       刘邦画像.png            # 原始图片（不处理）
│   某书/
│     chapter1.pdf             # 原始 PDF
│
├── wiki/                      # kb-compile 生成的文档
│   entities/
│   concepts/
│   synthesis/
│
├── output/                    # 输出产物
│
└── .agents/                   # 程序化文件
    skills/
      kb-ingest/
      kb-compile/
      kb-lint/
      kb-query/
      kb-archive/
      kb-status/
    skills-lock.json           # skill 版本记录
```

---

## 3. Skills 组织原则

### 3.1 按类型分组

- `skills/minimal/`：基础 skill 实现（kb-ingest、kb-compile、kb-lint、kb-query、kb-archive、kb-status）
- `skills/history/`：历史知识库定制（kb-compile 的历史版本）

### 3.2 技能执行模型

每个 skill 是 **agent 指令包**：

- **SKILL.md**：agent 加载的上下文指令，定义操作流程和规则
- **scripts/**：辅助工具，agent 可按需调用执行具体任务
- **references/**：参考文档、模板、模式定义

**调用方式：** 用户触发技能名称（如"kb-ingest"），agent 加载对应 SKILL.md 获得指令，按流程执行并适时调用 scripts。

### 3.3 职责分离与自包含

每个 skill 完全自包含，职责单一：

| skill | 职责 | scripts |
|-------|------|---------|
| kb-ingest | 扫描 raw/、预处理文件、输出到 raw/.extracted/ | scan_raw.py, validate_batch.py, normalize_markdown.py, convert_pdf.py |
| kb-compile | 读取文件、提取实体、生成 wiki 页面（完全 LLM） | read_file.py, update_registry.py |
| kb-lint | Wiki 检查（语法、语义、修复） | lint.py, syntax.py, semantic.py, fix.py |
| kb-query | Wiki 查询 + 回溯模式 + 生成 report | search_wiki.py |
| kb-archive | 接收 report + 回写摘要 + 有机融入 | read_report.py, create_synthesis.py, update_entity.py |
| kb-status | 展示知识库仪表盘（解析 index.md + raw-registry.md） | read_registry.py, read_index.py, format_dashboard.py |

**无依赖关系**：各 skill 独立运作。kb-ingest 输出是 kb-compile 输入，但无声明依赖，用户手动编排顺序。

### 3.4 minimal 作为基础

- minimal 规则使用 `source: minimal`（所有 skill）
- history 规则对 kb-compile 使用 `source: history`，其他 skill 使用 `source: minimal`
- kb-ingest 只有 minimal 版本（预处理逻辑通用）

---

## 4. Rules 规则定义

### 4.1 rules 目录组织

采用"基础 + 覆盖"模式：

- **minimal**：基础规则，包含完整配置
- **其他规则**：继承 minimal，只包含差异文件

```
rules/
  minimal/                   # 基础知识库规则（完整）
    AGENTS.md
    structure.json
    skills.json
    templates/
      index.md
      log.md
      raw-registry.md

  history/                   # 历史知识库规则（继承 + 覆盖）
    AGENTS.md                # 覆盖
    skills.json              # 完整覆盖
    templates/
      index.md               # 覆盖（如有差异）
```

### 4.2 配置文件

#### AGENTS.md

知识库 schema，定义：
- 目录结构
- 命名规范
- 引用格式
- 操作规则

#### structure.json

定义目录结构：

```json
{
  "directories": {
    "raw": {
      ".extracted": {}
    },
    "wiki": {
      "entities": {},
      "concepts": {},
      "synthesis": {}
    },
    "output": {}
  }
}
```

**使用时机：**

| 阶段 | 是否使用 | 说明 |
|------|---------|------|
| migu init | ✓ 使用 | 创建知识库目录结构 |
| kb-compile | ✗ 不使用 | 目录已存在，实体类型→目录映射由 SKILL.md 定义 |

**隐含约束：**

structure.json wiki 目录结构需与 kb-compile SKILL.md 实体类型→目录映射一致。rules 设计者需确保三者匹配：
- structure.json wiki 目录
- kb-compile SKILL.md 映射
- index.md sections

#### templates/

存放初始文件的内容模板，migu init 复制到知识库根目录。

**templates/index.md：**

```markdown
# Wiki Index

<!-- 
entry format: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD
sections 对应 structure.json wiki 目录结构
-->

<!-- 以下 section 由 migu init 根据 structure.json 动态生成 -->
```

migu init 根据 structure.json wiki 目录动态生成 sections，每个 section 添加 entry 注释。

**templates/log.md：**

```markdown
# Knowledge Base Log

<!-- 
entry format: ## [YYYY-MM-DD] operation | details
operation: ingest | compile | archive | lint
query 和 status 不记录
-->

<!-- 操作日志由 kb-ingest/compile/archive/lint 自动追加 -->
```

**templates/raw-registry.md：**

```markdown
# Raw File Registry

<!-- 
entry format: | 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |

字段格式说明：
- 文件：wikilink 格式，如 [[raw/史记/本纪/高祖本纪.md\|史记·本纪·高祖本纪]]
- 类型：markdown | pdf | image
- 摘要：内容简述，可选
- 预处理状态：未处理 | 已处理 | 无需处理
- 产物路径：相对路径（以知识库根目录为 root），如 raw/.extracted/史记/本纪/高祖本纪.md；无产物时为 `-`
- 编译状态：未编译 | 已编译 | 部分编译 | 已引用
- 最近处理日期：YYYY-MM-DD 格式，未处理时为 `-`
-->

| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
```

**entry format 注释作用：**

| 作用 | 说明 |
|------|------|
| LLM 理解格式 | kb-compile/archive 创建 entry 时参考注释模板 |
| 格式一致性 | 所有 entry 符合统一格式 |
| 字段说明 | 明确每个字段的格式和可选值 |

不同规则可通过覆盖模板定制初始内容。

#### skills.json

定义安装哪些 skills：

**minimal 的 skills.json：**

```json
{
  "skills": [
    {
      "name": "kb-ingest",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-compile",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-lint",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-query",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-archive",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-status",
      "source": "minimal",
      "version": "1.0"
    }
  ]
}
```

**history 的 skills.json：**

```json
{
  "skills": [
    {
      "name": "kb-ingest",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-compile",
      "source": "history",
      "version": "1.0"
    },
    {
      "name": "kb-lint",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-query",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-archive",
      "source": "minimal",
      "version": "1.0"
    },
    {
      "name": "kb-status",
      "source": "minimal",
      "version": "1.0"
    }
  ]
}
```

### 4.3 继承规则

非 minimal 规则继承 minimal 的配置，只覆盖差异部分：

| 文件/目录 | 继承行为 |
|----------|---------|
| AGENTS.md | 存在则覆盖，不存在则继承 minimal |
| skills.json | 存在则完整覆盖（需包含全部 skills 配置），不存在则继承 minimal |
| structure.json | 存在则覆盖，不存在则继承 minimal |
| templates/*.md | 同名文件覆盖，不存在则继承 minimal/templates/ 对应文件 |

**继承示例：**

history 规则只需要定制 kb-compile 的实体提取模板，因此：
- AGENTS.md：覆盖（schema 不同）
- skills.json：完整覆盖（kb-compile source 不同）
- structure.json：不提供，继承 minimal（目录结构相同）
- templates/index.md：覆盖（索引格式可能不同）
- templates/log.md：不提供，继承 minimal
- templates/raw-registry.md：不提供，继承 minimal

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
2. 合并配置（继承 minimal + 覆盖指定 rules）：
   - structure.json：minimal 为基础，rules 覆盖
   - AGENTS.md：minimal 为基础，rules 覆盖
   - skills.json：minimal 为基础，rules 完整覆盖
3. 创建目录结构（根据合并后的 structure.json）
4. 创建 `raw/.extracted/` 目录结构
5. 安装 skills（根据合并后的 skills.json）：
   - 复制 `skills/<source>/<name>` → `<target-dir>/.agents/skills/<name>`
   - 创建 skills-lock.json
6. 复制模板文件（继承 minimal/templates + 覆盖 rules/templates）：
   - log.md：直接复制模板
   - raw-registry.md：直接复制模板
   - index.md：动态生成
     - 复制 templates/index.md 头部注释
     - 根据 structure.json wiki 目录动态生成 sections
     - 每个 section 添加 entry 注释

**输出示例：**
```
✓ Created knowledge base structure in my-kb/
✓ Generated AGENTS.md (rules: history)
✓ Created raw/.extracted/ directory
✓ Installed 6 skills: kb-ingest, kb-compile (from history), kb-lint, kb-query, kb-archive, kb-status
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

**migu skill reinstall：**

执行流程：
1. 查找 skill 的 source（从 skills-lock.json）
2. 检测目标 skill 目录是否有用户修改（对比 migu 捆绑版本）
3. 如有修改，显示 diff 并询问：
   ```
   kb-compile has local modifications:
   
   --- SKILL.md
   +++ SKILL.md (migu v1.3)
   @@ -12,7 +12,7 @@
   - 提取实体时优先匹配人物关系
   + 提取实体时优先匹配人物关系和地点关联
   
   --- references/templates/person-template.md
   +++ references/templates/person-template.md (migu v1.3)
   @@ -5,3 +5,5 @@
   + ## 相关地点
   + 
   
   Reinstall will overwrite these changes.
   Continue? (y/n/abort)
   ```
4. 用户选择：
   - `y`：覆盖，继续 reinstall
   - `n`：跳过该 skill，继续处理其他
   - `abort`：中止整个 reinstall 操作
5. 复制最新版本，更新 skills-lock.json

**migu skill list：**

- 列出已安装 skills（name、source、version）
- 对比 migu 捆绑版本与 skills-lock.json 记录版本
- 显示版本状态：✓ latest 或 ⚠ outdated (可升级)

**输出示例：**
```
Installed skills in my-kb/:
  kb-ingest     ✓ installed (v1.0, from minimal) ✓ latest
  kb-compile    ✓ installed (v1.2, from history) ⚠ outdated (migu v1.3)
  kb-lint       ✓ installed (v1.0, from minimal) ✓ latest
  kb-query      ✓ installed (v1.0, from minimal) ✓ latest
  kb-archive    ✓ installed (v1.0, from minimal) ✓ latest
  kb-status     ✓ installed (v1.0, from minimal) ✓ latest

Run 'migu skill reinstall <name>' to upgrade outdated skills.
```

### 5.3 版本命令

```bash
migu --version        # 显示版本
migu --help           # 显示帮助
```

---

## 6. 知识库文件

### 6.1 index.md

wiki 文档索引，kb-compile 创建 wiki 页面时更新，kb-archive 创建报告时更新。

**生成方式：**

| 阶段 | 操作 |
|------|------|
| migu init | 根据 structure.json wiki 目录动态生成 sections |
| kb-compile | 创建 wiki 页面后，在对应 section 添加 entry |
| kb-archive | 创建 synthesis 报告后，在 synthesis section 添加 entry |

**格式示例：**

```markdown
# Wiki Index

<!-- 
entry format: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD
sections 对应 structure.json wiki 目录结构
-->

## entities
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->
- [[刘邦]] | 汉朝开国皇帝，沛县出身 | 更新: 2026-04-18
- [[萧何]] | 汉初丞相，推荐刘邦 | 更新: 2026-04-17

## concepts
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->
- [[沛县]] | 刘邦故乡，江苏北部 | 更新: 2026-04-17

## synthesis
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->
- [[刘邦关系网络]] | 刘邦核心社交关系分析 | 更新: 2026-04-19
```

**字段说明：**

| 字段 | 格式 | 说明 |
|------|------|------|
| section名 | 与 structure.json wiki 子目录名对应 | migu init 动态生成 |
| 文档名 | wikilink | 链接到 wiki 文档 |
| brief | 简短摘要 | kb-compile/archive 生成 |
| 更新时间 | YYYY-MM-DD | 最近修改时间（非创建时间） |

**隐含约束：**

index.md sections 与 structure.json wiki 目录结构一致。kb-status 解析 index.md 获取 wiki 统计信息，无需扫描 wiki 目录。

### 6.2 log.md

操作日志，每次操作后追加。

**entry format：**

```markdown
## [YYYY-MM-DD] operation | details
```

**operation 标准值：**

| operation | 说明 | 是否记录 |
|-----------|------|---------|
| ingest | 预处理 raw 文件 | ✓ 记录 |
| compile | 编译生成 wiki | ✓ 记录 |
| archive | 创建 synthesis + 回写 | ✓ 记录 |
| lint | Wiki 检查 | ✓（有修复时记录） |
| query | Wiki 查询 | ✗ 不记录 |
| status | 展示仪表盘 | ✗ 不记录 |

**格式示例：**

```markdown
# Knowledge Base Log

## [2026-04-17] ingest | 处理 raw/史记/本纪/*.md，共 5 个文件

## [2026-04-17] compile | 编译 raw/史记/本纪/高祖本纪.md → wiki/entities/刘邦.md

## [2026-04-18] archive | 创建 synthesis/刘邦关系网络.md，回写 [[萧何]]、[[曹参]]
```

### 6.3 raw-registry.md

raw 文件注册表，kb-ingest 和 kb-compile 共同维护。

**表格格式：**

```markdown
# Raw File Registry

| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
| [[raw/史记/本纪/高祖本纪.md\|史记·本纪·高祖本纪]] | markdown | 记载刘邦生平及汉朝建立 | 已处理 | raw/.extracted/史记/本纪/高祖本纪.md | 已编译 | 2026-04-17 |
| [[raw/史记/本纪/项羽本纪.md\|史记·本纪·项羽本纪]] | markdown | - | 已处理 | - | 未编译 | - |
| [[raw/史记/assets/刘邦画像.png\|刘邦画像]] | image | 刘邦画像（汉代） | 无需处理 | - | 已引用 | 2026-04-16 |
| [[raw/某书/chapter1.pdf\|某书·第一章]] | pdf | - | 已处理 | raw/.extracted/某书/chapter1.md | 未编译 | 2026-04-17 |
```

**字段说明：**

| 字段 | 说明 | 更新者 |
|------|------|--------|
| 文件 | raw 文件路径（wikilink） | kb-ingest |
| 类型 | 文件格式（markdown、pdf、image） | kb-ingest |
| 摘要 | 内容摘要（可选） | kb-ingest |
| 预处理状态 | kb-ingest 处理状态 | kb-ingest |
| 产物路径 | 主产物路径（有产物时记录，无产物时为 `-`） | kb-ingest |
| 编译状态 | kb-compile 编译状态 | kb-compile |
| 最近处理日期 | 最后处理时间 | kb-ingest/kb-compile |

**状态定义：**

| 预处理状态 | 说明 | 产物路径 |
|-----------|------|---------|
| 未处理 | raw 文件已添加，kb-ingest 未执行 | `-` |
| 已处理 | 已预处理，可能有产物 | 有产物时记录路径，无产物时 `-` |
| 无需处理 | image 文件，直接引用 | `-` |

| 编译状态 | 说明 |
|---------|------|
| 未编译 | kb-compile 未执行 |
| 已编译 | wiki 页面已生成 |
| 部分编译 | 部分实体已提取，未完成 |
| 已引用 | image 文件被 wiki 页面引用 |

### 6.4 wiki 文档格式

wiki 文档由 kb-compile 生成，存放在 `wiki/` 目录下。

**标准结构：**

```markdown
# 刘邦

## 基本信息
- 别名：高祖、沛公、刘季
- 出生地：[[沛丰邑中阳里]]
- 父亲：[[刘太公]]
- 母亲：[[刘媪]]

## 生平
...

## 相关事件
- [[陈涉起义]]
- [[楚汉之争]]

## 来源
source: [[raw/史记/本纪/高祖本纪.md]]
```

**source 字段规范：**

| 规则 | 说明 |
|------|------|
| 必须包含 | 每个 wiki 文档必须有 source 字段 |
| 指向 raw | 指向原始 raw 文件（原始出处），而非 .extracted/ 产物 |
| wikilink 格式 | 便于 Obsidian 导航 |
| 回溯依赖 | kb-query 回溯模式通过此字段定位 raw 文件 |

### 6.5 skills-lock.json

安装时记录 skill 版本信息：

```json
{
  "rules": "history",
  "installed_at": "2026-04-17T10:00:00",
  "migu_version": "1.0",
  "skills": [
    {
      "name": "kb-ingest",
      "source": "minimal",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    },
    {
      "name": "kb-compile",
      "source": "history",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    },
    {
      "name": "kb-lint",
      "source": "minimal",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    },
    {
      "name": "kb-query",
      "source": "minimal",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    },
    {
      "name": "kb-archive",
      "source": "minimal",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    },
    {
      "name": "kb-status",
      "source": "minimal",
      "version": "1.0",
      "installed_at": "2026-04-17T10:00:00"
    }
  ]
}
```

---

## 7. kb-ingest 执行流程

### 7.1 流程步骤

1. **扫描 raw/ 目录**：检测所有文件（递归）
2. **对比 raw-registry.md**：找出未记录的文件，添加新条目（预处理状态：未处理）
3. **处理文件**：
   - markdown：
     - 无需预处理：标记为"已处理"，产物路径 `-`
     - 需预处理（编码修复/图片下载）：调用 normalize_markdown.py → 输出到 `raw/.extracted/`，记录产物路径
   - pdf：调用 convert_pdf.py → 输出 markdown + 图片到 `raw/.extracted/`，记录产物路径
   - image：标记为"无需处理"，产物路径 `-`
4. **更新 raw-registry.md**：
   - 预处理状态：已处理 / 无需处理
   - 产物路径：有产物时记录路径，无产物时 `-`
   - 最近处理日期：当前日期

### 7.2 类型判断

根据文件扩展名：

| 扩展名 | 类型 | 处理方式 |
|--------|------|---------|
| .md | markdown | 规范化检查 → 可能生成 raw/.extracted/（编码修复/图片下载时） |
| .pdf | pdf | 转 markdown + 提取图片 → raw/.extracted/ |
| .png, .jpg, .gif | image | 无需处理，直接引用 |

### 7.3 markdown 预处理场景

| 场景 | 产物路径 | 说明 |
|------|---------|------|
| 无需预处理 | `-` | 文件格式规范，编码正常，无 http 图片 |
| 编码修复 | raw/.extracted/... | 文件名或内容含特殊编码，规范化后输出 |
| 图片下载 | raw/.extracted/... | 含 http 图片，下载到本地，更新链接后输出 |

---

## 8. kb-compile 执行流程

kb-compile 采用完全 LLM 方案：实体提取和 wiki 生成均由 agent（LLM）完成。

### 8.1 流程步骤

1. **读取 raw-registry.md**：筛选需编译文件（预处理状态 != 未处理 且 编译状态 != 已编译/已引用）
2. **读取文件内容**：
   - 产物路径 != `-`：读取产物路径对应文件
   - 产物路径 == `-`：读取 raw 文件本身
3. **LLM 实体提取**：
   - 阅读 document 内容
   - 提取实体：人物、地点、事件、制度等
   - 识别关系、消歧别名
   - 参考 references/templates/ 约束输出格式
4. **LLM wiki 生成**：
   - 检查 wiki/ 是否已有对应实体文档
   - 无：根据 templates 创建新文档
   - 有：阅读现有内容，合并新信息（增量更新）
   - wiki 文档 source 字段指向 raw 文件
5. **更新 index.md**：添加新页面索引
6. **更新 raw-registry.md**：
   - 编译状态：已编译 / 部分编译
   - 最近处理日期：当前日期

### 8.2 增量更新逻辑

当 wiki/ 已存在同名实体文档时：

| 场景 | LLM 处理方式 |
|------|-------------|
| 信息补充 | 追加新字段或补充现有字段内容 |
| 信息冲突 | 判断是否同一信息的不同表述，或保留冲突注释 |
| 关系去重 | 判断两个关系是否重复，合并 |
| 结构调整 | 根据信息量调整页面结构 |

### 8.3 重新编译意图识别

SKILL.md 包含意图分支逻辑：

| 用户意图 | 执行方式 |
|---------|---------|
| 默认编译 | 筛选"已处理但未编译"的文件 |
| 重新编译（指定文件） | 直接编译指定文件，忽略编译状态 |
| 重新编译（表达意图） | 如用户说"重新编译刘邦"，识别后强制执行 |

### 8.4 SKILL.md 结构示例

```
## kb-compile 执行流程

1. 识别用户意图：
   - 默认编译：筛选预处理完成但未编译的文件
   - 重新编译：用户指定文件或表达"重新编译"意图

2. 根据产物路径读取文件内容

3. 阅读文档，提取实体（人物、地点、事件等）

4. 检查 wiki/ 是否已有对应实体：
   - 无：根据 templates 创建新文档
   - 有：阅读现有内容，合并新信息

5. 更新 index.md 和 raw-registry.md
```

---

## 9. kb-query 和 kb-archive 执行流程

### 9.1 kb-query 流程

kb-query 输出 report（符合模板格式），供 kb-archive 执行。

#### 流程步骤

1. **接收查询意图**：用户提出问题（如"刘邦的社交关系网络"）

2. **解析意图**：
   - 查询对象：实体类型（人物、地点、事件、关系）
   - 查询范围：单实体、多实体、全库、时间限定
   - 查询方式：关键词匹配、语义搜索、关系遍历
   - 输出格式：文档列表、关系图、时间线、对比表格
   - 检测回溯关键词（见下文）

3. **【含回溯关键词】询问用户**：
   ```
   检测到回溯关键词，是否需要回溯 raw 文件？
   (yes → 回溯模式 / no → 标准模式)
   ```

4. **搜索 wiki/ 目录**：根据意图选择搜索策略，匹配相关文档

5. **聚合结果**：汇总查询结果

6. **【查询结果为空】输出提示并终止**：
   ```
   未找到相关实体，建议检查 raw 是否已 compile
   ```

7. **根据模式执行**：

   **标准模式**：
   - 检测疑似缺失（关系不对称、信息稀疏）

   **回溯模式**：
   - 识别相关 raw（通过 entities 的 source 字段）
   - 检查回溯范围限制：
     - 数量限制：最多 5 个 raw 文件
     - 大小限制：单文件超过 50KB 提示用户确认
   - 回溯 raw 文件
   - LLM 提取未提取信息

8. **生成 report**（符合 report-template.md）

9. **【标准模式】输出疑似缺失提示**：
   ```
   疑似缺失提示：
   - [[萧何]] 信息稀疏，建议重新 compile raw/史记/本纪/高祖本纪.md
   
   是否立即重新 compile？(yes/no)
   ```

10. **呈现 report**

#### 回溯关键词

| 关键词 | 示例查询 |
|--------|---------|
| 回溯 | 回溯分析刘邦的社交网络 |
| 全面 | 全面梳理楚汉之争的关键人物 |
| 详细 | 详细考察萧何的政治生涯 |
| 完整 | 完整还原刘邦的早期经历 |
| 补充 | 补充刘邦与萧何的关系细节 |
| 溯源 | 溯源刘邦早期经历的原始记载 |

#### 回溯范围限制

| 限制类型 | 规则 | 超出处理 |
|---------|------|---------|
| 数量限制 | 最多回溯 5 个 raw 文件 | 提示用户选择优先回溯哪些 |
| 大小限制 | 单文件不超过 50KB | 提示用户确认是否处理 |

#### 边界情况处理

| 场景 | 输出 |
|------|------|
| wiki 无相关实体 | "未找到相关实体，建议检查 raw 是否已 compile" |
| 回溯无新发现 | "raw 回溯完成，无新发现信息" |

#### report 输出格式

report 符合 report-template.md 结构：

```markdown
# {{title}}

## 分析
{{analysis}}

【回溯模式额外】
### 回溯新发现
从 raw/xxx.md 发现：
- 信息A（未提取）
- 信息B（未提取）

## 结论
{{conclusion}}

## 相关实体
[[entity1]], [[entity2]], ...

## 回写建议
- 补充 [[entity]]：内容描述（来源：wiki/entities/xxx.md 或 raw/xxx.md）
```

---

### 9.2 kb-archive 流程

kb-archive 接收 kb-query 的 report，执行回写建议。

#### 流程步骤

1. **接收 report**：kb-query 生成的 report 作为上下文

2. **解析回写建议**：提取 report 中的回写建议列表

3. **生成回写摘要**：
   ```
   ## 回写摘要
   
   ### 补充 [[萧何]]
   位置：相关人物 section
   内容：添加"推荐刘邦担任亭长"
   ---
   原文：萧何与刘邦关系密切
   更新后：萧何与刘邦关系密切，曾向沛公推荐刘邦担任亭长
   
   ### 补充 [[曹参]]
   位置：生平 section
   内容：添加早期与刘邦相识
   ---
   原文：曹参随刘邦起兵
   更新后：曹参早年与刘邦同在沛县服役，后随刘邦起兵
   
   是否执行回写？(yes/no/selective)
   ```

4. **询问用户是否执行回写**：
   - `yes`：执行所有回写建议
   - `no`：只创建 synthesis 报告，不执行回写
   - `selective`：逐个确认每条回写建议

5. **根据用户选择执行**：
   - 创建 synthesis/*.md（写入 report，不含回写建议）
   - 执行回写建议：有机融入 wiki 实体文档

6. **更新 index.md**：添加新报告索引

#### 有机融入逻辑

回写采用有机融入，而非简单追加：

| 场景 | 简单追加（错误） | 有机融入（正确） |
|------|-----------------|-----------------|
| 补充关系 | 文末追加"推荐刘邦" | 在"相关人物"section 融入萧何→刘邦关系 |
| 补充事件 | 文末追加事件描述 | 在"生平"section 按时间顺序插入 |
| 补充属性 | 文末追加"出生地：沛县" | 在"基本信息"section 补充或确认出生地字段 |

有机融入由 LLM 执行：
- 阅读现有 wiki 文档内容和结构
- 阅读回写建议中的新内容
- LLM 判断：新内容应融入哪个 section
- 融合写入：补充、合并、或插入到合适位置

#### synthesis 报告格式

synthesis 报告符合 synthesis-template.md 结构：

```markdown
# {{title}}

## 分析
{{analysis}}

## 结论
{{conclusion}}

## 相关实体
[[entity1]], [[entity2]], ...
```

注：synthesis 报告不含"回写建议"section（回写建议已由 kb-archive 执行）。

---

## 10. kb-status 执行流程

### 10.1 流程步骤

1. **解析 raw-registry.md**：统计 raw 文件数量、类型分布、处理状态
2. **解析 index.md**：统计 wiki 文档数量、分类分布、最近修改时间
3. **查找最近活动**：
   - 最近修改 wiki：从 index.md 各 section 获取最新更新时间
   - 最近预处理 raw：从 raw-registry.md 获取最新处理日期
4. **查找待处理文件**：从 raw-registry.md
   - 预处理状态为"未处理"
   - 编译状态为"未编译"或"部分编译"
5. **格式化输出**：调用 format_dashboard.py 生成文本仪表盘

**信息来源：**

| 信息 | 来源 | 说明 |
|------|------|------|
| raw 文件统计 | raw-registry.md | 数量、类型、状态 |
| wiki 文档统计 | index.md | 数量、分类（不扫描 wiki 目录） |
| 最近修改 wiki | index.md | 各 entry 的更新时间 |
| 最近预处理 | raw-registry.md | 最近处理日期字段 |

### 10.2 输出格式

```
Knowledge Base Dashboard: my-kb/

┌─────────────────────────────────────────────────┐
│ Overview                                         │
├─────────────────────────────────────────────────┤
│ Raw Files:         42 (markdown: 28, pdf: 8, image: 6) │
│ Wiki Documents:    156 (entities: 98, concepts: 34, synthesis: 24) │
│ Pending Ingest:    5 files                       │
│ Pending Compile:   12 files                      │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Recent Activity                                   │
├─────────────────────────────────────────────────┤
│ Latest Compiled:   [[liu-bang]] (2026-04-17)     │
│ Latest Archived:   [[刘邦关系网络]] (2026-04-16) │
│ Latest Ingested:   raw/史记/本纪/项羽本纪.md (2026-04-17) │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ Pending Files                                     │
├─────────────────────────────────────────────────┤
│ raw/史记/列传/张良传.md         (未处理)          │
│ raw/史记/列传/韩信传.md         (未处理)          │
│ raw/某书/chapter2.pdf          (已处理, 未编译)   │
│ ...                                              │
│ (显示前 10 个，另有 X 个待处理)                   │
└─────────────────────────────────────────────────┘
```

---

## 11. kb-lint 执行流程

### 11.1 流程步骤

1. **扫描 wiki/ 目录**：获取所有 wiki 文档
2. **语法检查**：调用 syntax.py 检查 markdown 格式、链接有效性
3. **语义检查**：调用 semantic.py 检查内容一致性、引用完整性
4. **报告问题**：汇总检查结果，呈现给用户
5. **可选修复**：调用 fix.py 自动修复可修复的问题

---

## 12. 技术栈

- **Python 3.11+**
- **uv**：包管理和依赖管理
- **typer**：CLI 框架
- **rich**：终端输出格式化

---

## 13. Git 管理

migu 是 Git 管理的独立仓库：
- skills 和 rules 的变更可追溯
- 用户可通过 `git pull` 更新 migu
- migu 版本号与 git tag 对应

---

## 14. 扩展设计

未来可添加：
- 新的 rules 类型（tech、legal 等）
- 新的 skills（kb-export、kb-sync 等）
- migu upgrade 命令（更新 migu 本身）

---

## 15. 关键设计决策

### 15.1 skills 按类型分组

**选择：按类型分组（minimal/history）**

理由：
- 与 rules 目录组织一致，命名统一
- minimal 作为基础，减少重复
- 类型专属 skill 可覆盖 minimal 实现（如 history kb-compile）

### 15.2 scripts 放在 skill 内部

**选择：放在 skill 内部**

理由：
- skill 自包含，复制即安装
- 无需额外的 scripts.config 配置
- 各 skill 独立运作，无依赖关系

### 15.3 kb-ingest 和 kb-compile 分离

**选择：分离预处理和编译**

理由：
- 预处理逻辑通用（markdown 规范化、PDF 转换）
- 编译逻辑可定制（实体提取规则因知识库类型不同）
- 中间产物 raw/.extracted/ 可复用，避免重复预处理

### 15.4 kb-query 和 kb-archive 分离

**选择：分离查询和回写**

理由：
- kb-query 保持纯查询，不修改 wiki
- kb-archive 负责回写，用户可控
- 相似文档检测时询问用户，避免盲目覆盖

### 15.5 raw-registry.md 不记录编译产物

**选择：移除编译产物字段**

理由：
- wiki 文档已有 `source` 字段指向 raw 文件
- 双向追踪造成冗余
- raw-registry 只追踪处理状态，简化结构

### 15.6 版本升级通过检测提示

**选择：migu skill list 检测版本差异**

理由：
- 用户可选择是否升级，不强制
- 显示具体版本差异，用户知情决策
- reinstall 时检测修改并显示 diff，保护用户定制

### 15.7 kb-query 回溯模式

**选择：有限支持回溯（关键词触发 + 用户确认 + 范围限制）**

理由：
- 标准模式保持高效（只查 wiki，无 raw 回溯）
- 回溯模式满足深度需求（发现 raw 中未提取信息）
- 关键词触发避免误执行（用户表达回溯意图）
- 用户确认确保意图准确（避免关键词歧义）
- 范围限制控制资源消耗（最多 5 文件，单文件 50KB）
- wiki 文档 source 字段依赖：回溯通过 source 定位 raw

### 15.8 structure.json 与其他组件匹配约束

**选择：rules 设计者需确保三者一致**

三者需匹配：

| 组件 | 内容 | 生成/定义时机 |
|------|------|--------------|
| structure.json | wiki 目录结构 | rules 定义 |
| kb-compile SKILL.md | 实体类型 → 目录映射 | rules 定义 |
| index.md | sections 分类 | migu init 根据 structure.json 生成 |

**匹配示例：**

| structure.json | kb-compile SKILL.md | index.md |
|----------------|---------------------|----------|
| wiki/entities/ | 人物 → entities/ | ## entities |
| wiki/concepts/ | 概念 → concepts/ | ## concepts |
| wiki/synthesis/ | synthesis | ## synthesis |

**kb-compile 不读取 structure.json：**

- 目录由 migu init 创建，已存在
- kb-compile 通过 SKILL.md 映射决定实体放入哪个目录
- rules 设计者需确保 SKILL.md 映射目标目录与 structure.json 一致

---

## 16. 文件命名规范

| 文件 | 命名规则 |
|------|----------|
| skill 目录 | `<skill-name>`（无类型后缀） |
| skills.json 配置 | 通过 `source` 字段指定来源 |
| raw-registry.md wikilink | 使用 `\|` 转义符号 |
| raw/.extracted/ 文件 | 与 raw/ 目录结构镜像对应 |

---

## 17. 约束

- raw/ 目录不可变（用户管理）
- raw/.extracted/ 目录由 kb-ingest 维护（不手动修改）
- AGENTS.md 可修改（用户定制）
- skills-lock.json 自动维护（不手动修改）
- raw-registry.md 自动维护（kb-ingest/kb-compile 更新）