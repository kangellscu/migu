import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-compile" / "scripts"

def test_read_file(tmp_path):
    """Verify read_file.py reads file content."""
    f = tmp_path / "test.md"
    f.write_text("# Hello World")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_file.py"), str(f)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "# Hello World" in result.stdout

def test_read_file_missing(tmp_path):
    """Verify read_file.py errors on missing file."""
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "read_file.py"), str(tmp_path / "nope.md")],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "not found" in result.stderr

def test_update_registry(tmp_path):
    """Verify update_registry.py updates compile status."""
    registry = tmp_path / "raw-registry.md"
    registry.write_text("""| 文件 | 类型 | 摘要 | 预处理状态 | 产物路径 | 编译状态 | 最近处理日期 |
|------|------|------|-----------|---------|---------|-------------|
| [[raw/test.md\|test]] | markdown | test | 已处理 | raw/.extracted/test.md | 未编译 | - |
""")
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "update_registry.py"), str(tmp_path), "raw/test.md", "已编译"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "Updated" in result.stdout
    
    content = registry.read_text()
    assert "已编译" in content
