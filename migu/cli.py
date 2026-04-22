"""Migu CLI - LLM-WIKI knowledge base scaffolder."""

import typer

from migu import __version__

app = typer.Typer(
    name="migu",
    help="CLI scaffolder for LLM-WIKI knowledge bases",
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"migu {__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    version: bool = typer.Option(
        None,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    pass


@app.command()
def init(
    target_dir: str = typer.Argument(..., help="Target directory for the knowledge base"),
    rules: str = typer.Option("minimal", "--rules", help="Rules type (default: minimal)"),
) -> None:
    """Initialize a new knowledge base."""
    from migu.init.creator import create_kb

    create_kb(target_dir, rules)


from migu.skill.cli import skill_app

app.add_typer(skill_app, name="skill")

if __name__ == "__main__":
    app()
