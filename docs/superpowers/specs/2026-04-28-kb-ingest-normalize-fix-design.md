# kb-ingest normalize_markdown.py 输出逻辑修正设计

## 问题诊断

**当前流程缺陷**：
- normalize_markdown.py 无条件输出：即使文件无需修复，也创建 `.extracted/` 产物
- 状态传递缺失：normalize_markdown.py 不返回处理结果，kb-ingest 无法正确更新 registry
- registry 状态混淆：无法区分"已处理有产物"与"检查过无需处理"

**问题影响**：
- 存储浪费：每个 markdown 文件都创建副本，即使无修改
- registry 状态不清晰：无法正确记录处理状态
- kb-compile 读取路径混乱：不知道应该读 raw/ 还是 `.extracted/`

## 设计决策

| 项目 | 决策 |
|------|------|
| 判断条件 | BOM + CJK 部首（保持简单） |
| 状态设计 | 二元：processed / skipped |
| 输出行为 | 有修复才输出到 `.extracted/` |
| 返回格式 | JSON（status、output_path、issues） |
| registry 记录 | string path 格式（如 `.extracted/史记/本纪/项羽本纪.md`） |
| 目录命名 | 保持 `.extracted/`（隐藏目录，agent 可访问，用户可选择性查看） |
| 下游读取 | kb-compile 根据状态决定路径 |

## 修改后流程意图

**文件处理路径**：
- 无修复的文件：normalize_markdown.py 检测后返回 `skipped` 状态，kb-ingest 不创建产物，registry 记录 `-`
- 有修复的文件：normalize_markdown.py 检测后返回 `processed` 状态，kb-ingest 创建产物，registry 记录路径

**状态传递机制**：
- normalize_markdown.py 必须返回结构化状态信息
- kb-ingest 调用逻辑必须接收状态，并据此更新 raw-registry.md

**下游消费约束**：
- kb-compile 根据 registry 中的 status 决定读取路径
- `processed` → 读 `.extracted/` 产物
- `skipped` → 读 `raw/` 原文件

## normalize_markdown.py 修改约束

### 判断条件

**需要修复的条件**（满足任一即需修复）：
- 文件包含 BOM（`\ufeff` UTF-8 BOM 前缀）
- 文件包含康熙部首/CJK 部首（需要转换为统一汉字）

### 输出行为约束

**输出时机**：
- 有修复：必须创建 `.extracted/` 目录下的产物文件，路径与原文件相对路径一致
- 无修复：不创建任何产物文件，不创建 `.extracted/` 子目录

**输出内容**：
- BOM 移除后的内容
- CJK 部首转换后的内容（康熙部首 → 统一汉字）

### 返回值约束

**必须返回 JSON 结构**，包含：
- `status`：`"processed"` 或 `"skipped"`
- `output_path`：产物路径（有产物时为完整路径字符串，如 `.extracted/史记/本纪/项羽本纪.md`，无产物时为 `null`）
- `issues`：检测到的问题类型列表（如 `["bom"]`、`["radicals"]`、`["bom", "radicals"]`，无问题时为空列表 `[]`）

### 调用方式约束

**保持命令行调用方式**：
- 输入参数：源文件路径、输出目录路径
- 输出方式：JSON 结果打印到 stdout，日志信息打印到 stderr

## kb-ingest 调用逻辑修改约束

### 状态接收约束

**必须解析 normalize_markdown.py 的 JSON 返回**：
- 从 stdout 读取 JSON 结果
- 解析 status、output_path、issues 字段

### registry 更新约束

**raw-registry.md 记录内容**（每个文件条目）：
- 文件路径（相对于 `raw/`）
- status：`processed` 或 `skipped`
- output_path：string path 格式（如 `.extracted/史记/本纪/项羽本纪.md`），无产物时为 `-`
- processed_date：处理日期

**更新时机**：
- 每处理完一个文件，立即更新该文件在 registry 中的条目

### 错误处理约束

**normalize_markdown.py 执行失败**：
- registry 不更新该文件条目
- log.md 记录失败原因
- 继续处理下一个文件（不中断整体流程）

## SKILL.md 更新约束

### 需要明确的内容

**步骤 3 处理文件描述**：
- 明确"如有修复"的判断条件（BOM + CJK 部首）
- 明确无修复时不输出

**normalize_markdown.py 返回值约定**：
- 补充说明：返回 JSON 状态（status、output_path、issues）
- 补充说明：JSON 输出到 stdout，日志输出到 stderr

**scripts 使用说明表格**：
- 补充 normalize_markdown.py 的返回值说明

### 不需要修改的内容

- 类型判断表格（扩展名处理方式不变）
- 边界情况表格（逻辑不变）
- 其他步骤描述

## 实现方式

**使用 skill-creator skill 处理实际的 kb-ingest 优化迭代工作**，确保：
- skill 修改有正确的测评流程
- 边界情况测试覆盖 SKILL.md 定义的所有场景
- 测评使用独立 grader agent，避免主观偏见