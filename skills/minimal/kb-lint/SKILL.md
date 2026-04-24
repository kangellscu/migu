---
name: kb-lint
description: "Check and validate wiki pages in a knowledge base. Detects syntax errors (wikilink imbalance, missing sources), structure issues (orphan pages, broken wikilinks, missing titles), and provides repair suggestions. Use whenever user mentions: lint wiki, check wiki, 检查知识库, 知识库质量, wiki有问题, orphan pages, broken wikilinks, 格式错误, or wants to validate/fix wiki pages. Supports modes: 'lint wiki' (summary), 'lint 详细' (detailed report), 'lint 建议' (suggestions), 'lint 并修复' (auto-fix). NOT for: writing wiki pages, compiling from raw, ingesting files, querying content, archiving analysis, code linting, or general markdown formatting."
version: 2.0
---

# kb-lint

## 职责

Wiki 检查（语法、语义、修复），支持分层检测和分级报告。

## 意图识别

根据用户输入识别执行模式：

| 用户意图 | 执行方式 | 输出内容 |
|---------|---------|---------|
| "lint wiki" | 检测所有问题 | 仅摘要 |
| "lint 详细" | 检测所有问题 | 完整报告 |
| "lint 建议" | 检测所有问题 | 摘要 + 结构问题建议 |
| "lint 并修复" | 检测 + 自动修复格式问题 | 摘要 + 修复结果 |

触发词示例：
- 默认："lint wiki"、"检查 wiki"
- 详细："lint 详细"、"完整检查"
- 建议："lint 建议"、"检查建议"
- 修复："lint 并修复"、"检查并修复"

## 执行流程

1. **扫描 wiki/ 目录**：获取所有 wiki 文档
2. **格式检查**：wikilink 不平衡、缺失 source
3. **结构检查**：orphan pages、broken wikilinks、缺失 title
4. **内容检查**：语义问题（需要 LLM）
5. **报告问题**：根据模式输出摘要或详细报告
6. **可选修复**：调用 `fix.py` 自动修复格式问题

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| lint.py | 协调检查流程 | 默认启动 | 必须 |
| fix.py | 自动修复 | 意图"lint 并修复" | 可选 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script
- 可选：agent 可判断是否需要调用

## 问题分类

| 问题类型 | 确定性程度 | 检测方式 | 修复方式 |
|---------|-----------|---------|---------|
| 格式问题 | 高 | scripts | 自动修复 |
| 结构问题 | 中 | scripts | 输出建议 |
| 内容问题 | 低 | LLM | 仅提示 |

## 输出摘要

完成后输出：
1. **处理结果**：X 个格式问题（可自动修复），Y 个结构问题（建议修复），Z 个内容问题（需人工修复）
2. **下一步提示**：
   - 格式问题：执行 "lint 并修复" 自动修复
   - 结构问题：执行 "lint 建议" 查看修复建议
   - 内容问题：需人工判断处理