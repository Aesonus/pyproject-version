from pathlib import Path

import pytest
from click.testing import CliRunner
from semver import Version


@pytest.fixture
def runner():
    yield CliRunner()


@pytest.fixture
def pyproject_version():
    from pyproject_version.cli import pyproject_version

    yield pyproject_version


@pytest.fixture
def patch_tools(mocker):
    mock = mocker.patch("pyproject_version.cli.tools")
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
@pytest.mark.parametrize("dry_run", [True, False], ids=["dry_run", "update_files"])
@pytest.mark.usefixtures("fakefs_onepackage")
def test_pyproject_version_bump(
    runner: CliRunner, patch_tools, pyproject_version, part, new_version, dry_run: bool
):
    patch_tools.get_version_files_from_pyproject.return_value = [
        Path("/package_a/__init__.py").absolute()
    ]

    result = runner.invoke(
        pyproject_version,
        ["bump", part, "--project-root", "/", *(["--dry-run"] if dry_run else [])],
        catch_exceptions=False,
    )

    assert result.output == (
        f"Bumping {part} version from 0.1.0"
        f" to {new_version}\n" + ("Dry run, not updating files.\n" if dry_run else "")
    )

    if not dry_run:
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
@pytest.mark.parametrize("dry_run", [True, False], ids=["dry_run", "update_files"])
@pytest.mark.usefixtures("fakefs_onepackage")
def test_pyproject_version_bump_with_token(
    runner: CliRunner, patch_tools, pyproject_version, part, new_version, token, dry_run
):
    patch_tools.get_version_files_from_pyproject.return_value = [
        Path("/package_a/__init__.py").absolute()
    ]

    result = runner.invoke(
        pyproject_version,
        [
            "bump",
            part,
            "--project-root",
            "/",
            "--token",
            token,
            *(["--dry-run"] if dry_run else []),
        ],
        catch_exceptions=False,
    )
    print(result.output)

    assert result.output == (
        f"Bumping {part} version from 0.1.0"
        f" to {new_version}\n" + ("Dry run, not updating files.\n" if dry_run else "")
    )

    if not dry_run:
        patch_tools.change_pyproject_file_version.assert_called_once_with(
            Path("/pyproject.toml").absolute(), new_version
        )

        patch_tools.change_init_file_version.assert_called_once_with(
            Path("/package_a/__init__.py").absolute(), new_version
        )


@pytest.mark.parametrize(
    "new_version",
    [
        "1.0.0",
        "0.2.0",
        "0.1.1",
        "0.1.1-rc.1",
        "0.1.0+build.1",
    ],
)
@pytest.mark.parametrize("dry_run", [True, False], ids=["dry_run", "update_files"])
@pytest.mark.usefixtures("fakefs_onepackage")
def test_pyproject_version_set_version(
    runner: CliRunner, patch_tools, pyproject_version, new_version, dry_run: bool
):
    patch_tools.get_version_files_from_pyproject.return_value = [
        Path("/package_a/__init__.py").absolute()
    ]

    result = runner.invoke(
        pyproject_version,
        [
            "set-version",
            new_version,
            "--project-root",
            "/",
            *(["--dry-run"] if dry_run else []),
        ],
        catch_exceptions=False,
    )

    assert result.output == (
        f"Setting version to {new_version}\n"
        + ("Dry run, not updating files.\n" if dry_run else "")
    )

    if not dry_run:
        patch_tools.change_pyproject_file_version.assert_called_once_with(
            Path("/pyproject.toml").absolute(), new_version
        )

        patch_tools.change_init_file_version.assert_called_once_with(
            Path("/package_a/__init__.py").absolute(), new_version
        )


@pytest.mark.parametrize(
    "invalid_version",
    [
        "invalid",
        "1.0",
        "1.0.0.0",
        "1.0.0-",
        "1.0.0+",
    ],
)
@pytest.mark.usefixtures("fakefs_onepackage")
def test_pyproject_version_set_invalid_version(
    runner: CliRunner, patch_tools, pyproject_version, invalid_version
):
    result = runner.invoke(
        pyproject_version,
        ["set-version", invalid_version, "--project-root", "/"],
        catch_exceptions=False,
    )

    assert "Invalid version" in result.output
    assert result.exit_code != 0
    patch_tools.change_pyproject_file_version.assert_not_called()
    patch_tools.change_init_file_version.assert_not_called()
