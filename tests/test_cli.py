from typing import Any

import pytest
import tomlkit
from click.testing import CliRunner

from py_version.cli import py_version


@pytest.fixture
def runner():
    yield CliRunner()


@pytest.mark.parametrize(
    "part, new_version",
    [
        ("major", "1.0.0"),
        ("minor", "0.2.0"),
        ("patch", "0.1.1"),
        ("prerelease", "0.1.1-rc.1"),
        ("build", "0.1.0+build.1"),
    ],
)
@pytest.mark.usefixtures("fakefs_onepackage")
def test_py_version_bump_one_package(runner: CliRunner, part, new_version):

    result = runner.invoke(
        py_version, ["bump", part, "--project_root", "/"], catch_exceptions=False
    )
    print(result.output)

    expected_init_contents = f'''"""Test package_a init file."""

__version__ = "{new_version}"
'''
    with open("/pyproject.toml", encoding="utf-8") as f:
        pyproject: dict[str, Any] = tomlkit.parse(f.read())

        assert pyproject["tool"]["poetry"]["version"] == new_version

    with open("/package_a/__init__.py", encoding="utf-8") as f:
        assert f.read() == expected_init_contents


@pytest.mark.parametrize(
    "part, new_version, token",
    [
        ("prerelease", "0.1.1-beta.1", "beta"),
        ("build", "0.1.0+bui.1", "bui"),
    ],
)
@pytest.mark.usefixtures("fakefs_onepackage")
def test_py_version_bump_one_package_with_token(
    runner: CliRunner, part, new_version, token
):

    result = runner.invoke(
        py_version,
        ["bump", part, "--project_root", "/", "--token", token],
        catch_exceptions=False,
    )
    print(result.output)

    expected_init_content = f'''"""Test package_a init file."""

__version__ = "{new_version}"
'''
    with open("/pyproject.toml", encoding="utf-8") as f:
        pyproject: dict[str, Any] = tomlkit.parse(f.read())

        assert pyproject["tool"]["poetry"]["version"] == new_version

    with open("/package_a/__init__.py", encoding="utf-8") as f:
        assert f.read() == expected_init_content


@pytest.mark.parametrize(
    "part, new_version",
    [
        ("major", "1.0.0"),
        ("minor", "0.2.0"),
        ("patch", "0.1.1"),
        ("prerelease", "0.1.1-rc.1"),
        ("build", "0.1.0+build.1"),
    ],
)
@pytest.mark.usefixtures("fakefs_twopackage")
def test_py_version_bump_two_package(runner: CliRunner, part, new_version):

    result = runner.invoke(
        py_version, ["bump", part, "--project_root", "/"], catch_exceptions=False
    )
    print(result.output)

    expected_package_a_init_contents = f'''"""Test package_a init file."""

__version__ = "{new_version}"
'''
    expected_package_b_init_contents = '''"""Test package_b init file."""

__version__ = "0.1.0"
'''
    with open("/pyproject.toml", encoding="utf-8") as f:
        pyproject: dict[str, Any] = tomlkit.parse(f.read())

        assert pyproject["tool"]["poetry"]["version"] == new_version

    with open("/package_a/__init__.py", encoding="utf-8") as f:
        assert f.read() == expected_package_a_init_contents

    with open("/package_b/__init__.py", encoding="utf-8") as f:
        assert f.read() == expected_package_b_init_contents
