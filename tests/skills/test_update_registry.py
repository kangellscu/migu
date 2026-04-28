"""Tests for update_registry.py."""

import json
import subprocess
import tempfile
from pathlib import Path


REGISTRY_TEMPLATE = """---
version: 2.0
---
# Raw File Registry

<!-- 
entry format: | File | Type | Summary | Preprocess Status | Product Path | Compile Status | Last Processed | Remaining Omissions |
-->

| File | Type | Summary | Preprocess Status | Product Path | Compile Status | Last Processed | Remaining Omissions |
|------|------|------|-----------|---------|---------|-------------|------------------|

## 剩余遗漏字段约定

- `空`：已收敛，无遗漏
- `实体1, 实体2, ...`：剩余遗漏实体清单（逗号分隔）
- `-`：未编译，字段不适用
"""


def test_add_processed_entry():
    """新增 processed 条目，使用 string path 格式。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        registry_file = kb_dir / "raw-registry.md"
        registry_file.write_text(REGISTRY_TEMPLATE, encoding='utf-8')
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/update_registry.py",
             str(kb_dir),
             "--file", "史记/本纪/秦本纪.md",
             "--type", "markdown",
             "--status", "processed",
             "--output", ".extracted/史记/本纪/秦本纪.md"],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        assert result.returncode == 0
        
        content = registry_file.read_text(encoding='utf-8')
        assert "史记/本纪/秦本纪.md" in content
        assert ".extracted/史记/本纪/秦本纪.md" in content
        assert "[[" not in content  # 无 wikilink


def test_add_skipped_entry():
    """新增 skipped 条目，Product Path 为 `-`。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        registry_file = kb_dir / "raw-registry.md"
        registry_file.write_text(REGISTRY_TEMPLATE, encoding='utf-8')
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/update_registry.py",
             str(kb_dir),
             "--file", "史记/本纪/高祖本纪.md",
             "--type", "markdown",
             "--status", "skipped"],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        assert result.returncode == 0
        
        content = registry_file.read_text(encoding='utf-8')
        assert "史记/本纪/高祖本纪.md" in content
        lines = content.split('\n')
        for line in lines:
            if "高祖本纪.md" in line:
                parts = [p.strip() for p in line.split('|')]
                assert parts[5] == "-"  # Product Path


def test_update_existing_entry():
    """更新已有条目，状态和日期更新。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        registry_file = kb_dir / "raw-registry.md"
        
        initial_content = REGISTRY_TEMPLATE.replace(
            "|------|------|------|-----------|---------|---------|-------------|------------------|",
            "|------|------|------|-----------|---------|---------|-------------|------------------|\n| [[raw/史记/本纪/秦本纪.md]] | markdown | | 待处理 | [[raw/.extracted/史记/本纪/秦本纪.md]] | - | - | - |"
        )
        registry_file.write_text(initial_content, encoding='utf-8')
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/update_registry.py",
             str(kb_dir),
             "--file", "史记/本纪/秦本纪.md",
             "--type", "markdown",
             "--status", "processed",
             "--output", ".extracted/史记/本纪/秦本纪.md"],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        assert result.returncode == 0
        
        content = registry_file.read_text(encoding='utf-8')
        assert "[[" not in content  # wikilink should be removed
        lines = content.split('\n')
        for line in lines:
            if "秦本纪.md" in line:
                parts = [p.strip() for p in line.split('|')]
                assert parts[1] == "史记/本纪/秦本纪.md"  # File: string path
                assert parts[4] == "已处理"
                assert parts[5] == ".extracted/史记/本纪/秦本纪.md"  # Product Path: string path
                assert len(parts[7]) == 10  # Date format YYYY-MM-DD


def test_replace_wikilink_entry():
    """wikilink 格式条目被替换为 string path 格式。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        registry_file = kb_dir / "raw-registry.md"
        
        initial_content = REGISTRY_TEMPLATE.replace(
            "|------|------|------|-----------|---------|---------|-------------|------------------|",
            "|------|------|------|-----------|---------|---------|-------------|------------------|\n| [[raw/test.md]] | markdown | | 待处理 | - | - | - | - |"
        )
        registry_file.write_text(initial_content, encoding='utf-8')
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/update_registry.py",
             str(kb_dir),
             "--file", "test.md",
             "--type", "markdown",
             "--status", "skipped"],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        assert result.returncode == 0
        
        content = registry_file.read_text(encoding='utf-8')
        assert "[[" not in content
        assert "test.md" in content
        lines = content.split('\n')
        for line in lines:
            if "test.md" in line:
                parts = [p.strip() for p in line.split('|')]
                assert parts[1] == "test.md"


def test_batch_mode():
    """批量模式，从 stdin 读取 JSON。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        registry_file = kb_dir / "raw-registry.md"
        registry_file.write_text(REGISTRY_TEMPLATE, encoding='utf-8')
        
        batch_data = [
            {"file": "test1.md", "type": "markdown", "status": "processed", "output_path": ".extracted/test1.md"},
            {"file": "test2.md", "type": "markdown", "status": "skipped"},
        ]
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/update_registry.py",
             str(kb_dir), "--batch"],
            input='\n'.join(json.dumps(d) for d in batch_data),
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        assert result.returncode == 0
        
        content = registry_file.read_text(encoding='utf-8')
        assert "test1.md" in content
        assert "test2.md" in content
        assert "[[" not in content