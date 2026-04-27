# kb-archive Skill 评估总结与改进建议

## 评估概况

**测试轮次**: 2轮
- 第1轮: 模拟测试（基于假设的 grading.json）
- 第2轮: 实际测试（在真实知识库中执行）

**测试知识库**: `/Users/23mofang/Documents/knowledge-bases/test`

**最终 Pass Rate**: 90% (从模拟的75%提升到实际的90%)

---

## 发现的问题清单

### 🔴 必须修复 (P0 - 阻塞问题)

#### 1. index.md 更新遗漏
- **问题描述**: kb-archive 执行后没有更新 index.md，导致 synthesis 报告无法在索引中找到
- **影响**: 用户无法通过 index.md 发现新生成的 synthesis 报告
- **根本原因**: SKILL.md 步骤7虽然提到"更新 index.md"，但：
  1. 没有提供具体的更新方法或脚本
  2. 步骤描述不够强调重要性
  3. 没有验证机制确保执行
- **证据**: 
  - 新报告 `wiki/synthesis/楚汉战争关键人物决策分析.md` 未在 index.md 中
  - 旧报告 `wiki/synthesis/秦国历代国君战争统计分析.md` 也未在 index.md 中（历史遗留问题）

#### 2. synthesis 目录初始化检查缺失
- **问题描述**: index.md 的 synthesis section 初始为空，导致后续添加困难
- **影响**: 如果 synthesis 目录首次创建报告，index.md 没有对应 section
- **根本原因**: kb-init 或 kb-compile 没有初始化 synthesis section

---

### 🟡 建议修复 (P1 - 质量问题)

#### 3. create_synthesis.py 重复 frontmatter
- **问题描述**: 生成的 synthesis 文件包含原始 report 的 frontmatter，导致双重 frontmatter
- **影响**: 文件格式不规范，影响可读性和解析
- **根本原因**: `create_synthesis.py` 直接将 stdin 内容写入文件，未过滤 frontmatter
- **代码位置**: `scripts/create_synthesis.py:17`

#### 4. update_entity.py 换行符处理
- **问题描述**: 命令行参数中的 `\n` 未转换为实际换行符
- **影响**: 实体页面添加的章节格式错误
- **根本原因**: 命令行参数传递时字符串 `\n` 未被解析
- **代码位置**: `scripts/update_entity.py:27`
- **备注**: 手动编辑可以避免此问题，但自动化脚本应正确处理

---

### 🟢 架构改进 (P2 - 流程优化)

#### 5. 缺少自动化脚本
- **问题描述**: kb-archive 流程中多个步骤需要手动执行，缺少自动化脚本
- **影响**: 
  1. 容易遗漏步骤（如 index.md 更新）
  2. 执行效率低
  3. 流程不一致
- **建议添加的脚本**:
  - `update_index.py`: 自动更新 index.md
  - `validate_report.py`: 验证 report 格式和必需字段

#### 6. 流程验证机制缺失
- **问题描述**: 执行流程后没有验证机制确认所有步骤完成
- **影响**: 遗漏步骤无法及时发现
- **建议**: 
  - 添加流程验证检查点
  - 生成执行报告列出所有修改的文件

---

## 详细改进建议

### 建议1: 添加 update_index.py 脚本 (P0)

**目标**: 自动化 index.md 更新，确保 synthesis 报告被索引

**实现方案**:

```python
#!/usr/bin/env python3
"""Update index.md with new synthesis report entry."""

import sys
from pathlib import Path
from datetime import datetime

def main(index_path: str, synthesis_file: str, summary: str):
    index_file = Path(index_path)
    synth_file = Path(synthesis_file)
    
    # Extract title from synthesis file
    content = synth_file.read_text(encoding="utf-8")
    # Parse frontmatter for title
    title = synth_file.stem  # Use filename as title
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Read index.md
    index_content = index_file.read_text(encoding="utf-8")
    
    # Find synthesis section
    if "## synthesis" not in index_content:
        # Add synthesis section if missing
        index_content += "\n## synthesis\n<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->\n"
    
    # Add entry
    entry = f"- [[{title}]] | {summary} | 更新: {date_str}\n"
    
    # Find insertion point (after synthesis section header)
    lines = index_content.split("\n")
    synth_idx = next(i for i, l in enumerate(lines) if l.startswith("## synthesis"))
    insert_idx = synth_idx + 2  # After header and comment line
    
    lines.insert(insert_idx, entry)
    
    index_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Updated index.md: added [[{title}]]")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: update_index.py <index_path> <synthesis_file> <summary>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
```

**SKILL.md 修改**: 步骤7改为调用脚本
```
7. **更新 index.md**：调用 `update_index.py` 添加新报告索引
```

---

### 建议2: 修复 create_synthesis.py frontmatter 处理 (P1)

**目标**: 避免重复 frontmatter

**修改位置**: `scripts/create_synthesis.py`

```python
def strip_frontmatter(content: str) -> str:
    """Remove existing frontmatter from content."""
    if content.strip().startswith("---"):
        # Find end of frontmatter
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()

def main(synthesis_dir: str, title: str):
    out_dir = Path(synthesis_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Read report from stdin
    content = sys.stdin.read()
    
    # Strip original frontmatter
    clean_content = strip_frontmatter(content)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Add new frontmatter
    output = f"---\ntitle: {title}\ntype: synthesis\ndate: {date_str}\n---\n\n{clean_content}\n"
    
    out_file = out_dir / f"{title}.md"
    out_file.write_text(output, encoding="utf-8")
    print(f"Created: {out_file}")
```

---

### 建议3: 修复 update_entity.py 换行符 (P1)

**目标**: 正确处理换行符

**修改位置**: `scripts/update_entity.py`

**方案A**: 从 stdin 读取内容（推荐）
```python
def main(entity_path: str):
    p = Path(entity_path)
    if not p.exists():
        print(f"ERROR: Entity file not found: {entity_path}", file=sys.stderr)
        sys.exit(1)
    
    # Read content from stdin instead of command line
    content = sys.stdin.read()
    
    existing = p.read_text(encoding="utf-8")
    
    # Append to end before source section
    if "## 来源" in existing:
        parts = existing.split("## 来源", 1)
        updated = parts[0].rstrip() + "\n\n" + content + "\n\n## 来源" + parts[1]
    else:
        updated = existing.rstrip() + "\n\n" + content + "\n"
    
    p.write_text(updated, encoding="utf-8")
    print(f"Updated: {entity_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: update_entity.py <entity_path>", file=sys.stderr)
        print("Content should be provided via stdin", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
```

**调用方式**: 
```bash
echo "## 决策特点\n刘邦善于..." | python update_entity.py wiki/entities/刘邦.md
```

---

### 建议4: 增强 SKILL.md 流程控制 (P0)

**目标**: 确保所有步骤都被执行，不遗漏

**修改**: 在 SKILL.md 添加流程检查点

```
## 执行流程（强制）

⚠️ **重要**: 以下步骤必须全部执行，不可跳过

1. **检查 report 是否存在**：
   - report 在 agent 上下文中：继续执行 ✓
   - report 不存在：输出提示并终止 ✗
   
2. **接收 report**：调用 `read_report.py` ✓
   
3. **解析回写建议**：提取 report 中的回写建议列表 ✓
   
4. **生成回写摘要**：呈现给用户 ✓
   
5. **询问用户是否执行回写** ✓
   
6. **创建 synthesis**：调用 `create_synthesis.py` ✓
   
7. **执行回写**（如用户选择 yes）：
   - 调用 `update_entity.py` 更新实体 ✓
   
8. **更新 index.md**：调用 `update_index.py` ⚠️ **必须执行**
   
9. **验证输出**：
   - 确认 synthesis 文件创建成功 ✓
   - 确认 index.md 已更新 ✓
   - 确认实体页面已修改（如有） ✓

## 输出验证

完成后必须输出以下验证信息：
```
✓ synthesis 文件: wiki/synthesis/xxx.md (已创建)
✓ index.md (已更新)
✓ 实体更新: wiki/entities/xxx.md (已更新/无更新)
✓ log.md (已记录)
```
```

---

### 建议5: 添加流程验证脚本 (P2)

**目标**: 自动验证流程完整性

**实现**: `scripts/validate_archive.py`

```python
#!/usr/bin/env python3
"""Validate kb-archive execution completeness."""

import sys
from pathlib import Path

def main(kb_path: str, synthesis_title: str):
    kb_dir = Path(kb_path)
    
    checks = []
    
    # Check 1: synthesis file exists
    synth_file = kb_dir / "wiki/synthesis" / f"{synthesis_title}.md"
    checks.append(("synthesis文件存在", synth_file.exists()))
    
    # Check 2: index.md contains synthesis
    index_file = kb_dir / "index.md"
    if index_file.exists():
        index_content = index_file.read_text(encoding="utf-8")
        checks.append(("index.md包含报告", f"[[{synthesis_title}]]" in index_content))
    else:
        checks.append(("index.md存在", False))
    
    # Check 3: log.md updated
    log_file = kb_dir / "log.md"
    if log_file.exists():
        log_content = log_file.read_text(encoding="utf-8")
        today = datetime.now().strftime("%Y-%m-%d")
        checks.append(("log.md已更新", today in log_content and "archive" in log_content))
    
    # Print results
    all_pass = True
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")
        if not passed:
            all_pass = False
    
    sys.exit(0 if all_pass else 1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: validate_archive.py <kb_path> <synthesis_title>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
```

---

### 建议6: kb-compile/kb-init 初始化 synthesis section (P2)

**目标**: 确保 index.md 包含完整的 section 结构

**修改位置**: 
- `kb-init`: 初始化 index.md 时添加 synthesis section
- `kb-compile`: 如果 synthesis section 不存在，添加注释提示

**index.md 初始化模板**:
```markdown
---
version: "1.0"
---
# Wiki Index

## entities
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->

## concepts
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->

## synthesis
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->
<!-- kb-archive will add entries here -->
```

---

## 实施优先级

| 优先级 | 建议 | 预期效果 | 实施难度 |
|--------|------|---------|---------|
| **P0** | 建议1: update_index.py | 解决 index.md 遗漏问题 | 低 (新增脚本) |
| **P0** | 建议4: 增强 SKILL.md | 确保流程执行完整性 | 低 (文档修改) |
| **P1** | 建议2: 修复 create_synthesis.py | 提升输出质量 | 低 (代码修改) |
| **P1** | 建议3: 修复 update_entity.py | 修复换行符问题 | 低 (代码修改) |
| **P2** | 建议5: 验证脚本 | 增加自动化检查 | 中 (新增脚本) |
| **P2** | 建议6: 初始化 synthesis section | 改善初始化流程 | 中 (修改多处) |

---

## 测试覆盖率评估

当前测试覆盖的场景：
- ✓ 有 report 时创建 synthesis
- ✓ 有 report 时更新实体
- ✓ 无 report 时错误处理
- ✓ index.md 更新（发现问题后修复）

**建议增加的测试场景**:
- synthesis 目录不存在时的处理
- entity 文件不存在时的处理
- report 格式错误时的处理
- 回写建议为空时的处理
- 用户选择 "no" 或 "selective" 时的处理

---

## 总结

kb-archive skill 核心流程设计合理，但存在**流程执行不严格**的关键问题：
1. 步骤遗漏（index.md 更新）
2. 缺少自动化支持（手动执行风险）
3. 缺少验证机制（问题无法及时发现）

**关键改进方向**: 
- **自动化**: 添加脚本支持关键步骤
- **强制化**: SKILL.md 强调流程完整性
- **验证化**: 添加执行结果验证

通过实施以上建议，可将 Pass Rate 从 90% 提升至接近 100%。