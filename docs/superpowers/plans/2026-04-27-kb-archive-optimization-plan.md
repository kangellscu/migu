# kb-archive Skill 优化实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复 kb-archive skill 的遗漏问题和质量问题，达到 100% Pass Rate。

**Architecture:** SKILL.md 流程强化 + scripts 质量修复，参照 kb-compile iteration-3 做法，保持一致性。

**Tech Stack:** Python scripts + LLM agent 流程指导

---

## 前置检查

- [ ] **Step 0: 验证 spec 存在**

检查 spec 文件：
```bash
ls docs/superpowers/specs/2026-04-27-kb-archive-optimization-design.md
```

预期：文件存在

---

## Task 1: SKILL.md 流程强化（minimal 版本）

**Files:**
- Modify: `skills/minimal/kb-archive/SKILL.md`

- [ ] **Step 1: 在执行流程中添加步骤 8、9**

定位到"执行流程"章节的步骤 7 之后，添加：

```
8. **更新 index.md**（根目录）：添加新页面索引到 synthesis section ⚠️ **必须执行**
9. **更新 log.md**（根目录）：追加 archive 操作记录 ⚠️ **必须执行**
```

调整后续步骤编号。

- [ ] **Step 2: 添加"输出验证"章节**

在"输出摘要"章节后添加新章节：

```
## 输出验证

完成后必须输出以下验证信息：
- ✓ synthesis 文件: wiki/synthesis/xxx.md (已创建)
- ✓ index.md (已更新 - synthesis section)
- ✓ log.md (已更新)
- ✓ 实体更新: X 个实体页面 (已更新/无更新)

格式示例：
处理结果：生成 1 个 synthesis 报告，更新 4 个实体页面
验证：✓ wiki/synthesis/楚汉战争关键人物决策分析.md 已创建
      ✓ index.md synthesis section 已更新
      ✓ log.md 已追加 archive 记录
下一步提示：可运行 kb-status 查看知识库状态
```

- [ ] **Step 3: 验证修改**

```bash
cat skills/minimal/kb-archive/SKILL.md | grep -A 5 "步骤 8"
cat skills/minimal/kb-archive/SKILL.md | grep -A 15 "输出验证"
```

预期：新增内容存在

- [ ] **Step 4: 提交**

```bash
git add skills/minimal/kb-archive/SKILL.md
git commit -m "feat(kb-archive): 流程强化 - 添加 index.md/log.md 更新步骤和输出验证"
```

---

## Task 2: create_synthesis.py 修复（minimal 版本）

**Files:**
- Modify: `skills/minimal/kb-archive/scripts/create_synthesis.py`

- [ ] **Step 1: 添加 frontmatter 过滤函数**

在文件开头（import 之后）添加函数：

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
```

- [ ] **Step 2: 修改 main 函数调用过滤**

在 `main` 函数中，修改内容处理部分：

找到：
```python
content = sys.stdin.read()
```

替换为：
```python
content = sys.stdin.read()
clean_content = strip_frontmatter(content)
```

找到：
```python
output = f"---\ntitle: {title}\ntype: synthesis\ndate: {date_str}\n---\n\n{content}\n"
```

替换为：
```python
output = f"---\ntitle: {title}\ntype: synthesis\ndate: {date_str}\n---\n\n{clean_content}\n"
```

- [ ] **Step 3: 验证修改**

```bash
python -c "
import sys
sys.path.insert(0, 'skills/minimal/kb-archive/scripts')
from create_synthesis import strip_frontmatter
test = '''---
title: test
---
content'''
result = strip_frontmatter(test)
assert result == 'content', f'Expected content, got {result}'
print('OK: strip_frontmatter works')
"
```

预期：输出 "OK: strip_frontmatter works"

- [ ] **Step 4: 提交**

```bash
git add skills/minimal/kb-archive/scripts/create_synthesis.py
git commit -m "fix(kb-archive): create_synthesis 过滤重复 frontmatter"
```

---

## Task 3: update_entity.py 修复（minimal 版本）

**Files:**
- Modify: `skills/minimal/kb-archive/scripts/update_entity.py`

- [ ] **Step 1: 修改 main 函数签名**

找到：
```python
def main(entity_path: str, content: str):
```

替换为：
```python
def main(entity_path: str):
```

- [ ] **Step 2: 修改内容获取方式**

找到：
```python
existing = p.read_text(encoding="utf-8")
```

在其前添加：
```python
content = sys.stdin.read()
```

删除原有的 `content` 参数使用。

- [ ] **Step 3: 修改 if __name__ == "__main__"**

找到：
```python
if len(sys.argv) != 3:
    print("Usage: update_entity.py <entity_path> <content>", file=sys.stderr)
    sys.exit(1)
main(sys.argv[1], sys.argv[2])
```

替换为：
```python
if len(sys.argv) != 2:
    print("Usage: update_entity.py <entity_path>", file=sys.stderr)
    print("Content should be provided via stdin", file=sys.stderr)
    sys.exit(1)
main(sys.argv[1])
```

- [ ] **Step 4: 验证修改**

创建测试文件：
```bash
mkdir -p /tmp/test_kb
echo '---
type: entity
---
# Test

## 描述
Test entity.

## 来源
- source: [[test.md]]
' > /tmp/test_kb/test_entity.md
```

测试 stdin 方式：
```bash
echo "## 新章节
测试内容" | python skills/minimal/kb-archive/scripts/update_entity.py /tmp/test_kb/test_entity.md
cat /tmp/test_kb/test_entity.md
```

预期：文件包含新章节，换行符正确转换

- [ ] **Step 5: 提交**

```bash
git add skills/minimal/kb-archive/scripts/update_entity.py
git commit -m "fix(kb-archive): update_entity 改为 stdin 读取，修复换行符问题"
```

---

## Task 4: history 版本同步修改

**Files:**
- Modify: `skills/history/kb-archive/SKILL.md`
- Modify: `skills/history/kb-archive/scripts/create_synthesis.py`
- Modify: `skills/history/kb-archive/scripts/update_entity.py`

- [ ] **Step 1: 复制 minimal 版本的 SKILL.md 修改**

如果 history 版本存在，应用相同的修改：
- 添加步骤 8、9（流程强化）
- 添加"输出验证"章节

```bash
# 检查 history 版本是否存在
ls skills/history/kb-archive/SKILL.md 2>/dev/null || echo "History version not found, skip"
```

- [ ] **Step 2: 复制 scripts 修改**

如果 history 版本存在，应用相同的脚本修复：
- create_synthesis.py: 添加 strip_frontmatter
- update_entity.py: 改为 stdin 读取

- [ ] **Step 3: 提交（如 history 版本存在）**

```bash
git add skills/history/kb-archive/ 2>/dev/null || true
git commit -m "feat(kb-archive): history 版本同步修改" 2>/dev/null || echo "No history changes"
```

---

## Task 5: 使用 skill-creator skill 进行测试验证

**Files:**
- Test: 使用 skill-creator skill 流程

- [ ] **Step 1: 确认 skill-creator skill 可用**

```bash
ls -la .agents/skills/skill-creator/SKILL.md
```

预期：文件存在

- [ ] **Step 2: 在测试知识库运行测试**

按照 §8 实施原则，使用 skill-creator skill：
1. 创建测试用例（包含 eval-3: index.md/log.md 更新验证）
2. 运行测试（with-skill 和 without-skill）
3. 使用 eval-viewer 展示结果
4. 根据反馈迭代改进
5. 达到 Pass Rate 100%

**注意**: 这一步应在 skill-creator skill 的指导下执行，而非手动执行。

- [ ] **Step 3: 验证 Pass Rate 达到 100%**

检查最终 benchmark.json：
```bash
cat skills/minimal/kb-archive-workspace/iteration-*/benchmark.json | grep "pass_rate"
```

预期：所有检查项通过，Pass Rate = 100%

- [ ] **Step 4: 提交最终状态**

```bash
git add skills/minimal/kb-archive-workspace/
git commit -m "test(kb-archive): 测试验证完成，Pass Rate 100%"
```

---

## 验收标准

- [ ] **最终验收**

运行以下检查：
```bash
# 1. SKILL.md 包含步骤 8、9
grep "步骤 8" skills/minimal/kb-archive/SKILL.md
grep "步骤 9" skills/minimal/kb-archive/SKILL.md

# 2. SKILL.md 包含输出验证章节
grep "输出验证" skills/minimal/kb-archive/SKILL.md

# 3. create_synthesis.py 包含 strip_frontmatter
grep "strip_frontmatter" skills/minimal/kb-archive/scripts/create_synthesis.py

# 4. update_entity.py 使用 stdin
grep "sys.stdin.read" skills/minimal/kb-archive/scripts/update_entity.py

# 5. Pass Rate 达到 100%
cat skills/minimal/kb-archive-workspace/iteration-*/benchmark.json | grep '"pass_rate": 1.0'
```

预期：所有检查通过

---

## 完成标记

全部任务完成后：
```bash
git log --oneline -5
```

预期输出包含：
- feat(kb-archive): 流程强化
- fix(kb-archive): create_synthesis 过滤重复 frontmatter
- fix(kb-archive): update_entity 改为 stdin 读取
- test(kb-archive): Pass Rate 100%