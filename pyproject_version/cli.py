"""Command line interface for the pyproject_version package."""

import pathlib
from typing import Literal

import click

from pyproject_version import __version__, tools

PART_CHOICES = ["major", "minor", "patch", "prerelease", "build"]


@click.group()
@click.version_option(version=__version__)
def pyproject_version():
    """A simple CLI for working with Python project versions."""


@pyproject_version.command()
@click.argument("part", type=click.Choice(PART_CHOICES))
@click.option(
    "--project-root",
    "-r",
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
@click.option("--token", "-t", "version_token", type=str, default=None)
@click.option("--dry-run", is_flag=True, help="Print the new version without updating.")
def bump(
    part: Literal["major", "minor", "patch", "prerelease", "build"],
    project_root: pathlib.Path,
    version_token: str | None,
    dry_run: bool = False,
):
    """Bump the version of a Python project."""
    pyproject_toml = project_root / "pyproject.toml"

    current_version = tools.parse_pyproject_file_version(pyproject_toml)

    if part == "build":
        new_version = getattr(current_version, f"bump_{part}")(version_token)
    else:
        new_version = current_version.next_version(part, version_token or "rc")
    click.echo(
        f"Bumping {part} version from {click.style(current_version, fg='cyan')}"
        f" to {click.style(new_version, fg='green')}"
    )
    if dry_run:
        click.secho("Dry run, not updating files.", fg="yellow")
        return

    tools.change_pyproject_file_version(pyproject_toml, str(new_version))

    for path in tools.get_version_files_from_pyproject(pyproject_toml):
        tools.change_init_file_version(path, str(new_version))
