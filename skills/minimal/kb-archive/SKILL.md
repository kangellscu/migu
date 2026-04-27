---
name: kb-archive
description: "Write synthesis reports and integrate findings back into wiki entity pages. Use when user asks to archive findings, write synthesis, summarize research, or integrate analysis into knowledge base."
version: 1.0
---

# kb-archive

## 职责

接收 report + 回写摘要 + 有机融入。

## 会话依赖

kb-archive 必须在 kb-query 执行后的同一 agent session 中执行。

## 执行流程

1. **检查 report 是否存在**：
   - report 在 agent 上下文中：继续执行
   - report 不存在：输出提示并终止
2. **接收 report**：调用 `read_report.py` 读取 agent 上下文中的 report
3. **解析回写建议**：提取 report 中的回写建议列表
4. **生成回写摘要**：呈现给用户
5. **询问用户是否执行回写**：
   - `yes`：执行所有回写
   - `no`：只创建 synthesis 报告
   - `selective`：逐个确认
6. **根据选择执行**：
   - 调用 `create_synthesis.py` 创建 synthesis 文件（不含回写建议）
   - 调用 `update_entity.py` 有机融入 wiki 实体文档
8. **更新 index.md**（根目录）：添加新页面索引到 synthesis section ⚠️ **必须执行**
  9. **更新 log.md**（根目录）：追加 archive 操作记录 ⚠️ **必须执行**

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_report.py | 读取 report 内容 | 步骤 2：从 agent 上下文读取 | 必须 |
| create_synthesis.py | 创建 synthesis 文件 | 步骤 6：创建 synthesis 报告 | 必须 |
| update_entity.py | 有机融入 wiki 文档 | 步骤 6：执行回写建议 | 必须 |

## 输出摘要

完成后输出：
1. **处理结果**：生成 X 个 synthesis 报告，更新 Y 个实体页面
2. **下一步提示**：可运行 kb-status 查看知识库状态，或运行 kb-lint 检查健康度

**Synthesis 页面类型**：kb-archive 生成的分析页面存储在 `wiki/synthesis/`，通过 frontmatter type 字段区分：
- `synthesis`: 综合分析报告
- `comparison`: 对比分析
- `overview`: 概述页面

示例：
```
处理结果：生成 2 个 synthesis 报告，更新 3 个实体页面
下一步提示：可运行 kb-status 查看知识库状态，或运行 kb-lint 检查健康度
```

## 输出验证

完成后必须输出以下验证信息：
- ✓ synthesis 文件: wiki/synthesis/xxx.md (已创建)
- ✓ index.md (已更新 - synthesis section)
- ✓ log.md (已更新)
- ✓ 实体更新: X 个实体页面 (已更新/无更新)

格式示例：
```
处理结果：生成 1 个 synthesis 报告，更新 4 个实体页面
验证：✓ wiki/synthesis/楚汉战争关键人物决策分析.md 已创建
      ✓ index.md synthesis section 已更新
      ✓ log.md 已追加 archive 记录
下一步提示：可运行 kb-status 查看知识库状态
```
