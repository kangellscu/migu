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
│   │   kb-query/              # Wiki 查询
│   │   │   SKILL.md
│   │   │   references/
│   │   │       intent-patterns.md
│   │   │       templates/
│   │   │
│   │   kb-archive/            # 回写
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   create_report.py
│   │   │   │   update_page.py
│   │   │   references/
│   │   │       templates/
│   │   │       │   report-template.md
│   │   │
│   │   kb-status/             # 仪表盘
│   │   │   SKILL.md
│   │   │   scripts/
│   │   │   │   scan_registry.py
│   │   │   │   scan_wiki.py
│   │   │   │   format_dashboard.py
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
| kb-query | Wiki 查询 | 无（依赖 references） |
| kb-archive | 回写查询结果（新建报告或更新现有页面） | create_report.py, update_page.py |
| kb-status | 展示知识库仪表盘 | scan_registry.py, scan_wiki.py, format_dashboard.py |

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

#### templates/

存放初始文件的内容模板：

- **index.md**：wiki 文档索引模板
- **log.md**：操作日志模板
- **raw-registry.md**：raw 文件注册表模板（含表格结构）

模板文件直接复制到知识库根目录，不同规则可通过覆盖模板定制初始内容。

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
   - 合并 templates 目录内容
   - 复制到 `<target-dir>/`（index.md、log.md、raw-registry.md）

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

格式由 AGENTS.md 定义。

### 6.2 log.md

操作日志，每次操作后追加。

格式：`## [YYYY-MM-DD] operation | details`

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

**source 字段说明：**

- 指向 raw 文件（原始出处），而非 .extracted/ 产物
- 语义：用户视角的原始来源追溯
- 格式：wikilink（便于 Obsidian 导航）

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

1. **接收查询意图**：用户提出问题（如"刘邦的社交关系网络"）
2. **解析意图**：根据 references/intent-patterns.md 判断查询类型
3. **搜索 wiki/ 目录**：匹配相关文档
4. **聚合结果**：汇总查询结果，呈现给用户
5. **不修改 wiki**：kb-query 只查询，不回写

### 9.2 kb-archive 流程

kb-archive 接收 kb-query 结果的方式：用户在 kb-query 执行后，将查询结果（文档路径、实体列表、关系图等）作为上下文传递给 agent，然后触发 kb-archive。

**流程步骤：**

1. **接收查询结果**：用户传递 kb-query 的结果作为上下文
2. **检查 synthesis/ 目录**：是否存在相似主题文档
3. **如存在相似文档**：询问用户（新建 or 更新）
   ```
   Found similar document: synthesis/刘邦关系网络.md
   Create new report or update existing? (new/update)
   ```
4. **执行回写**：
   - 新建报告：调用 create_report.py → `synthesis/<主题>.md`
   - 更新现有：调用 update_page.py → 补充信息到相关 wiki 页面
5. **更新 index.md**：添加新报告索引（如新建）

---

## 10. kb-status 执行流程

### 10.1 流程步骤

1. **解析 raw-registry.md**：统计文件数量、类型分布、处理状态
2. **扫描 wiki/ 目录**：统计文档数量、分类分布
3. **查找最近活动**：
   - 最近编译的 wiki 文档（按 processed_at 日期排序）
   - 最近归档的 synthesis 文档（按文件修改时间）
   - 最近预处理的 raw 文件（从 raw-registry.md）
4. **查找待处理文件**：
   - 预处理状态为"未处理"
   - 编译状态为"未编译"或"部分编译"
5. **格式化输出**：调用 format_dashboard.py 生成文本仪表盘

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