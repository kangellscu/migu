---
title: kb-archive Skill 优化设计
created: 2026-04-27
type: spec
status: draft
version: 1.1
related_specs:
  - docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
  - docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
---

# kb-archive Skill 优化设计

## 1. 问题背景

kb-archive skill 在实际测试评估中发现两类问题，影响 Pass Rate（当前 90%）。

### P0 遗漏问题

| 问题 | 描述 | 影响 |
|------|------|------|
| index.md 未更新 | synthesis 报告不在索引中 | 用户无法通过 index.md 发现新报告 |
| log.md 未更新 | 操作记录缺失 | 无法追溯 archive 操作历史 |

**根本原因**：SKILL.md 步骤 7 虽然提到"更新 index.md"，但未强调必须执行，缺少验证机制。

### P1 质量问题

| 问题 | 代码位置 | 影响 |
|------|----------|------|
| 重复 frontmatter | scripts/create_synthesis.py | 文件格式不规范，包含双重 frontmatter |
| 换行符未处理 | scripts/update_entity.py | 实体页面添加的章节格式错误（`\n` 未转换） |

### 与 kb-compile 对比

kb-compile 在 iteration-3 测试时也发现类似问题，解决方案：
- SKILL.md 步骤 5、6 强调"必须执行"
- 添加评估检查项：`updates-root-index-md`、`updates-root-log-md`
- 测试用例覆盖检查项

---

## 2. 优化目标

1. **确保流程完整性**：index.md 和 log.md 更新必须执行
2. **提升输出质量**：修复 scripts 质量问题
3. **保持一致性**：与 kb-compile 处理方式一致（LLM agent 手动更新，无专门脚本）
4. **提升评估覆盖率**：添加检查项和测试用例

---

## 3. 改进范围

参照 kb-compile iteration-3 做法，采用标准方案：

- SKILL.md：强调流程、添加输出验证
- Scripts：修复质量问题
- 评估检查项：添加 `updates-root-index-md` 和 `updates-root-log-md`
- 测试用例：覆盖 index.md/log.md 检查

**不添加**：专门脚本（与 kb-compile 保持一致）

---

## 4. SKILL.md 改进

### 4.1 流程强化

在现有执行流程步骤 7 后，新增两个步骤并强调必须执行：

**新增步骤 8**：更新根目录 index.md，将新 synthesis 报告添加到 synthesis section，标记为必须执行。

**新增步骤 9**：更新根目录 log.md，追加 archive 操作记录，标记为必须执行。

### 4.2 输出验证章节

新增章节"输出验证"，要求完成后输出验证信息：

**验证项**：
- synthesis 文件创建状态（路径确认）
- index.md 更新状态（synthesis section）
- log.md 更新状态
- 实体页面更新数量

**输出格式**：先输出处理结果摘要，再逐项验证，最后给出下一步提示。

### 4.3 index.md 更新意图

LLM agent 应在根目录 index.md 的 synthesis section 添加新条目：

**条目内容**：报告标题 wikilink + 简短摘要 + 更新日期。

**格式要求**：遵循现有 index.md entry 格式（wikilink + 摘要 + 日期）。

### 4.4 log.md 更新意图

LLM agent 应在根目录 log.md 追加 archive 操作记录：

**记录内容**：日期 + archive 操作标识 + 生成的 synthesis 报告标题 + 更新的实体数量和列表。

**格式要求**：遵循现有 log.md entry 格式（日期标记 + 操作类型 + 详情）。

---

## 5. Scripts 质量修复

### 5.1 create_synthesis.py 改进

**问题**：直接将 stdin 内容写入文件，导致重复 frontmatter（原始 report frontmatter + 新 synthesis frontmatter）。

**修复意图**：

脚本应在写入前过滤输入内容中已存在的 YAML frontmatter（以 `---` 标记的段落），只保留正文内容，然后添加新的 synthesis frontmatter（包含 title、type、date 字段）。

**预期结果**：生成的 synthesis 文件包含单一 frontmatter，无重复。

### 5.2 update_entity.py 改进

**问题**：命令行参数传递内容时 `\n` 字符未转换为实际换行符。

**修复意图**：

脚本应改为从 stdin 读取要添加的内容，而非命令行参数。参数仅需实体文件路径。内容通过管道传入，确保换行符正确处理。

**内容插入位置**：在实体文件末尾的"来源"章节前插入新内容，如无"来源"章节则追加到文件末尾。

**预期结果**：实体页面新章节格式正确，换行符正确转换。

---

## 6. 评估检查项与测试用例

### 6.1 评估检查项

参照 kb-compile iteration-3，新增以下检查项：

| 检查项名称 | 检查内容 |
|-----------|----------|
| synthesis-created | synthesis 报告是否创建在 wiki/synthesis/ 目录 |
| synthesis-quality | synthesis 文件是否包含单一 frontmatter（无重复） |
| entities-updated | 实体页面是否更新，包含新章节 |
| updates-root-index-md | 根目录 index.md synthesis section 是否包含新报告索引 |
| updates-root-log-md | 根目录 log.md 是否包含 archive 操作记录 |

### 6.2 测试用例

新增测试用例覆盖以下场景：

| 测试场景 | 输入 | 预期输出 |
|---------|------|---------|
| 有 report 执行 archive | test-report.md | synthesis 创建、实体更新、格式正确 |
| 无 report 执行 archive | 无 | 提示 report 不存在、终止执行、无文件创建 |
| 验证 index.md/log.md 更新 | test-report.md | index.md synthesis section 包含索引、log.md 包含记录 |

---

## 7. 实施约束

### 7.1 不添加专门脚本

与 kb-compile 保持一致：
- index.md 和 log.md 由 LLM agent 手动更新
- 不添加 update_index.py 或 update_log.py
- 通过 SKILL.md 强调和评估检查项确保执行

### 7.2 前置条件

- kb-query 生成的 report 可包含 frontmatter（create_synthesis.py 会过滤）
- synthesis section 需存在或由 agent 添加（如不存在）

---

## 8. 实施原则

### 8.1 使用 skill-creator skill

实施优化时应使用 skill-creator skill 进行实际的优化工作，遵循 skill-creator 的评估流程：
- 运行测试用例
- 使用 eval-viewer 展示结果
- 根据反馈迭代改进
- 达到 Pass Rate 100%

---

## 9. 验收标准

优化完成后应达到：

| 标准 | 目标 |
|------|------|
| Pass Rate | 100% |
| 所有检查项通过 | synthesis-created, synthesis-quality, entities-updated, updates-root-index-md, updates-root-log-md |
| 与 kb-compile 一致 | 处理方式、评估检查项、测试用例覆盖 |
| Scripts 质量 | create_synthesis.py 无重复 frontmatter，update_entity.py 正确处理换行 |