---
title: Skill Evaluation Constraints
created: 2026-04-27
type: spec
audience: migu skill 测评执行者
related_spec: docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
---

# Skill Evaluation Constraints

> 本 spec 定义 migu skills 测评的核心约束，确保测评结果客观可靠。
>
> 测评使用 skill-creator 提供的框架，本 spec 定义 migu 特定约束。

---

## 1. 断言设计规范

### 1.1 断言来源

所有断言必须引用 skill spec（SKILL.md）作为基准：
- **正确行为**：spec 明确定义的行为
- **边界处理**：spec 定义的边界情况处理方式
- **输出要求**：spec 定义的输出字段/格式

### 1.2 断言类型

仅验证**行为断言**（是否符合 spec），不验证主观指标：

| 断言类型 | 是否允许 | 示例 |
|---------|---------|------|
| 行为断言 | ✅ | "输出包含 raw 文件数量"（spec 定义） |
| 边界断言 | ✅ | "raw-registry.md 缺失时报错提示先执行 kb-ingest"（spec 定义） |
| 格式风格断言 | ❌ | "输出使用 box 格式"（主观风格偏好） |
| 非强制断言 | ❌ | "包含下一步提示"（非 spec 强制要求） |

### 1.3 断言格式

使用 skill-creator expectations 格式：
- `text`：断言文本（断言内容）
- `passed`：是否通过（由 grader 填入）
- `evidence`：验证依据（由 grader 填入）

断言文本应包含 spec 引用，例如：
- "输出包含 raw 文件数量（spec: SKILL.md 输出摘要 §1）"
- "raw-registry.md 缺失时报错提示先执行 kb-ingest（spec: SKILL.md 边界情况表格）"

---

## 2. 边界测试覆盖要求

### 2.1 覆盖原则

测评必须覆盖 skill spec（SKILL.md）中定义的所有边界情况：
- 每个边界情况至少有 1 个测试用例
- 测试用例必须验证 spec 定义的预期处理方式

### 2.2 边界测试用例设计

从 SKILL.md "边界情况" 表格提取测试场景：

| 测试场景 | 输入条件 | 预期行为（引用 spec） |
|---------|---------|---------------------|
| <边界情况名称> | <触发条件> | <spec 定义的处理方式> |

示例（kb-status）：
| 测试场景 | 输入条件 | 预期行为 |
|---------|---------|---------|
| raw-registry.md 缺失 | 知识库无 raw-registry.md | 报错退出，提示"先执行 kb-ingest" |
| index.md 缺失 | 知识库无 index.md | 报错退出，提示"先执行 kb-compile" |
| 无待处理文件 | 所有文件已处理 | 显示 "All up to date" |

### 2.3 测试覆盖报告

测评完成后生成覆盖报告：
- 已覆盖边界情况：X / Y
- 未覆盖边界情况列表（如有）
- 是否满足覆盖要求

---

## 3. 数据采集规范

### 3.1 timing 数据来源

timing 数据必须来自 subagent task notification（真实运行数据）：

| 数据来源 | 是否允许 |
|---------|---------|
| subagent 返回的 total_tokens 和 duration_ms | ✅ |
| 手动估算填入 | ❌ |

采集时机：subagent task 完成时立即保存到 `timing.json`

### 3.2 grading 执行方式

grading 应使用独立 agent 执行，避免当前 session 的主观偏见：

| 执行方式 | 是否允许 |
|---------|---------|
| spawn grader subagent，读取 agents/grader.md 执行 grading | ✅ |
| 当前 session 人工判定 grading.json | ❌ |

grader agent 职责：
- 接收 expectations 参数（含 spec 引用）
- 根据 expectations 中引用的 spec 验证每个断言
- 输出 grading.json（含 summary，使用 text/passed/evidence 字段）

### 3.3 数据一致性检查

benchmark 生成前验证：
- `timing.json` 存在且数值合理（duration > 0）
- `grading.json` 存在且含 summary 字段
- expectations 使用正确字段名（text, passed, evidence）

---

## 4. 测评流程总结

完整测评流程（结合 skill-creator 框架）：

1. **准备阶段**
   - 阅读 skill SKILL.md，提取边界情况表格
   - 设计测试用例（正常 + 边界）
   - 设计断言（引用 spec）

2. **执行阶段**
   - Spawn with-skill 和 baseline subagent（并行）
   - 采集 timing 数据（subagent notification）
   - 保存到 eval directories

3. **评分阶段**
   - Spawn grader subagent（独立 agent）
   - 验证断言是否符合 spec
   - 输出 grading.json

4. **汇总阶段**
   - 运行 aggregate_benchmark.py
   - 生成 benchmark.json 和 benchmark.md
   - 生成边界覆盖报告

5. **评审阶段**
   - 运行 generate_review.py（eval viewer）
   - 用户评审输出，提供反馈

---

## 5. 测评产出

每次测评产出：
- `evals.json`：测试用例和断言定义
- `benchmark.json`：定量结果（pass_rate, timing, tokens）
- `benchmark.md`：人类可读摘要
- `coverage-report.md`：边界测试覆盖情况
- `review.html`：eval viewer（或 feedback.json）