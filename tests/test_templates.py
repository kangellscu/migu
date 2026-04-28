"""Tests for templates copying mechanism."""
import tempfile
from pathlib import Path

from migu.init.creator import create_kb


def test_templates_copying_from_minimal():
    """Test templates copied from minimal/templates/ to knowledge base root."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Check templates copied
        assert (kb_path / "index.md").exists()
        assert (kb_path / "log.md").exists()
        assert (kb_path / "raw-registry.md").exists()
        assert (kb_path / "AGENTS.md").exists()


def test_templates_inheritance_history():
    """Test history inherits templates from minimal (history has no templates dir)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-history"
        
        create_kb(str(kb_path), "history")
        
        # Check templates inherited from minimal
        assert (kb_path / "index.md").exists()
        assert (kb_path / "log.md").exists()
        assert (kb_path / "raw-registry.md").exists()


def test_index_md_dynamic_sections():
    """Test index.md sections generated from structure.json wiki directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Read index.md content
        index_content = (kb_path / "index.md").read_text()
        
        # Check sections match structure.json wiki directories
        assert "## entities" in index_content
        assert "## concepts" in index_content
        assert "## synthesis" in index_content
        
        # Check section format
        assert "<!-- entry: - [[Page Name]] | brief summary | updated: YYYY-MM-DD -->" in index_content


def test_templates_frontmatter_preserved():
    """Test templates frontmatter (version) preserved when copied."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Check frontmatter preserved
        index_content = (kb_path / "index.md").read_text()
        assert "---" in index_content
        assert "version:" in index_content


def test_kb_readme_standalone_copying():
    """Test kb-README.md copied from rules/ root (not templates/)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-kb"
        
        create_kb(str(kb_path), "minimal")
        
        # Check README.md exists (copied from kb-README.md)
        assert (kb_path / "README.md").exists()
        
        # Check README.md content matches kb-README.md
        readme_content = (kb_path / "README.md").read_text()
        kb_readme_path = Path(__file__).parent.parent / "rules" / "minimal" / "kb-README.md"
        kb_readme_content = kb_readme_path.read_text()
        
        # README.md should have kb-README.md content (frontmatter + sections)
        assert kb_readme_content in readme_content


def test_kb_readme_inheritance():
    """Test kb-README.md inheritance (history inherits minimal)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        kb_path = Path(tmpdir) / "test-history"
        
        create_kb(str(kb_path), "history")
        
        # Check README.md exists (inherited from minimal kb-README.md)
        assert (kb_path / "README.md").exists()
        
        # Check README.md content matches minimal kb-README.md
        readme_content = (kb_path / "README.md").read_text()
        kb_readme_path = Path(__file__).parent.parent / "rules" / "minimal" / "kb-README.md"
        kb_readme_content = kb_readme_path.read_text()
        
        assert kb_readme_content in readme_content