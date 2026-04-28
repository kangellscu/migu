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
    """新增 processed 条目，File 使用 wikilink，Product Path 使用 string path。"""
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
        assert "[[raw/史记/本纪/秦本纪.md]]" in content  # File: wikilink
        assert "raw/.extracted/史记/本纪/秦本纪.md" in content  # Product Path: with raw/ prefix


def test_add_skipped_entry():
    """新增 skipped 条目，File 使用 wikilink，Product Path 为 `-`。"""
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
        assert "[[raw/史记/本纪/高祖本纪.md]]" in content  # File: wikilink
        lines = content.split('\n')
        for line in lines:
            if "高祖本纪.md" in line:
                parts = [p.strip() for p in line.split('|')]
                assert parts[5] == "-"  # Product Path: string


def test_update_existing_entry():
    """更新已有条目，File 保持 wikilink，Product Path 更新为 string path。"""
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
        assert "[[raw/史记/本纪/秦本纪.md]]" in content  # File: wikilink kept
        lines = content.split('\n')
        for line in lines:
            if "秦本纪.md" in line and line.startswith('|'):
                parts = [p.strip() for p in line.split('|')]
                assert parts[1] == "[[raw/史记/本纪/秦本纪.md]]"  # File: wikilink
                assert parts[4] == "已处理"
                assert parts[5] == "raw/.extracted/史记/本纪/秦本纪.md"  # Product Path: with raw/ prefix
                assert len(parts[7]) == 10  # Date format YYYY-MM-DD


def test_batch_mode():
    """批量模式，File 使用 wikilink，Product Path 使用 string path。"""
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
        assert "[[raw/test1.md]]" in content  # File: wikilink
        assert "[[raw/test2.md]]" in content  # File: wikilink
        assert "raw/.extracted/test1.md" in content  # Product Path: with raw/ prefix