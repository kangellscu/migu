import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-lint" / "scripts"


def test_syntax_check_valid(tmp_path):
    """Verify syntax.py passes on valid markdown."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "test.md").write_text("# Test\n\nContent here.\n\n## 来源\n- source: [[raw/test.md]]")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "syntax.py"), str(wiki)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0


def test_syntax_check_missing_source(tmp_path):
    """Verify syntax.py detects missing source field."""
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "test.md").write_text("# Test\n\nContent.\n\n## 无关\nno source")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "syntax.py"), str(wiki)],
        capture_output=True, text=True,
    )
    assert result.returncode != 0
    assert "source" in result.stdout.lower()
