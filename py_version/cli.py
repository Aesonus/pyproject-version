"""Command line interface for the py_version package."""

import pathlib
from typing import Any, Literal

import click
import semver
import tomlkit

from py_version import __version__, tools

PART_CHOICES = ["major", "minor", "patch", "prerelease", "build"]


@click.group()
@click.version_option(version=__version__)
def py_version():
    """A simple CLI for working with Python project versions."""


@py_version.command()
@click.argument("part", type=click.Choice(PART_CHOICES))
@click.option(
    "--project_root",
    type=click.Path(
        exists=True,
        file_okay=False,
        allow_dash=False,
        path_type=pathlib.Path,
        resolve_path=True,
    ),
    default=".",
    help="The root of the Python project.",
)
@click.option("--token", "version_token", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Print the new version without updating.")
def bump(
    part: Literal["major", "minor", "patch", "prerelease", "build"],
    project_root: pathlib.Path,
    version_token: str | None,
    dry_run: bool = False,
):
    """Bump the version of a Python project."""
    pyproject_toml = project_root / "pyproject.toml"

    if not pyproject_toml.exists():
        raise click.ClickException(f"Could not find pyproject.toml in {project_root}")

    pyproject: Any = tomlkit.parse(pyproject_toml.read_text(encoding="utf-8"))

    if "tool" not in pyproject or "poetry" not in pyproject["tool"]:
        raise click.ClickException(
            "Could not find poetry configuration in pyproject.toml"
        )

    try:
        current_version = semver.version.Version.parse(
            pyproject["tool"]["poetry"]["version"]
        )
    except ValueError as exc:
        raise click.ClickException(f"Could not parse version: {exc}")
    if part == "build":
        new_version = getattr(current_version, f"bump_{part}")(version_token)
    else:
        new_version = current_version.next_version(part, version_token or "rc")
    click.echo(
        f"Bumping {part} version from {click.style(current_version, fg='cyan')}"
        f" to {click.style(new_version, fg='green')}"
    )

    if dry_run:
        return
    pyproject["tool"]["poetry"]["version"] = str(new_version)
    pyproject_toml.write_text(pyproject.as_string(), encoding="utf-8")

    for path in map(
        pathlib.Path, pyproject["tool"].get("py-version", {"files": []})["files"]
    ):
        tools.change_file_version(path, new_version)
