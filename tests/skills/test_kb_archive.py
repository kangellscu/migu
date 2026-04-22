import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent.parent / "skills" / "minimal"
SCRIPTS = SKILLS_DIR / "kb-archive" / "scripts"

def test_create_synthesis(tmp_path):
    """Verify create_synthesis.py creates synthesis file."""
    synthesis_dir = tmp_path / "wiki" / "synthesis"
    synthesis_dir.mkdir(parents=True)
    report_content = "# Test Report\n\n## 分析\n...\n\n## 结论\nDone."
    
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "create_synthesis.py"), str(synthesis_dir), "Test Report"],
        capture_output=True, text=True,
        input=report_content,
    )
    assert result.returncode == 0
    assert (synthesis_dir / "Test Report.md").exists()
