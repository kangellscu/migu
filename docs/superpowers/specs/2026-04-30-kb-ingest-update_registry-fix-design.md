---
title: kb-ingest update_registry.py Bug 分析报告
date: 2026-04-30
type: bug-report
---
# kb-ingest update_registry.py Bug 分析报告

## 问题概述

### 发现时间
2026-04-30，执行 kb-ingest 操作时

### 问题表现
kb-ingest 处理两个新文件时（`Ontology Design Best Practices - Part I.md` 和 `Ontology Design Best Practices - Part II.md`），`raw-registry.md` 只成功记录了 Part I.md，Part II.md 条目丢失。

### 影响范围
- 连续多次调用 `update_registry.py` 时，第二次及后续调用可能丢失新条目
- 影响 kb-ingest 流程的可靠性

---

## 根因分析

### 问题代码位置
文件：`.agents/skills/kb-ingest/scripts/update_registry.py`
函数：`parse_registry()` (第 42-74 行)
问题行：第 50 行、第 53 行

```python
# 问题1：标题行匹配
if line.startswith('| File |'):
    in_table = True
    header_lines.append(line)

# 问题2：分隔符行匹配
elif line.startswith('|------|'):
    header_lines.append(line)
```

### 问题机制

#### 问题1：标题行匹配失败
第一次写入后，标题行格式化为：`| File                                                                              | Type     | ...`
`startswith('| File |')` 匹配失败。

#### 问题2：分隔符行匹配失败
格式化后的分隔符行：`| --------------------------------------------------------------------------------- | -------- |`
`startswith('|------|')` 也匹配失败。

#### 第一次调用流程
1. `raw-registry.md` 标题行为原始格式：`| File | Type | Summary | ...`
2. `startswith('| File |')` 匹配成功
3. `in_table = True`，正确解析表格
4. `entries` 包含原有条目
5. 新条目成功添加
6. `format_entry()` 格式化输出，列对齐（添加空格）

#### 第一次写入后的表格格式
```markdown
| File                                                                              | Type     | Summary | Preprocess Status | Product Path | Compile Status | Last Processed | Remaining Omissions |
| --------------------------------------------------------------------------------- | -------- | ------- | ----------------- | ------------ | -------------- | -------------- | ------------------- |
```

#### 第二次调用（Part II.md）
1. 标题行已格式化：`| File                                                                              | Type     | ...`
2. `startswith('| File |')` 匹配失败（因为 '| File |' vs '| File                                                                              |')
3. 标题行进入 `else` 分支，添加到 `header_lines`
4. `in_table` 保持 `False`
5. 所有表格行（包括分隔符和原有条目）也进入 `else` 分支
6. `entries` 为空列表
7. 写入逻辑中查找 `table_start`：
   ```python
   for i, line in enumerate(new_lines):
       if line.startswith('| File |'):
           table_start = i
           break
   ```
   `table_start = None`（因为标题行已格式化）
8. `new_lines` 保持为 `header_lines`（包含原有5个表格行）
9. 新添加的 Part II 条目从未写入

### 流程图

```
第一次调用
┌─────────────────────────────────────────────────────┐
│  标题行: | File | Type | ...                        │
│  startswith('| File |') → True                      │
│  in_table = True                                    │
│  entries = [原有条目]                                │
│  成功添加新条目                                       │
│  format_entry() 输出格式化行（空格对齐）               │
└─────────────────────────────────────────────────────┘

第二次调用
┌─────────────────────────────────────────────────────┐
│  标题行: | File                                                | Type     | ... │
│  startswith('| File |') → False                        │
│  进入 else 分支 → header_lines                          │
│  in_table = False                                      │
│  entries = []                                           │
│  table_start = None                                     │
│  new_lines = header_lines (原有表格行)                   │
│  新条目丢失                                              │
└─────────────────────────────────────────────────────┘
```

---

## 修复方案

### 方案一：修改标题行和分隔符行匹配逻辑（已实施）

修改 `parse_registry()` 第 50 行和第 53 行：

```python
# 原代码
if line.startswith('| File |'):
    in_table = True
    header_lines.append(line)
elif line.startswith('|------|'):
    header_lines.append(line)

# 修复后
if line.startswith('| File') and 'Type' in line:
    in_table = True
    header_lines.append(line)
elif line.startswith('|') and '---' in line and line.count('---') >= 3:
    header_lines.append(line)
```

**优点**：
- 标题行匹配更宽松，兼容格式化后的标题行
- `and 'Type' in line` 防止误匹配其他表格
- 分隔符行检测包含多个 `---` 的行，兼容所有格式
- 最小改动，风险低

**测试验证**：
```python
# 标题行
line1 = '| File | Type | Summary | ...'
line2 = '| File                                                                              | Type     | Summary | ...'
line1.startswith('| File') and 'Type' in line1  # True
line2.startswith('| File') and 'Type' in line2  # True

# 分隔符行
line3 = '|------|------|------|...'
line4 = '| --------------------------------------------------------------------------------- | -------- | ------- |'
line3.startswith('|') and '---' in line3 and line3.count('---') >= 3  # True
line4.startswith('|') and '---' in line4 and line4.count('---') >= 3  # True
```

### 方案二：简化写入逻辑（可选）

第 143-146 行代码逻辑混乱，可简化：

```python
# 原代码
if table_start is not None:
    new_lines = new_lines[:table_start + 2]
    for entry in entries:
        new_lines.append(format_entry(entry))
    
    remaining_lines = header_lines[table_start + 2:]
    for entry in entries[:table_start + 2]:
        remaining_lines = remaining_lines[len(entries):]
    new_lines.extend(remaining_lines)

# 简化后
if table_start is not None:
    new_lines = new_lines[:table_start + 2]
    for entry in entries:
        new_lines.append(format_entry(entry))
```

**注意**：方案一修复后，方案二可选（不影响功能）

---

## 实施建议

### 必须修复
- 方案一：标题行匹配逻辑

### 可选优化
- 方案二：简化写入逻辑

### 测试步骤
1. 修复后重新运行 kb-ingest
2. 验证两个文件都成功写入 raw-registry.md
3. 检查 raw-registry.md 条目完整性

---

## 相关文件

- Bug 文件：`.agents/skills/kb-ingest/scripts/update_registry.py`
- 受影响流程：kb-ingest
- 测试文件：`raw-registry.md`

---

## 总结

| 项目 | 内容 |
|------|------|
| 问题类型 | 标题行和分隔符行格式兼容性问题 |
| 根因 | 硬编码匹配字符串不兼容格式化输出（两个问题点） |
| 严重程度 | 中等（影响连续调用可靠性） |
| 修复难度 | 低（两行代码修改） |
| 修复状态 | 已完成 |
| 修复方案 | 标题行和分隔符行匹配改为宽松模式 |