---
title: kb-archive Skill 优化设计
created: 2026-04-27
type: spec
status: draft
version: 1.0
related_specs:
  - docs/superpowers/specs/2026-04-17-migu-scaffold-design.md
  - docs/superpowers/specs/2026-04-21-skills-implementation-guide.md
---

# kb-archive Skill 优化设计

## 1. 问题背景

kb-archive skill 在实际测试评估中发现两类问题，影响 Pass Rate（当前 90%）。

### P0 遗漏问题

| 问题 | 描述 | 影响 |
|------|------|------|
| index.md 未更新 | synthesis 报告不在索引中 | 用户无法通过 index.md 发现新报告 |
| log.md 未更新 | 操作记录缺失 | 无法追溯 archive 操作历史 |

**根本原因**：SKILL.md 步骤 7 虽然提到"更新 index.md"，但未强调必须执行，缺少验证机制。

### P1 质量问题

| 问题 | 代码位置 | 影响 |
|------|----------|------|
| 重复 frontmatter | scripts/create_synthesis.py:17 | 文件格式不规范，包含双重 frontmatter |
| 换行符未处理 | scripts/update_entity.py:27 | 实体页面添加的章节格式错误（`\n` 未转换） |

### 与 kb-compile 对比

kb-compile 在 iteration-3 测试时也发现类似问题，解决方案：
- SKILL.md 步骤 5、6 强调"必须执行"
- 添加评估检查项：`updates-root-index-md`、`updates-root-log-md`
- 测试用例覆盖检查项

---

## 2. 优化目标

1. **确保流程完整性**：index.md 和 log.md 更新必须执行
2. **提升输出质量**：修复 scripts 质量问题
3. **保持一致性**：与 kb-compile 处理方式一致（LLM agent 手动更新，无专门脚本）
4. **提升评估覆盖率**：添加检查项和测试用例

---

## 3. 改进范围

参照 kb-compile iteration-3 做法，采用标准方案：

- SKILL.md：强调流程、添加输出验证
- Scripts：修复质量问题
- 评估检查项：添加 `updates-root-index-md` 和 `updates-root-log-md`
- 测试用例：覆盖 index.md/log.md 检查

**不添加**：专门脚本（与 kb-compile 保持一致）

---

## 4. SKILL.md 改进

### 4.1 流程强化

在现有执行流程步骤 7 后，添加强调：

```markdown
7. **根据选择执行**：
   - 调用 `create_synthesis.py` 创建 synthesis 文件（不含回写建议）
   - 调用 `update_entity.py` 有机融入 wiki 实体文档
8. **更新 index.md**（根目录）：添加新页面索引到 synthesis section ⚠️ **必须执行**
9. **更新 log.md**（根目录）：追加 archive 操作记录 ⚠️ **必须执行**
```

### 4.2 输出验证章节

添加新章节：

```markdown
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
```

### 4.3 index.md 更新格式

LLM agent 应在 index.md synthesis section 添加条目：

```markdown
## synthesis
<!-- entry: - [[文档名]] | brief摘要 | 更新: YYYY-MM-DD -->
- [[报告标题]] | 简短摘要 | 更新: 2026-04-27
```

### 4.4 log.md 更新格式

LLM agent 应在 log.md 追加记录：

```markdown
## [YYYY-MM-DD] archive | 生成 synthesis 报告（报告标题），更新 X 个实体页面（实体列表）
```

---

## 5. Scripts 质量修复

### 5.1 create_synthesis.py 改进

**问题**：直接将 stdin 内容写入文件，导致重复 frontmatter（原始 report frontmatter + 新 synthesis frontmatter）。

**解决方案**：添加 frontmatter 过滤逻辑。

**改动**：

```python
def strip_frontmatter(content: str) -> str:
    """Remove existing frontmatter from content.
    
    Handles YAML frontmatter enclosed by --- markers.
    Returns content without frontmatter section.
    """
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[2].strip()
    return content.strip()

def main(synthesis_dir: str, title: str):
    out_dir = Path(synthesis_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    content = sys.stdin.read()
    clean_content = strip_frontmatter(content)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    output = f"---\ntitle: {title}\ntype: synthesis\ndate: {date_str}\n---\n\n{clean_content}\n"
    
    out_file = out_dir / f"{title}.md"
    out_file.write_text(output, encoding="utf-8")
    print(f"Created: {out_file}")
```

### 5.2 update_entity.py 改进

**问题**：命令行参数中的 `\n` 字符未转换为实际换行符。

**解决方案**：改为 stdin 读取内容。

**改动**：

```python
def main(entity_path: str):
    p = Path(entity_path)
    if not p.exists():
        print(f"ERROR: Entity file not found: {entity_path}", file=sys.stderr)
        sys.exit(1)
    
    content = sys.stdin.read()
    
    existing = p.read_text(encoding="utf-8")
    
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

**使用方式**：

```bash
echo "## 决策特点
刘邦善于用人决策..." | python update_entity.py wiki/entities/刘邦.md
```

---

## 6. 评估检查项与测试用例

### 6.1 评估检查项

参照 kb-compile iteration-3，在 grading.json 添加：

```json
{
  "expectations": [
    {
      "text": "synthesis-created",
      "passed": true,
      "evidence": "Created synthesis report in wiki/synthesis/"
    },
    {
      "text": "synthesis-quality",
      "passed": true,
      "evidence": "Synthesis file has clean frontmatter, no duplication"
    },
    {
      "text": "entities-updated",
      "passed": true,
      "evidence": "Entity pages updated with new sections"
    },
    {
      "text": "updates-root-index-md",
      "passed": true,
      "evidence": "Root index.md synthesis section updated with new report entry"
    },
    {
      "text": "updates-root-log-md",
      "passed": true,
      "evidence": "Root log.md updated with archive operation record"
    }
  ]
}
```

### 6.2 测试用例

新增测试用例：

```json
{
  "skill_name": "kb-archive",
  "evals": [
    {
      "id": 1,
      "prompt": "有 report 时执行 kb-archive，验证 synthesis 创建和实体更新",
      "expected_output": "synthesis 创建成功，实体页面更新，格式正确",
      "files": ["test-report.md"]
    },
    {
      "id": 2,
      "prompt": "无 report 时执行 kb-archive",
      "expected_output": "提示 report 不存在，终止执行，无文件创建",
      "files": []
    },
    {
      "id": 3,
      "prompt": "执行 kb-archive 后验证 index.md 和 log.md 更新",
      "expected_output": "index.md synthesis section 包含新报告索引，log.md 包含 archive 记录",
      "files": ["test-report.md"]
    }
  ]
}
```

---

## 7. 实施约束

### 7.1 不添加专门脚本

与 kb-compile 保持一致：
- index.md 和 log.md 由 LLM agent 手动更新
- 不添加 update_index.py 或 update_log.py
- 通过 SKILL.md 强调和评估检查项确保执行

### 7.2 前置条件

- kb-query 生成的 report 可包含 frontmatter（create_synthesis.py 会过滤）
- synthesis section 需存在或由 agent 添加（如不存在）

---

## 8. 验收标准

优化完成后应达到：

| 标准 | 目标 |
|------|------|
| Pass Rate | 100% |
| 所有检查项通过 | synthesis-created, synthesis-quality, entities-updated, updates-root-index-md, updates-root-log-md |
| 与 kb-compile 一致 | 处理方式、评估检查项、测试用例覆盖 |
| Scripts 质量 | create_synthesis.py 无重复 frontmatter，update_entity.py 正确处理换行 |