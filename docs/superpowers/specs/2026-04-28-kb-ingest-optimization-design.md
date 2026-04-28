# kb-ingest SKILL.md 优化设计

## 问题总结

| 问题 | 发现 | 解决方案 |
|------|------|----------|
| Product Path 格式 | 当前不含 `raw/`，kb-compile 可能解析错误 | Product Path 包含 `raw/` 前缀 |
| SKILL.md 冗余 | 类型判断、边界情况、返回值格式、registry 格式约定 4 个部分冗余 | 删除冗余部分 |

## Product Path 格式规范

### 格式约定

| 字段 | 格式 | 示例 | 用途 |
|------|------|------|------|
| File | wikilink `[[raw/<path>]]` | `[[raw/史记/本纪/秦本纪.md]]` | Obsidian 点击跳转 |
| Product Path | string path `raw/.extracted/<path>` | `raw/.extracted/史记/本纪/秦本纪.md` | kb-compile 直接拼接 |

### kb-compile 路径解析规则

**拼接规则**：
- File：解析 wikilink，提取 `<path>`，拼接 `kb_dir / <path>`
- Product Path：直接拼接 `kb_dir / product_path`

### 数据流

```
normalize_markdown.py 返回：
  {"output_path": ".extracted/史记/本纪/秦本纪.md"}  （不含 raw/）

update_registry.py 接收：
  --output ".extracted/史记/本纪/秦本纪.md"

format_entry() 格式化：
  Product Path: "raw/.extracted/史记/本纪/秦本纪.md"  （添加 raw/ 前缀）

raw-registry.md 存储：
  | ... | raw/.extracted/史记/本纪/秦本纪.md | ... |
```

## SKILL.md 冗余清理

### 冗余原则

**SKILL.md 应仅包含 agent 需要知道的内容**：
- 执行流程顺序
- 脚本调用方式
- 输出格式约定
- 成功标准

**不应包含的内容**：
- 脚本已处理的信息（类型判断、边界情况）
- 脚本内部实现细节（返回值具体字段）
- 脚本已保证的格式（registry 格式约定）

### 删除部分

| 部分 | 行数 | 删除理由 |
|------|------|----------|
| 类型判断 | 23-29 | scan_raw.py 输出 `文件路径|类型`，agent 无需判断 |
| 边界情况 | 31-37 | 脚本报错时 agent 根据错误输出自然处理 |
| normalize_markdown.py 返回值格式 | 52-65 | scripts 表格已说明返回 JSON，具体字段在脚本注释 |
| raw-registry.md 格式约定 | 67-79 | update_registry.py 脚本已处理格式转换 |

### 保留部分

| 部分 | 行数 | 保留理由 |
|------|------|----------|
| frontmatter | 1-5 | skill 元数据 |
| 职责 | 9-11 | 告诉 agent 做什么 |
| 执行流程 | 13-21 | 告诉 agent 执行顺序 |
| scripts 使用说明 | 39-51 | 告诉 agent 如何调用脚本 |
| 输出摘要 | 81-91 | 告诉 agent 完成后输出什么 |

### scripts 表格优化

**normalize_markdown.py 返回值列**：

当前：
```
stdout: JSON 状态，stderr: 日志
```

优化后：
```
stdout: JSON `{status, output_path, issues}`，stderr: 日志
```

## 修改清单

### update_registry.py

| 函数 | 修改内容 |
|------|----------|
| `to_wikilink()` | 新增：File 字段转换为 `[[raw/<path>]]` |
| `format_entry()` | File 使用 wikilink；Product Path 添加 `raw/` 前缀（如果以 `.extracted/` 开头） |

### test_update_registry.py

| 测试 | 修改内容 |
|------|----------|
| 所有测试 | Product Path 断言改为含 `raw/` 前缀 |
| 所有测试 | File 断言改为 wikilink 格式 |

### SKILL.md

| 部分 | 操作 |
|------|------|
| 类型判断（23-29行） | 删除 |
| 边界情况（31-37行） | 删除 |
| normalize_markdown.py 返回值格式（52-65行） | 删除 |
| raw-registry.md 格式约定（67-79行） | 删除 |
| scripts 表格 normalize_markdown.py 返回值列 | 补充 `{status, output_path, issues}` |

## 实现方式

**使用 skill-creator skill 进行实际的 kb-ingest skill 优化**，确保：
- skill 修改有正确的测评流程
- 边界情况测试覆盖 SKILL.md 定义的所有场景
- 测评使用独立 grader agent（避免主观偏见）