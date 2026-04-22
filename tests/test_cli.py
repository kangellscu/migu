import json
from typer.testing import CliRunner


def test_cli_app_exists():
    """Verify the CLI app can be imported and run."""
    from migu.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "migu" in result.stdout.lower()


def test_init_creates_knowledge_base(tmp_path):
    """Verify migu init creates full knowledge base structure."""
    from migu.cli import app

    target = tmp_path / "test-kb"
    runner = CliRunner()
    result = runner.invoke(app, ["init", str(target)])

    assert result.exit_code == 0

    # Verify expected directories exist
    assert (target / "raw" / ".extracted").is_dir()
    assert (target / "wiki" / "entities").is_dir()
    assert (target / "wiki" / "concepts").is_dir()
    assert (target / "wiki" / "synthesis").is_dir()
    assert (target / "output").is_dir()
    assert (target / ".agents" / "skills").is_dir()

    # Verify expected files exist
    assert (target / "AGENTS.md").is_file()
    assert (target / "index.md").is_file()
    assert (target / "log.md").is_file()
    assert (target / "raw-registry.md").is_file()

    # Verify skills-lock.json
    lock_file = target / ".agents" / "skills-lock.json"
    assert lock_file.is_file()

    lock_data = json.loads(lock_file.read_text())
    assert lock_data["rules"] == "minimal"
    assert "skills" in lock_data

    # Verify each skill has installed_at
    for skill in lock_data["skills"]:
        assert "installed_at" in skill


def test_init_fails_on_existing_directory(tmp_path):
    """Verify migu init fails if target directory exists."""
    from migu.cli import app

    target = tmp_path / "test-kb"
    target.mkdir()

    runner = CliRunner()
    result = runner.invoke(app, ["init", str(target)])

    assert result.exit_code != 0
    assert "already exists" in str(result.exception).lower()
