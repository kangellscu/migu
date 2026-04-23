---
name: kb-status
description: "Show knowledge base dashboard with file counts and processing status. Use when user asks to check KB status, see statistics, view dashboard, or wants overview of raw files and wiki pages."
version: 1.0
---

# kb-status

## 职责

展示知识库仪表盘（解析 index.md + raw-registry.md）。

## 执行流程

1. **解析 raw-registry.md**：调用 `read_registry.py` 统计 raw 文件数量、类型分布、处理状态
2. **解析 index.md**：调用 `read_index.py` 统计 wiki 文档数量、分类分布
3. **格式化输出**：将结果管道给 `format_dashboard.py` 生成仪表盘

## 边界情况

| 场景 | 处理方式 |
|------|----------|
| raw-registry.md 不存在 | 报错退出，提示用户先执行 kb-ingest |
| index.md 不存在 | 报错退出，提示用户先执行 kb-compile |
| 无待处理文件 | 显示 "All up to date" |

## scripts 使用说明

| script | 用途 | 调用时机 | 依赖类型 |
|--------|------|---------|---------|
| read_registry.py | 解析 raw-registry.md | 步骤 1：统计 raw 文件状态 | 必须 |
| read_index.py | 解析 index.md | 步骤 2：统计 wiki 文档状态 | 必须 |
| format_dashboard.py | 格式化仪表盘输出 | 步骤 3：生成仪表盘 | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script

## 输出摘要

完成后输出：
1. **处理结果**：状态：X 个 raw 文件（Y 待处理），Z 个 wiki 文档
2. **下一步提示**：可运行 kb-ingest 处理 raw 文件，或运行 kb-compile 开始编译

示例：
```
处理结果：状态：10 个 raw 文件（5 待处理），8 个 wiki 文档
下一步提示：可运行 kb-ingest 处理 raw 文件，或运行 kb-compile 开始编译
```
