---
title: Migu 脚手架项目设计文档
created: 2026-04-17
type: spec
status: draft
version: 3.0
last_updated: 2026-04-21
changes: 重组 spec 结构：按 domain 分离（脚手架/知识库）、移出 skills 流程细节至 implementation guide、新增 §5 契约边界、§4.3 AGENTS.md 开发指南、§3.4 实现约束、删除 §14 扩展设计、§16 分散整合；优化 spec：消除冗余（Karpathy 表/skills 表）、补全遗漏（output/目录/解析规范/扩展指南/错误处理）、修复不一致（source 字段格式/scripts 使用方式）
---

# Migu 脚手架项目设计文档

> **受众声明**：本 spec 服务于脚手架开发者、知识库开发者（Skills + AGENTS.md）。知识库使用者（仅调用 skills）不在受众范围内。
>
> **核心理念**：本设计践行 Karpathy LLM-WIKI 模式——三层架构（Raw sources → Wiki → Schema），Operations（Ingest/Query/Lint），wiki 作为持久化可累积产物。

---

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

**架构概览：**

与 Karpathy LLM-WIKI 三层架构对应：

| Karpathy 层 | migu 对应 | 说明 |
|-------------|-----------|------|
| Raw sources | `raw/` 目录 | 用户管理的源文件，不可变 |
| Wiki | `wiki/` 目录 | LLM 生成的结构化文档 |
| Schema | `AGENTS.md` + Skills | 告诉 LLM 如何结构化 wiki |

---

## 2. 目录结构

> 目录结构定义架构边界。脚手架开发者关注 §2.1（migu 项目）；知识库开发者关注 §2.2（知识库实例）。

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

## 3. 脚手架架构

> 本节定义脚手架层架构。知识库开发者可跳过，但需了解 §3.1 中 skills.json 格式（脚手架交付给知识库的契约）。

### 3.1 Rules 规则定义

#### rules 目录组织

采用"基础 + 覆盖"模式：

- **minimal**：基础规则，包含完整配置
- **其他规则**：继承 minimal，只包含差异文件

#### 配置文件

**AGENTS.md**

知识库 schema，定义：
- 目录结构
- 命名规范
- 引用格式
- 操作规则

**structure.json**

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

使用时机：

| 阶段 | 是否使用 | 说明 |
|------|---------|------|
| migu init | ✓ 使用 | 创建知识库目录结构 |
| kb-compile | ✗ 不使用 | 目录已存在，实体类型→目录映射由 SKILL.md 定义 |

隐含约束：structure.json wiki 目录结构需与 kb-compile SKILL.md 实体类型→目录映射一致（见 §5.1 三方一致性验证）。

**skills.json**

定义安装哪些 skills。

skills.json 是**技能选择器**，而非继承器：

- 每个 rules 的 skills.json 是独立配置，选择该类型知识库需要的 skills
- minimal 的 skills.json 是默认配置模板（6 个基础 skills）
- 其他 rules 的 skills.json 根据需求选择 skills（数量可能不同）

**强制要求**：每个 rules 必须提供 skills.json。migu init 执行时若 rules 目录缺少 skills.json，报错退出。

minimal 的 skills.json：

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

history 的 skills.json：

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

注：history 选择 kb-compile 的 history 版本，其他 skills 选择 minimal 版本。

**templates/**

存放初始文件的内容模板，migu init 复制到知识库根目录。详见 §4.1 文件格式规范。

#### 继承规则

非 minimal 规则继承 minimal 的配置，只覆盖差异部分：

| 文件/目录 | 继承行为 |
|----------|---------|
| AGENTS.md | 存在则覆盖，不存在则继承 minimal |
| skills.json | **独立配置，不继承** |
| structure.json | 存在则覆盖，不存在则继承 minimal |
| templates/*.md | 同名文件覆盖，不存在则继承 minimal/templates/ 对应文件 |

继承示例（history 规则）：
- AGENTS.md：覆盖（schema 不同）
- skills.json：独立配置（选择需要的 skills）
- structure.json：不提供，继承 minimal（目录结构相同）
- templates/index.md：覆盖（索引格式可能不同）
- templates/log.md：不提供，继承 minimal
- templates/raw-registry.md：不提供，继承 minimal

### 3.2 CLI 命令设计

#### migu init

```bash
migu init <target-dir> [--rules <rules-name>]
```

参数：
- `<target-dir>`：知识库目标目录（必需）
- `--rules`：规则名称（minimal、history），默认 minimal

执行流程：
1. 检查 `<target-dir>` 是否存在：已存在则报错退出
2. 验证三方一致性（见 §5.1）
3. 合并配置（继承 minimal + 覆盖指定 rules）
4. 创建目录结构（根据合并后的 structure.json）
5. 安装 skills（根据 skills.json）：复制 `skills/<source>/<name>` → `<target-dir>/.agents/skills/<name>`
6. 创建 skills-lock.json
7. 复制模板文件（保留 frontmatter）

幂等性：migu init 是幂等操作，重复执行同一命令会被拒绝。

#### migu skill

```bash
migu skill install <skill-name> <target-dir>
migu skill uninstall <skill-name> <target-dir>
migu skill reinstall <skill-name> <target-dir>
migu skill list <target-dir>
```

migu skill reinstall：
- 查找 skill 的 source（从 skills-lock.json）
- 检测目标 skill 目录是否有用户修改（对比 migu 捆绑版本）
- 如有修改，显示 diff 并询问用户确认
- 复制最新版本，更新 skills-lock.json

migu skill list：
- 列出已安装 skills（name、source、version）
- 对比 migu 捆绑版本与 skills-lock.json 记录版本
- 显示版本状态：✓ latest 或 ⚠ outdated

#### migu rules

```bash
migu rules list <target-dir>
```

检测 rules 配置文件（AGENTS.md、templates/*.md）的版本更新状态（见 §3.3 版本追踪机制）。

rules 配置文件由用户手动修改，migu 不自动更新。

#### 版本命令

```bash
migu --version        # 显示版本
migu --help           # 显示帮助
```

### 3.3 版本追踪机制

#### frontmatter 格式

migu repo 中 rules 文件预置 frontmatter，复制到知识库时保留：

| 文件 | migu repo 状态 | 复制到知识库行为 |
|------|----------------|------------------|
| AGENTS.md | 预置 frontmatter | 保留原有 frontmatter |
| templates/*.md | 预置 frontmatter | 保留原有 frontmatter |

frontmatter 示例：

```yaml
---
version: 1.0
---
# Knowledge Base Schema
```

字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| version | string | 配置文件版本号 |

#### skills-lock.json 格式

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
    }
  ]
}
```

#### 版本检测逻辑

skills 版本检测（migu skill list）：
- 对比 skills-lock.json 记录版本与 migu 捆绑版本
- 显示差异，用户可选择 reinstall

rules 配置版本检测（migu rules list）：
- 解析知识库文件的 frontmatter.version
- 根据 skills-lock.json 的 `rules` 字段定位 migu 捆绑的 rules 目录
- 对比 version，输出 diff + 手动更新建议

### 3.4 实现约束

#### 技术栈

- **Python 3.11+**
- **uv**：包管理和依赖管理
- **typer**：CLI 框架
- **rich**：终端输出格式化

#### Git 管理

migu 是 Git 管理的独立仓库：
- skills 和 rules 的变更可追溯
- 用户可通过 `git pull` 更新 migu
- migu 版本号与 git tag 对应

### 3.5 文件命名规范（脚手架层）

| 文件 | 命名规则 | 说明 |
|------|----------|------|
| skill 目录 | `<skill-name>`（无类型后缀） | 安装到知识库时目录名不含类型 |

---

## 4. 知识库架构

> 本节定义知识库层架构。脚手架开发者可跳过，但需了解 §4.2 中 Skills 契约定义（理解 skills.json 的 source 字段含义）。

### 4.1 文件格式规范

#### index.md

wiki 文档索引，kb-compile 创建 wiki 页面时更新，kb-archive 创建报告时更新。

生成方式：

| 阶段 | 操作 |
|------|------|
| migu init | 根据 structure.json wiki 目录动态生成 sections |
| kb-compile | 创建 wiki 页面后，在对应 section 添加 entry |
| kb-archive | 创建 synthesis 报告后，在 synthesis section 添加 entry |

格式示例：

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

隐含约束：index.md sections 与 structure.json wiki 目录结构一致。

#### log.md

操作日志，每次操作后追加。

entry format：

```markdown
## [YYYY-MM-DD] operation | details
```

operation 标准值：

| operation | 说明 | 是否记录 |
|-----------|------|---------|
| ingest | 预处理 raw 文件 | ✓ 记录 |
| compile | 编译生成 wiki | ✓ 记录 |
| archive | 创建 synthesis + 回写 | ✓ 记录 |
| lint | Wiki 检查 | ✓（有修复时记录） |
| query | Wiki 查询 | ✗ 不记录 |
| status | 展示仪表盘 | ✗ 不记录 |

#### raw-registry.md

raw 文件注册表，kb-ingest 和 kb-compile 共同维护。

表格格式：

```markdown
# Raw File Registry

| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
| [[raw/史记/本纪/高祖本纪.md\|史记·本纪·高祖本纪]] | markdown | 记载刘邦生平及汉朝建立 | 已处理 | raw/.extracted/史记/本纪/高祖本纪.md | 已编译 | 2026-04-17 |
```

**命名规范（知识库层）**：

| 文件 | 命名规则 | 说明 |
|------|----------|------|
| wikilink 格式 | 使用 `\|` 转义符号 | Obsidian 兼容格式 |
| raw/.extracted/ 文件 | 与 raw/ 目录结构镜像对应 | kb-ingest 输出产物 |

状态定义：

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

#### output/ 目录

存放根据 wiki 内容生成的衍生文档（slide、excel 等）。

管理方式：
- migu init 根据 structure.json 创建 output/ 目录
- 目录内容由用户自行管理（不定义专门 skill）
- 子目录结构由用户自定义
- migu 不追踪该目录内容状态（与 raw-registry.md 无关）

用途示例（用户可自定义）：
- slide/：导出的演示文稿
- excel/：导出的数据表格
- export/：其他格式导出

#### wiki 文档格式

wiki 文档由 kb-compile 生成，存放在 `wiki/` 目录下。

标准结构：

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
- source: [[raw/史记/本纪/高祖本纪.md]]
```

source 字段规范：

| 规则 | 说明 |
|------|------|
| 必须包含 | 每个 wiki 文档必须有 source 字段 |
| 固定位置 | 放在 `## 来源` section 下，作为列表项 |
| 格式固定 | `- source: [[raw/<path>]]` |
| 指向 raw | 指向原始 raw 文件（原始出处），而非 .extracted/ 产物 |
| 回溯依赖 | kb-query 回溯模式通过此字段定位 raw 文件 |

#### 解析规范

scripts 解析 raw-registry.md 时需遵循：

| 解析规则 | 说明 |
|----------|------|
| 表格分隔符 | 第二行为 `|------|------|...` 格式 |
| wikilink 解析 | `[[path\|alias]]` 格式，提取 path 部分 |
| 状态字段 | 预处理状态、编译状态为枚举值（见本 spec §4.1 raw-registry.md 状态定义表） |
| 日期格式 | YYYY-MM-DD 格式 |
| 空字段 | `-` 表示无值 |

#### 解析异常处理

kb-ingest scan_raw.py 与 kb-status read_registry.py 遇到格式错误时：

处理方式：
- 报错退出，不跳过异常条目
- 提供修复建议：指出错误行号 + 期望格式
- 提示重执行：kb-ingest 可恢复 raw-registry.md 格式

示例输出：

```
raw-registry.md 格式错误：
- 第 N 行：wikilink 格式不正确，期望 [[path\|alias]]
- 第 M 行：预处理状态值无效，期望：未处理/已处理/无需处理

修复方式：重新执行 kb-ingest 可恢复格式，或手动修复后重新执行。
```

#### templates/

存放初始文件的内容模板（migu init 复制到知识库根目录）：

**templates/index.md**：

```markdown
---
version: 1.0
---
# Wiki Index

<!-- 
entry format: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD
sections 对应 structure.json wiki 目录结构
-->

<!-- 以下 section 由 migu init 根据 structure.json 动态生成 -->
```

**templates/log.md**：

```markdown
---
version: 1.0
---
# Knowledge Base Log

<!-- 
entry format: ## [YYYY-MM-DD] operation | details
operation: ingest | compile | archive | lint
query 和 status 不记录
-->

<!-- 操作日志由 kb-ingest/compile/archive/lint 自动追加 -->
```

**templates/raw-registry.md**：

```markdown
---
version: 1.0
---
# Raw File Registry

<!-- 
entry format: | 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
-->

| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
```

### 4.2 Skills 契约定义

每个 skill 完全自包含，职责单一：

| skill | 职责 | scripts |
|-------|------|---------|
| kb-ingest | 扫描 raw/、预处理文件、输出到 raw/.extracted/ | scan_raw.py, validate_batch.py, normalize_markdown.py, convert_pdf.py |
| kb-compile | 读取文件、提取实体、生成 wiki 页面（完全 LLM） | read_file.py, update_registry.py |
| kb-lint | Wiki 检查（语法、语义、修复） | lint.py, syntax.py, semantic.py, fix.py |
| kb-query | Wiki 查询 + 回溯模式 + 生成 report | search_wiki.py |
| kb-archive | 接收 report + 回写摘要 + 有机融入 | read_report.py, create_synthesis.py, update_entity.py |
| kb-status | 展示知识库仪表盘（解析 index.md + raw-registry.md） | read_registry.py, read_index.py, format_dashboard.py |

**技能执行模型**：

每个 skill 是 agent 指令包：
- **SKILL.md**：agent 加载的上下文指令，定义操作流程和规则
- **scripts/**：辅助工具，agent 可按需调用执行具体任务
- **references/**：参考文档、模板、模式定义

调用方式：用户触发技能名称（如"kb-ingest"），agent 加载对应 SKILL.md 获得指令，按流程执行并适时调用 scripts。

**依赖层次**：

| 层次 | 类型 | 说明 | 示例 |
|------|------|------|------|
| 数据依赖 | 输入输出依赖 | 用户手动编排执行顺序 | kb-ingest 输出 → kb-compile 输入 |
| 会话依赖 | agent 上下文依赖 | 必须同一 agent session | kb-query report → kb-archive |

独立执行：各 skill 可独立触发执行，但协作型 skills（如 kb-query + kb-archive）存在会话依赖，需在同一 agent session 中执行。

**按类型分组**：

- `skills/minimal/`：基础 skill 实现（kb-ingest、kb-compile、kb-lint、kb-query、kb-archive、kb-status）
- `skills/history/`：历史知识库定制（kb-compile 的历史版本）

minimal 作为基础：
- minimal 规则使用 `source: minimal`（所有 skill）
- history 规则对 kb-compile 使用 `source: history`，其他 skill 使用 `source: minimal`
- kb-ingest 只有 minimal 版本（预处理逻辑通用）

### 4.3 AGENTS.md 开发指南

#### AGENTS.md 的职责

AGENTS.md 是知识库 schema，对应 Karpathy LLM-WIKI 的 Schema 层：

| Karpathy 定义 | AGENTS.md 对应 |
|---------------|----------------|
| 告诉 LLM wiki 如何结构化 | 定义目录结构、命名规范 |
| 约定是什么 | 定义引用格式、操作规则 |
| 工作流是什么 | 引用 Skills，定义执行顺序 |

#### AGENTS.md 包含的内容

- 目录结构定义
- 命名规范
- 引用格式（wikilink 规范）
- 操作规则（与 Karpathy Operations 对应）

与 Karpathy LLM-WIKI Operations 对应：

| Karpathy Operation | migu Skills |
|--------------------|-------------|
| Ingest | kb-ingest |
| Query | kb-query |
| Lint | kb-lint |

#### AGENTS.md 与 skills.json 协作

AGENTS.md 定义知识库结构，skills.json 选择用于操作该结构的 skills。

两者需协调：
- structure.json wiki 目录与 kb-compile SKILL.md 实体类型→目录映射一致
- AGENTS.md 引用格式与 wiki 文档 source 字段格式一致

### 4.4 约束

- raw/ 目录不可变（用户管理）
- raw/.extracted/ 目录由 kb-ingest 维护（不手动修改）
- output/ 目录由用户管理（自行创建衍生文档）
- AGENTS.md 可修改（用户定制）
- skills-lock.json 自动维护（不手动修改）
- raw-registry.md 自动维护（kb-ingest/kb-compile 更新）

违反约定可能导致 migu 功能异常，需重新执行对应 skill 恢复。

---

## 5. 契约边界

> 本节定义跨 domain 契约。两个角色都需要理解，确保脚手架交付物与知识库期望一致。
>
> **纯声明模式**：本节只声明契约关系，格式定义见 §3/§4。

### 5.1 脚手架 → 知识库的交付物

**migu init 交付内容**：

| 交付物 | 格式定义位置 | 说明 |
|--------|--------------|------|
| 目录结构 | §3.1 structure.json | 根据 rules 的 structure.json 创建 |
| AGENTS.md | §3.1 AGENTS.md | 从 rules 复制，保留 frontmatter |
| templates 文件 | §4.1 templates/ | index.md、log.md、raw-registry.md |
| Skills | §3.1 skills.json | 根据 skills.json 安装到 `.agents/skills/` |
| skills-lock.json | §3.3 skills-lock.json | 记录安装版本信息 |

**三方一致性验证**：

migu init 执行前验证三者一致（见 §3.2 CLI 命令设计）：

| 检查项 | 来源 |
|--------|------|
| wiki 目录列表 | structure.json `directories.wiki` 子目录 |
| 实体映射目录 | kb-compile SKILL.md 实体类型→目录映射 |
| sections 列表 | templates/index.md 或动态生成 |

验证失败则报错并拒绝创建。

### 5.2 知识库 → 脚手架的反馈

**版本信息反馈**：

| 反馈物 | 格式定义位置 | 说明 |
|--------|--------------|------|
| skills-lock.json | §3.3 skills-lock.json | 记录已安装 skills 版本，用于 migu skill list 检测 |
| rules 字段 | §3.3 skills-lock.json | 记录使用的 rules 类型，用于 migu rules list 定位 |

**版本检测机制**（见 §3.2 CLI 命令设计）：
- migu skill list：对比 skills-lock.json 与 migu 捆绑版本
- migu rules list：对比知识库文件 frontmatter 与 migu 捆绑 rules

### 5.3 版本升级边界

**skills 版本升级**：

- 检测：migu skill list
- 更新：migu skill reinstall
- 特点：自动更新，显示 diff，保护用户定制

**rules 配置升级**：

- 检测：migu rules list
- 更新：用户手动修改
- 特点：不自动更新，保护知识库定制内容

**职责差异**：

| 类型 | 检测命令 | 更新方式 | 原因 |
|------|----------|----------|------|
| skills | migu skill list | migu skill reinstall | skills 是程序化文件，可覆盖 |
| rules | migu rules list | 用户手动 | rules 是知识库 schema，需用户决策 |

---

## 6. 关键设计决策

### 6.1 skills 按类型分组

**选择：按类型分组（minimal/history）**

理由：
- 与 rules 目录组织一致，命名统一
- minimal 作为基础，减少重复
- 类型专属 skill 可覆盖 minimal 实现（如 history kb-compile）

### 6.2 scripts 放在 skill 内部

**选择：放在 skill 内部**

理由：
- skill 自包含，复制即安装
- 无需额外的 scripts.config 配置
- 各 skill 可独立触发执行，协作型 skills 存在会话依赖

### 6.3 kb-ingest 和 kb-compile 分离

**选择：分离预处理和编译**

理由：
- 预处理逻辑通用（markdown 规范化、PDF 转换）
- 编译逻辑可定制（实体提取规则因知识库类型不同）
- 中间产物 raw/.extracted/ 可复用，避免重复预处理

### 6.4 kb-query 和 kb-archive 分离

**选择：分离查询和回写**

理由：
- kb-query 保持纯查询，不修改 wiki
- kb-archive 负责回写，用户可控
- 相似文档检测时询问用户，避免盲目覆盖

### 6.5 raw-registry.md 不记录编译产物

**选择：移除编译产物字段**

理由：
- wiki 文档已有 `source` 字段指向 raw 文件
- 双向追踪造成冗余
- raw-registry 只追踪处理状态，简化结构

### 6.6 版本升级通过检测提示

**选择：migu skill list 检测版本差异**

理由：
- 用户可选择是否升级，不强制
- 显示具体版本差异，用户知情决策
- reinstall 时检测修改并显示 diff，保护用户定制

### 6.7 kb-query 回溯模式

**选择：有限支持回溯（关键词触发 + 用户确认 + 范围限制）**

理由：
- 标准模式保持高效（只查 wiki，无 raw 回溯）
- 回溯模式满足深度需求（发现 raw 中未提取信息）
- 关键词触发避免误执行（用户表达回溯意图）
- 用户确认确保意图准确（避免关键词歧义）
- 范围限制控制资源消耗（最多 5 文件，单文件 50KB）
- wiki 文档 source 字段依赖：回溯通过 source 定位 raw

### 6.8 structure.json 与其他组件匹配约束

**选择：rules 设计者需确保三者一致**

三者需匹配：

| 组件 | 内容 | 生成/定义时机 |
|------|------|--------------|
| structure.json | wiki 目录结构 | rules 定义 |
| kb-compile SKILL.md | 实体类型 → 目录映射 | rules 定义 |
| index.md | sections 分类 | migu init 根据 structure.json 生成 |

匹配示例：

| structure.json | kb-compile SKILL.md | index.md |
|----------------|---------------------|----------|
| wiki/entities/ | 人物 → entities/ | ## entities |
| wiki/concepts/ | 概念 → concepts/ | ## concepts |
| wiki/synthesis/ | synthesis | ## synthesis |

kb-compile 不读取 structure.json：
- 目录由 migu init 创建，已存在
- kb-compile 通过 SKILL.md 映射决定实体放入哪个目录
- rules 设计者需确保 SKILL.md 映射目标目录与 structure.json 一致

---

## 7. 扩展指南

### 创建新 rules 类型

最小文件集：
- AGENTS.md（必须）
- skills.json（必须）
- structure.json（可选，继承 minimal）
- templates/*.md（可选，继承 minimal）

命名规范：
- rules 名称：小写字母，如 legal、medical
- 目录位置：rules/<rules-name>/

继承规则：
- skills.json：独立配置，不继承
- 其他文件：存在则覆盖，不存在则继承 minimal

### 三方一致性验证

创建新 rules 时需确保三者一致：
- structure.json wiki 目录与 kb-compile SKILL.md 实体类型→目录映射一致
- index.md sections 与 structure.json wiki 目录一致

验证机制详见 §5.1，migu init 执行前自动验证，失败则拒绝创建。

### 示例：创建 legal rules

1. 创建目录：rules/legal/
2. 创建 AGENTS.md：定义法律知识库 schema
3. 创建 skills.json：选择需要的 skills
4. （可选）创建 structure.json：定义 wiki 目录结构
5. （可选）创建 templates/：定制初始文件模板
6. 测试：migu init test-kb --rules legal

---

## 8. 错误处理策略

### 错误类型

| 错误类型 | 说明 | 处理原则 |
|----------|------|---------|
| 参数无效 | target-dir 路径不合法、rules 名称不存在 | 报错退出，提示有效选项 |
| 目录已存在 | target-dir 已存在（非知识库） | 报错退出，提示选择其他路径 |
| 配置缺失 | rules 目录缺少 skills.json 或 structure.json | 报错退出，提示检查 rules 配置 |
| 版本冲突 | skills-lock.json 与 migu 捆绑版本不一致 | 显示 diff，提示用户选择 reinstall 或保留 |

### 处理原则

- 报错退出：严重错误，阻止继续执行
- 提示确认：用户可选择继续或退出（如版本冲突）
- 自动恢复：尝试修复简单问题（如创建缺失目录）

---

## 附录：Skills 流程设计指导

Skills 执行流程的设计指导文档见 `docs/superpowers/specs/2026-04-21-skills-implementation-guide.md`，包含各 skill 的流程模板、与 Karpathy LLM-WIKI Operations 的对应关系。

最终实现结果见 `skills/` 目录下的各 SKILL.md 文件。