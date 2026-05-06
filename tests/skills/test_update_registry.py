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


def test_unicode_filename_preserved():
    """Unicode characters in filename (e.g., smart quote U+2019) should be preserved in wikilink.
    
    Bug: KB-INGEST-001 - Unicode filename characters were converted to ASCII equivalents,
    causing Obsidian wikilink failures.
    
    Expected: Unicode characters (U+2019 smart quote) should remain unchanged in wikilink.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        registry_file = kb_dir / "raw-registry.md"
        registry_file.write_text(REGISTRY_TEMPLATE, encoding='utf-8')
        
        # File with Unicode smart quote (U+2019) - the bug case
        # Using Unicode escape to ensure correct character
        unicode_filename = "Understanding Palantir\u2019s Ontology.md"  # Contains U+2019 (smart quote)
        
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/update_registry.py",
             str(kb_dir),
             "--file", unicode_filename,
             "--type", "markdown",
             "--status", "skipped"],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        assert result.returncode == 0
        
        content = registry_file.read_text(encoding='utf-8')
        
        # Extract wikilink from registry
        lines = content.split('\n')
        wikilink = None
        for line in lines:
            if unicode_filename in line or "Palantir" in line:
                # Extract wikilink: [[raw/...]]
                start = line.find('[[')
                end = line.find(']]')
                if start >= 0 and end >= 0:
                    wikilink = line[start+2:end]
                    break
        
        assert wikilink is not None, "Wikilink should be found in registry"
        
        # Verify Unicode character preserved (U+2019, not U+0027)
        expected_path = f"raw/{unicode_filename}"
        assert wikilink == expected_path, f"Wikilink should preserve Unicode: expected {expected_path}, got {wikilink}"
        
        # Verify specific Unicode character
        assert '\u2019' in wikilink, f"Smart quote U+2019 should be preserved in wikilink: {wikilink}"
        assert '\u0027' not in wikilink.replace('\u2019', ''), f"ASCII quote U+0027 should not replace Unicode: {wikilink}"


def test_unicode_normalization_prevents_wrong_encoding():
    """Registry should preserve correct Unicode characters matching actual filename.
    
    Scenario: Registry has ASCII quote (U+0027), but actual filename has Unicode quote (U+2019).
    Expected: Registry should use Unicode version to match actual filename for Obsidian compatibility.
    
    Key insight: U+2019 and U+0027 are different Unicode characters (NFKC won't normalize them).
    The registry should match the actual filename encoding, not force ASCII conversion.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_dir = Path(tmpdir)
        registry_file = kb_dir / "raw-registry.md"
        
        # Pre-populate registry with WRONG ASCII quote entry (doesn't match actual filename)
        initial_content = REGISTRY_TEMPLATE.replace(
            "|------|------|------|-----------|---------|---------|-------------|------------------|",
            "|------|------|------|-----------|---------|---------|-------------|------------------|\n| [[raw/Palantir's Ontology.md]] | markdown | | 无需处理 | - | 已编译 | 2026-05-05 | - |"
        )
        registry_file.write_text(initial_content, encoding='utf-8')
        
        # Actual filename has Unicode quote (U+2019) - correct version
        unicode_filename = "Palantir\u2019s Ontology.md"
        
        # Update registry - should add correct Unicode entry
        # (ASCII entry won't match because they're different Unicode characters)
        result = subprocess.run(
            ["python", "skills/minimal/kb-ingest/scripts/update_registry.py",
             str(kb_dir),
             "--file", unicode_filename,
             "--type", "markdown",
             "--status", "skipped"],
            capture_output=True,
            text=True,
            cwd="/Users/23mofang/Documents/knowledge-bases/migu"
        )
        
        assert result.returncode == 0
        
        content = registry_file.read_text(encoding='utf-8')
        
        # Registry should have Unicode entry (matching actual filename)
        unicode_entries = [l for l in content.split('\n') if 'Palantir' in l and '\u2019' in l and l.startswith('|')]
        assert len(unicode_entries) >= 1, f"Should have Unicode entry (U+2019): found {len(unicode_entries)}"
        
        # Verify Unicode entry is correct (matches actual filename)
        unicode_entry = unicode_entries[0]
        assert '[[raw/Palantir\u2019s Ontology.md]]' in unicode_entry, "Wikilink should use Unicode (U+2019)"
        
        # Manual cleanup needed for wrong ASCII entry (separate concern)
        # This test verifies: correct Unicode preserved for Obsidian compatibility