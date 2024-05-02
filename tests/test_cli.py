from pathlib import Path

import pytest
from click.testing import CliRunner
from semver import Version


@pytest.fixture
def runner():
    yield CliRunner()


@pytest.fixture
def py_version():
    from py_version.cli import py_version

    yield py_version


@pytest.fixture
def patch_tools(mocker):
    mock = mocker.patch("py_version.cli.tools")
    mock.parse_pyproject_file_version.return_value = Version(0, 1, 0)
    return mock


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
def test_py_version_bump(
    runner: CliRunner,
    patch_tools,
    py_version,
    part,
    new_version,
):
    patch_tools.get_pyproject_files.return_value = [
        Path("/package_a/__init__.py").absolute()
    ]

    result = runner.invoke(
        py_version, ["bump", part, "--project-root", "/"], catch_exceptions=False
    )
    print(result.output)

    patch_tools.change_pyproject_file_version.assert_called_once_with(
        Path("/pyproject.toml").absolute(), new_version
    )

    patch_tools.change_init_file_version.assert_called_once_with(
        Path("/package_a/__init__.py").absolute(), new_version
    )


@pytest.mark.parametrize(
    "part, new_version, token",
    [
        ("prerelease", "0.1.1-beta.1", "beta"),
        ("build", "0.1.0+bui.1", "bui"),
    ],
)
@pytest.mark.usefixtures("fakefs_onepackage")
def test_py_version_bump_with_token(
    runner: CliRunner, patch_tools, py_version, part, new_version, token
):
    patch_tools.get_pyproject_files.return_value = [
        Path("/package_a/__init__.py").absolute()
    ]

    result = runner.invoke(
        py_version,
        ["bump", part, "--project-root", "/", "--token", token],
        catch_exceptions=False,
    )
    print(result.output)

    patch_tools.change_pyproject_file_version.assert_called_once_with(
        Path("/pyproject.toml").absolute(), new_version
    )

    patch_tools.change_init_file_version.assert_called_once_with(
        Path("/package_a/__init__.py").absolute(), new_version
    )
