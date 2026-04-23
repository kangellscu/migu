---
name: kb-lint
description: "Check wiki pages for syntax errors (wikilink format, frontmatter) and semantic issues (orphan pages, missing sources). Use when user asks to lint wiki, check format, fix errors, or verify knowledge base quality."
version: 1.0
---

# kb-lint

## 职责

Wiki 检查（语法、语义、修复）。

## 执行流程

1. **扫描 wiki/ 目录**：获取所有 wiki 文档
2. **语法检查**：调用 `syntax.py` 检查 markdown 格式、链接有效性、source 字段
3. **语义检查**：调用 `semantic.py` 检查内容一致性、模板结构
4. **报告问题**：汇总检查结果，呈现给用户
5. **可选修复**：调用 `fix.py` 自动修复可修复的问题

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| lint.py | 协调检查流程（syntax + semantic） | 步骤 2-3：启动检查 | 必须 |
| syntax.py | 语法检查 | 步骤 2：检查 markdown 格式、链接 | 必须 |
| semantic.py | 语义检查 | 步骤 3：检查内容一致性 | 必须 |
| fix.py | 自动修复 | 步骤 5：可选修复可修复问题 | 可选 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
- 可选：agent 可判断是否需要调用

## 输出摘要

完成后输出：
1. **处理结果**：X 个问题，Y 个已修复
2. **下一步提示**：可运行 kb-query 查询知识库，或运行 kb-archive 进行综合分析

示例：
```
处理结果：3 个问题，2 个已修复
下一步提示：可运行 kb-query 查询知识库，或运行 kb-archive 进行综合分析
```
