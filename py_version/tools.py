"""Module for tools that are used in the project."""

import functools
import io
import pathlib
import re
import tokenize
from operator import methodcaller

import semver
import tomlkit


def change_init_file_version(path: pathlib.Path, new_version: str) -> None:
    """Change the version in a file.

    Args:
        path (pathlib.Path): The path to the file.
        new_version (str): The new version to set in the file.

    """
    readline = tokenize.generate_tokens(io.StringIO(path.read_text()).readline)

    found_version = False
    found_operator = False
    new_lines = []
    for tok in readline:
        if (
            (not found_version)
            and tok.type == tokenize.NAME
            and tok.string == "__version__"
        ):
            found_version = True
            new_lines.append(tok)
            continue
        if (
            found_version
            and (not found_operator)
            and tok.type == tokenize.OP
            and tok.string == "="
        ):
            found_operator = True
            new_lines.append(tok)
            continue
        if found_version and found_operator and tok.type == tokenize.STRING:
            new_lines.append(
                tokenize.TokenInfo(
                    tokenize.STRING,
                    re.sub(
                        r"([\"']{1,3})(\s*[^'\"]+\s*)([\"']{1,3})",
                        lambda m: f"{m.group(1)}{new_version}{m.group(3)}",
                        tok.string,
                    ),
                    tok.start,
                    tok.end,
                    tok.line,
                )
            )
            found_version = False
            found_operator = False
            continue
        new_lines.append(tok)
    path.write_text(tokenize.untokenize(new_lines), encoding="utf-8")


@functools.cache
def parse_pyproject(path: pathlib.Path) -> tomlkit.TOMLDocument:
    """Parse the pyproject.toml file.

    Args:
        path (pathlib.Path): The path to the file.

    Returns:
        tomlkit.TOMLDocument: The parsed pyproject.toml file.

    """
    return tomlkit.parse(path.read_text(encoding="utf-8"))


def change_pyproject_file_version(path: pathlib.Path, new_version: str) -> None:
    """Change the version in the pyproject.toml file.

    Args:
        path (pathlib.Path): The path to the file.
        new_version (str): The new version to set in the file.

    """
    pyproject = parse_pyproject(path)
    pyproject["tool"]["poetry"]["version"] = new_version  # type: ignore
    path.write_text(pyproject.as_string(), encoding="utf-8")


def parse_pyproject_file_version(path: pathlib.Path) -> semver.VersionInfo:
    """Parse the version from the pyproject.toml file.

    Args:
        path (pathlib.Path): The path to the file.

    Returns:
        semver.VersionInfo: The parsed version.

    """
    pyproject = parse_pyproject(path)
    return semver.VersionInfo.parse(pyproject["tool"]["poetry"]["version"])  # type: ignore


def get_version_files_from_pyproject(path: pathlib.Path) -> list[pathlib.Path]:
    """Get the files that are to have their ``__version__`` updated.

    Args:
        path (pathlib.Path): The path to the file.

    Returns:
        list[pathlib.Path]: The files that are used for versioning.

    """
    pyproject = parse_pyproject(path)
    try:
        return list(
            map(
                methodcaller("absolute"),
                map(
                    pathlib.Path,
                    pyproject["tool"]["py-version"]["files"],  # type: ignore
                ),
            )
        )
    except KeyError:
        return []
