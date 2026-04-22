from typer.testing import CliRunner


def test_cli_app_exists():
    """Verify the CLI app can be imported and run."""
    from migu.cli import app

    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "migu" in result.stdout.lower()
