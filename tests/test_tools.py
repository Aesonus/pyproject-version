import pathlib

import pytest
import semver

from py_version import tools


@pytest.fixture
def minimal_pyproject_template():
    return """[tool.poetry]
    name = "package_a"
    version = "{version}"
    """


class TestChangeInitFileVersion:
    @pytest.mark.parametrize(
        "old_version,expected_version",
        [
            ('"0.1.0"', '"0.1.1"'),
            ('"0.1.0-dev0"', '"0.1.1"'),
            ('"""0.1.0+build.1"""', '"""0.1.1"""'),
            ("'0.1.0'", "'0.1.1'"),
            ('"""0.1.0\n"""', '"""0.1.1"""'),
        ],
        ids=[
            "double_quotes",
            "dev_version",
            "build_version, triple_quotes",
            "single_quotes",
            "multiline",
        ],
    )
    def test_change_init_file_version_replaces_version_with_new_version(
        self, fs, package_init_template: str, old_version, expected_version
    ):
        # Set up
        fs.create_file(
            "/package_a/__init__.py",
            contents=package_init_template.format(version=old_version),
        )

        path = pathlib.Path("/package_a/__init__.py")
        new_version = "0.1.1"
        tools.change_init_file_version(path, new_version)

        with open(path, encoding="utf-8") as f:
            assert f.read() == package_init_template.format(version=expected_version)


class TestChangePyprojectFileVersion:
    @pytest.mark.parametrize(
        "old_version,expected_version",
        [
            ("0.1.0", "0.1.1"),
            ("0.1.0-dev0", "0.1.1"),
            ("0.1.0+build.1", "0.1.1"),
        ],
        ids=["normal_version", "dev_version", "build_version"],
    )
    def test_change_pyproject_file_version_replaces_version_with_new_version(
        self, fs, old_version, expected_version, minimal_pyproject_template
    ):
        # Set up
        fs.create_file(
            "/pyproject.toml",
            contents=minimal_pyproject_template.format(version=old_version),
        )

        path = pathlib.Path("/pyproject.toml")
        tools.change_pyproject_file_version(path, expected_version)

        with open(path, encoding="utf-8") as f:
            assert f.read() == minimal_pyproject_template.format(
                version=expected_version
            )

    @pytest.mark.usefixtures("fs")
    def test_change_pyproject_file_version_raises_file_not_found_error_if_pyproject_not_found(
        self,
    ):
        with pytest.raises(FileNotFoundError):
            tools.change_pyproject_file_version(
                pathlib.Path("/pyproject.toml"), "0.1.1"
            )


class TestParsePyprojectFileVersion:

    @pytest.mark.parametrize(
        "version_str,expected_version",
        [
            ("0.1.0", semver.VersionInfo(major=0, minor=1, patch=0)),
            (
                "0.1.0-dev0",
                semver.VersionInfo(major=0, minor=1, patch=0, prerelease="dev0"),
            ),
            (
                "0.1.0+build.1",
                semver.VersionInfo(major=0, minor=1, patch=0, build="build.1"),
            ),
        ],
        ids=["normal_version", "dev_version", "build_version"],
    )
    def test_parse_pyproject_file_version_returns_version(
        self, fs, version_str, expected_version, minimal_pyproject_template
    ):
        # Set up
        fs.create_file(
            "/pyproject.toml",
            contents=minimal_pyproject_template.format(version=version_str),
        )

        path = pathlib.Path("/pyproject.toml")
        version = tools.parse_pyproject_file_version(path)

        assert version == expected_version

    @pytest.mark.usefixtures("fs")
    def test_parse_pyproject_file_version_raises_file_not_found_error_if_pyproject_not_found(
        self,
    ):
        with pytest.raises(FileNotFoundError):
            tools.parse_pyproject_file_version(pathlib.Path("/pyproject.toml"))

    @pytest.mark.parametrize(
        "pyproject_contents",
        [
            "[tool.poetry]",
            "[tool]",
            "[project]",
        ],
    )
    def test_parse_pyproject_file_version_raises_error_if_key_not_found(
        self, fs, pyproject_contents
    ):
        # Set up
        fs.create_file("/pyproject.toml", contents=pyproject_contents)

        path = pathlib.Path("/pyproject.toml")
        with pytest.raises(KeyError):
            tools.parse_pyproject_file_version(path)
