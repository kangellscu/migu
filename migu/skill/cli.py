"""Skill CLI commands (install, uninstall, reinstall, list)."""

import typer

from pathlib import Path

from migu.skill.manager import (
    load_skills_lock,
    validate_target_dir,
    get_bundled_skill_path,
)
from migu.skill.installer import (
    install_skill,
    uninstall_skill,
    check_skill_changed,
)

skill_app = typer.Typer(name="skill", help="Manage knowledge base skills")


@skill_app.command("list")
def list_skills(target_dir: str = typer.Argument(..., help="Knowledge base directory")) -> None:
    """List installed skills with version status."""
    target_path = Path(target_dir).resolve()
    try:
        validate_target_dir(target_path)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    
    lock_data = load_skills_lock(target_path)
    print(f"Skills in {target_path}:")
    print()
    
    for skill in lock_data["skills"]:
        bundled = get_bundled_skill_path(skill["name"], skill["source"])
        
        is_latest = bundled.exists()
        
        status = "✓ latest" if is_latest else "⚠ outdated"
        print(f"  {skill['name']}  source: {skill['source']}  version: {skill['version']}  {status}")
    
    print()


@skill_app.command("install")
def install_skill_cmd(
    skill_name: str = typer.Argument(..., help="Skill name (e.g., kb-ingest)"),
    target_dir: str = typer.Argument(..., help="Knowledge base directory"),
    source: str = typer.Option("minimal", "--source", help="Skill source (default: minimal)"),
) -> None:
    """Install a skill into a knowledge base."""
    target_path = Path(target_dir).resolve()
    try:
        validate_target_dir(target_path)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    
    lock_data = load_skills_lock(target_path)
    
    for skill in lock_data["skills"]:
        if skill["name"] == skill_name:
            typer.echo(f"Skill '{skill_name}' is already installed. Use 'reinstall' to update.")
            raise typer.Exit(code=1)
    
    install_skill(skill_name, source, target_path, lock_data)
    typer.echo(f"Skill '{skill_name}' installed from source '{source}'.")


@skill_app.command("uninstall")
def uninstall_skill_cmd(
    skill_name: str = typer.Argument(..., help="Skill name"),
    target_dir: str = typer.Argument(..., help="Knowledge base directory"),
) -> None:
    """Uninstall a skill from a knowledge base."""
    target_path = Path(target_dir).resolve()
    try:
        validate_target_dir(target_path)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    
    lock_data = load_skills_lock(target_path)
    uninstall_skill(skill_name, target_path, lock_data)
    
    typer.echo(f"Skill '{skill_name}' uninstalled.")


@skill_app.command("reinstall")
def reinstall_skill_cmd(
    skill_name: str = typer.Argument(..., help="Skill name"),
    target_dir: str = typer.Argument(..., help="Knowledge base directory"),
) -> None:
    """Reinstall a skill (updates to latest version)."""
    target_path = Path(target_dir).resolve()
    try:
        validate_target_dir(target_path)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    
    lock_data = load_skills_lock(target_path)
    
    source = None
    for skill in lock_data["skills"]:
        if skill["name"] == skill_name:
            source = skill["source"]
            break
    
    if source is None:
        typer.echo(f"Skill '{skill_name}' is not installed. Use 'install' first.")
        raise typer.Exit(code=1)
    
    if check_skill_changed(skill_name, target_path):
        typer.echo(f"⚠ Skill '{skill_name}' has been modified.")
        confirm = typer.confirm("Changes will be overwritten. Continue?")
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit()
    
    install_skill(skill_name, source, target_path, lock_data)
    typer.echo(f"Skill '{skill_name}' reinstalled from source '{source}'.")
