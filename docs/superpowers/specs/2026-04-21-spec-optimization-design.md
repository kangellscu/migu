---
title: Spec 优化设计文档
created: 2026-04-21
type: spec
status: draft
version: 1.0
related_specs:
  - docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
  - docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
---

# Spec 优化设计文档

> **优化目标**：消除冗余、补全遗漏、修复不一致、重构文档结构
>
> **文档分工**：
> - scaffold-design（架构层）：定义"是什么"（目录结构、契约边界、CLI 命令、版本机制、扩展指南）
> - implementation-guide（实现层）：定义"怎么做"（流程步骤、scripts 使用说明、Karpathy 映射）

---

## 1. 冗余消除

### 1.1 Karpathy 对应表

| 文档 | 处理 |
|------|------|
| scaffold-design §4.3 | 删除表格，改为引用："与 Karpathy LLM-WIKI Operations 的对应关系详见 implementation-guide 开头" |
| implementation-guide 开头 | 保留表格 |

### 1.2 Skills 职责表

| 文档 | 处理 |
|------|------|
| scaffold-design §4.2 | 简化为概览表，只保留两列：skill 名称、一句话职责；删除 scripts 列 |
| implementation-guide §1-6 | 各 skill 流程设计末尾增加详细 scripts 使用说明表格 |

**scaffold-design §4.2 概览表格式**：

| skill | 职责 |
|-------|------|
| kb-ingest | 扫描 raw/、预处理文件、输出到 raw/.extracted/ |
| kb-compile | 读取文件、提取实体、生成 wiki 页面（完全 LLM） |
| kb-lint | Wiki 检查（语法、语义、修复） |
| kb-query | Wiki 查询 + 回溯模式 + 生成 report |
| kb-archive | 接收 report + 回写摘要 + 有机融入 |
| kb-status | 展示知识库仪表盘（解析 index.md + raw-registry.md） |

### 1.3 minimal/history 分组说明

| 文档 | 处理 |
|------|------|
| scaffold-design §4.2 | 保留"按类型分组"说明（架构层定义） |
| implementation-guide §1-6 | "适用范围"改为引用 scaffold-design §4.2 |

**implementation-guide 适用范围格式**：

```markdown
**适用范围**：见 scaffold-design §4.2 按类型分组。
```

### 1.4 SKILL.md 编写模板

| 文档 | 处理 |
|------|------|
| scaffold-design 附录 | 保留引用 implementation-guide |
| implementation-guide 附录 | 移到开头，定义表格格式；原位置删除 |

---

## 2. 补全遗漏

### 2.1 output/ 目录定义

添加到 scaffold-design §4.1 文件格式规范：

```markdown
#### output/ 目录

存放根据 wiki 内容生成的衍生文档（slide、excel 等）。

管理方式：
- migu init 根据 structure.json 创建 output/ 目录
- 目录内容由用户自行管理（不定义专门 skill）
- 子目录结构由用户自定义
- migu 不追踪该目录内容状态（与 raw-registry.md 无关）

用途示例：
- slide/：导出的演示文稿
- excel/：导出的数据表格
- export/：其他格式导出
```

**structure.json 格式调整**：

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

注：`.agents/skills/` 不在 structure.json 中定义，由 migu init 安装 skills 时自动创建。

### 2.2 CLI 错误处理策略

添加到 scaffold-design §8（新增章节）：

```markdown
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
```

### 2.3 扩展指南

添加到 scaffold-design §7（新增章节）：

```markdown
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
```

### 2.4 raw-registry.md 解析规范

添加到 scaffold-design §4.1 raw-registry.md 格式定义末尾：

```markdown
#### 解析规范

scripts 解析 raw-registry.md 时需遵循：

| 解析规则 | 说明 |
|----------|------|
| 表格分隔符 | 第二行为 `|------|------|...` 格式 |
| wikilink 解析 | `[[path\|alias]]` 格式，提取 path 部分 |
| 状态字段 | 预处理状态、编译状态为枚举值（见状态定义表） |
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
```

---

## 3. 修复不一致

### 3.1 source 字段格式标准化

修改 scaffold-design §4.1 wiki 文档格式：

```markdown
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
```

### 3.2 scripts 使用方式明确化

修改 implementation-guide 各 skill 流程设计，末尾增加 scripts 使用说明表格：

```markdown
## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| <script-name> | <用途描述> | <调用时机> | 必须/可选 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
- 可选：agent 可判断是否需要调用，可用其他方式替代
```

### 3.3 约束说明强化

修改 scaffold-design §4.4：

```markdown
### 4.4 约束

- raw/ 目录不可变（用户管理）
- raw/.extracted/ 目录由 kb-ingest 维护（不手动修改）
- output/ 目录由用户管理（自行创建衍生文档）
- AGENTS.md 可修改（用户定制）
- skills-lock.json 自动维护（不手动修改）
- raw-registry.md 自动维护（kb-ingest/kb-compile 更新）

违反约定可能导致 migu 功能异常，需重新执行对应 skill 恢复。
```

---

## 4. 重构文档结构

### 4.1 scaffold-design 章节调整

| 章节 | 调整 |
|------|------|
| §1 项目定位 | 无变化 |
| §2 目录结构 | 无变化 |
| §3 脚手架架构 | 无变化 |
| §4 知识库架构 | §4.1 增加 output/ 定义、raw-registry.md 解析规范；§4.2 简化职责表；§4.3 删除 Karpathy 表改为引用；§4.4 强化约束说明 |
| §5 契约边界 | 无变化 |
| §6 关键设计决策 | 无变化 |
| **§7 扩展指南** | 新增（创建新 rules 类型指南） |
| **§8 错误处理策略** | 新增（错误类型 + 处理原则） |
| 附录 | 保留（引用 implementation-guide） |

### 4.2 implementation-guide 章节调整

| 章节 | 调整 |
|------|------|
| **开头 SKILL.md 编写模板** | 从附录移到开头，定义表格格式 |
| Karpathy 对应表 | 保留，作为实现层映射定义 |
| §1 kb-ingest | 适用范围改为引用；末尾增加 scripts 使用说明表格 |
| §2 kb-compile | 适用范围改为引用；末尾增加 scripts 使用说明表格 |
| §3 kb-lint | 适用范围改为引用；末尾增加 scripts 使用说明表格 |
| §4 kb-query | 适用范围改为引用；末尾增加 scripts 使用说明表格 |
| §5 kb-archive | 适用范围改为引用；末尾增加 scripts 使用说明表格 |
| §6 kb-status | 适用范围改为引用；末尾增加 scripts 使用说明表格 |

### 4.3 cross-reference 约定

两份文档之间的引用格式统一为：
- scaffold-design 引用 implementation-guide：`详见 implementation-guide §X.X`
- implementation-guide 引用 scaffold-design：`详见 scaffold-design §X.X`

---

## 5. 实施清单

### 5.1 scaffold-design 修改项

| 位置 | 修改内容 |
|------|---------|
| §4.1 | 新增 output/ 目录 subsection |
| §4.1 | 新增 raw-registry.md 解析规范 subsection |
| §4.1 | 修改 wiki 文档格式示例，标准化 source 字段 |
| §4.2 | 简化 skills 职责表（删除 scripts 列） |
| §4.3 | 删除 Karpathy 对应表，改为引用 |
| §4.4 | 强化约束说明，新增违反约定后果 |
| §7 | 新增扩展指南章节 |
| §8 | 新增错误处理策略章节 |
| structure.json 示例 | 新增 output 目录 |

### 5.2 implementation-guide 修改项

| 位置 | 修改内容 |
|------|---------|
| 开头 | 新增 SKILL.md 编写模板（从附录移入） |
| §1-6 | 适用范围改为引用 scaffold-design §4.2 |
| §1-6 | 末尾增加 scripts 使用说明表格 |
| 附录 | 删除（已移到开头） |