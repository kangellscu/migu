---
name: kb-query
description: "Search wiki pages with optional raw source backtracking. Use when user asks to query knowledge base, search entities, find information, or look up historical figures/events."
version: 1.0
---

# kb-query

## 职责

Wiki 查询 + 回溯模式 + 生成 report。

## 执行流程

1. **接收查询意图**：用户提出问题
2. **解析意图**：识别查询对象、范围、方式、回溯关键词
3. **【含回溯关键词】询问用户**：是否需要回溯 raw 文件？
4. **搜索 wiki/**：调用 `search_wiki.py` 根据意图匹配文档
5. **聚合结果**：汇总查询结果
6. **【查询结果为空】输出提示并终止**："未找到相关实体，建议检查 raw 是否已 compile"
7. **生成 report**（符合 report-template.md）
8. **【标准模式】输出疑似缺失提示**

## 回溯范围限制

| 限制类型 | 规则 | 超出处理 |
|---------|------|---------|
| 数量限制 | 最多 5 个唯一 raw 文件 | 提示用户选择优先哪些 |
| 大小限制 | 单文件不超过 50KB | 提示用户确认是否处理 |

## 边界情况

| 场景 | 输出 |
|------|------|
| wiki 无相关实体 | "未找到相关实体，建议检查 raw 是否已 compile" |
| 回溯无新发现 | "raw 回溯完成，无新发现信息" |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| search_wiki.py | 搜索 wiki 目录 | 步骤 4：根据意图匹配文档 | 可选（可替代为 grep） |

依赖类型说明：
- 可选：agent 可判断是否需要调用，可用其他方式替代

## 输出摘要

完成后输出：
1. **处理结果**：找到 X 个相关文档
2. **下一步提示**：可运行 kb-archive 进行综合分析，或继续查询其他内容

示例：
```
处理结果：找到 5 个相关文档
下一步提示：可运行 kb-archive 进行综合分析，或继续查询其他内容
```
