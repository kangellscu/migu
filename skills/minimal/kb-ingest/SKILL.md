---
name: kb-ingest
description: "Scan raw/ directory, preprocess files (normalize markdown, convert PDF, fix CJK radicals), output to raw/.extracted/, and update raw-registry.md. Use when user asks to ingest files, process raw sources, or prepare files for compilation."
version: 1.0
---

# kb-ingest

## 职责

扫描 raw/、预处理文件、输出到 raw/.extracted/，更新 raw-registry.md。

## 执行流程

1. **扫描 raw/ 目录**：调用 `scan_raw.py` 检测所有文件（递归，排除 .extracted/）
2. **对比 raw-registry.md**：找出未记录的文件，准备添加新条目
3. **处理文件**：
   - **markdown**：调用 `normalize_markdown.py` 检查编码、转换 CJK 部首，输出到 raw/.extracted/（如有修复）
   - **PDF**：调用 `convert_pdf.py` 转换为 markdown，输出到 raw/.extracted/
   - **image**：无需处理，直接引用
4. **验证**：调用 `validate_batch.py` 检查 raw-registry.md 格式
5. **更新 raw-registry.md**：
   - 预处理状态：已处理 / 无需处理
   - 产物路径：有产物时记录路径，无产物时 `-`
   - 最近处理日期：当前日期

## 类型判断

| 扩展名 | 类型 | 处理方式 |
|--------|------|---------|
| .md | markdown | 规范化检查，可能生成 raw/.extracted/ |
| .pdf | pdf | 转 markdown + 提取图片 → raw/.extracted/ |
| .png, .jpg, .gif | image | 无需处理，直接引用 |

## 边界情况

| 场景 | 处理方式 |
|------|----------|
| raw/ 目录为空 | 输出 "No files to process" |
| raw-registry.md 格式错误 | validate_batch.py 报错退出 |
| 文件已存在 .extracted/ 版本 | 跳过，除非重新处理 |

## scripts 使用说明

| script | 用途 | 调用时机 | 参数 | 依赖类型 |
|--------|------|---------|------|---------|
| scan_raw.py | 扫描 raw/ 目录，检测新文件 | 步骤 1：检测新文件 | <kb_dir> | 必须 |
| validate_batch.py | 验证 raw-registry.md 格式 | 步骤 4：验证格式 | - | 必须 |
| normalize_markdown.py | 规范化 markdown 文件 | 步骤 3：处理 markdown | - | 必须 |
| convert_pdf.py | 转换 PDF 为 markdown | 步骤 3：处理 PDF | - | 必须 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script

## 输出摘要

完成后输出：
1. **处理结果**：已处理 X 个文件，Y 个需转换
2. **下一步提示**：可运行 kb-compile 开始编译，或运行 kb-lint 检查知识库健康度

示例：
```
处理结果：已处理 5 个文件，2 个需转换
下一步提示：可运行 kb-compile 开始编译，或运行 kb-lint 检查知识库健康度
```
