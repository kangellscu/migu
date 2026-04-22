# tests/skills/test_kb_status.py
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-status" / "scripts"

def test_read_registry(tmp_path):
    """Verify read_registry.py counts pending files."""
    registry = tmp_path / "raw-registry.md"
    registry.write_text("""| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
| raw/a.md | markdown | test | 已处理 | raw/.extracted/a.md | 已编译 | 2026-04-22 |
| raw/b.pdf | pdf | pdf | 未处理 | - | 未编译 | - |
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_registry.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "pending_ingest:1" in result.stdout
    assert "pending_compile:1" in result.stdout

def test_read_index(tmp_path):
    """Verify read_index.py counts wiki documents."""
    index = tmp_path / "index.md"
    index.write_text("""# Wiki Index

## entities
- [[刘邦]] | 汉朝开国皇帝 | 更新: 2026-04-17

## concepts
- [[沛县]] | 刘邦故乡 | 更新: 2026-04-17
""")
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_index.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "total:2" in result.stdout

def test_read_registry_missing_file(tmp_path):
    """Verify error on missing raw-registry.md."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_registry.py"), str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "raw-registry.md not found" in result.stderr
