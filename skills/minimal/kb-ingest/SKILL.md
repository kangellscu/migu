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
   - **markdown**：调用 `normalize_markdown.py` 检查 BOM 和康熙部首/CJK 部首。有修复时输出到 `raw/.extracted/`，返回 JSON 状态；无修复时不输出，返回 status: skipped。然后调用 `update_registry.py` 更新 registry。
   - **PDF**：调用 `convert_pdf.py` 转换为 markdown，输出到 raw/.extracted/，调用 `update_registry.py` 更新 registry。
   - **image**：无需处理，直接引用，调用 `update_registry.py` 记录（status: skipped）
4. **更新 log.md**（根目录）：追加 ingest 操作记录

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

| script | 用途 | 调用时机 | 参数 | 依赖类型 | 返回值 |
|--------|------|---------|------|---------|--------|
| scan_raw.py | 扫描 raw/ 目录，检测新文件 | 步骤 1：检测新文件 | <kb_dir> | 必须 | stdout: 文件路径|类型 |
| validate_batch.py | 验证 raw-registry.md 格式 | 步骤 3 后：整体验证 | - | 可选 | 无 |
| normalize_markdown.py | 规范化 markdown 文件 | 步骤 3：处理 markdown | <input_file> <raw_dir> | 必须 | stdout: JSON 状态，stderr: 日志 |
| convert_pdf.py | 转换 PDF 为 markdown | 步骤 3：处理 PDF | - | 必须 | 无 |
| update_registry.py | 更新 raw-registry.md 条目 | 步骤 3：每个文件处理后 | <kb_dir> --file <path> --type <type> --status <status> [--output <path>] | 必须 | stdout: 更新确认 |

依赖类型说明：
- 必须：流程步骤明确依赖该 script

## normalize_markdown.py 返回值格式

stdout 输出 JSON：
```json
{
  "status": "processed" | "skipped",
  "output_path": ".extracted/path/to/file.md" | null,
  "issues": ["bom"] | ["radicals"] | ["bom", "radicals"] | []
}
```

stderr 输出日志：
- 有修复：`FIXED: <input> -> <output>`
- 无修复：`OK: <input>`

## raw-registry.md 格式约定

| 字段 | 格式 | 示例 |
|------|------|------|
| File | wikilink `[[raw/<path>]]` | `[[raw/史记/本纪/秦本纪.md]]` |
| Product Path | string path（无 `[[]]`）或 `-` | `.extracted/史记/本纪/秦本纪.md` 或 `-` |

**说明**：
- File 使用 wikilink：便于 Obsidian 点击跳转到源文件
- Product Path 使用 string path：便于 agent 解析和处理

**错误示例**（Product Path 不要使用 wikilink）：
- `[[raw/.extracted/史记/本纪/秦本纪.md]]` ❌

## 输出摘要

完成后输出：
1. **处理结果**：已处理 X 个文件，Y 个需转换
2. **下一步提示**：可运行 kb-compile 开始编译，或运行 kb-lint 检查知识库健康度

示例：
```
处理结果：已处理 5 个文件，2 个需转换
下一步提示：可运行 kb-compile 开始编译，或运行 kb-lint 检查知识库健康度
```
