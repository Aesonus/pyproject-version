import pathlib

import pytest

from py_version import tools


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
    fs, package_init_template: str, old_version, expected_version
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
