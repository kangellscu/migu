# tests/skills/test_kb_query.py
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-query" / "scripts"

def test_search_wiki(tmp_path):
    """Verify search_wiki.py finds matching documents."""
    wiki = tmp_path / "wiki"
    (wiki / "entities").mkdir(parents=True)
    (wiki / "entities" / "刘邦.md").write_text("# 刘邦\n\n汉朝开国皇帝，出生地沛县。\n\n## 来源\n- source: [[raw/test.md]]")
    (wiki / "entities" / "项羽.md").write_text("# 项羽\n\n西楚霸王。\n\n## 来源\n- source: [[raw/test.md]]")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "search_wiki.py"), str(tmp_path), "沛县"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "刘邦" in result.stdout
    assert "项羽" not in result.stdout

def test_search_wiki_no_results(tmp_path):
    """Verify search_wiki.py returns empty on no match."""
    wiki = tmp_path / "wiki"
    wiki.mkdir(parents=True)
    (wiki / "test.md").write_text("# Test\n\n## 来源\n- source: [[raw/t.md]]")

    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "search_wiki.py"), str(tmp_path), "nonexistent"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""
