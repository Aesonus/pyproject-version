import pytest


@pytest.fixture
def fakefs_onepackage(fs):
    fs.add_real_directory("tests/one_package_root", target_path="/", read_only=False)
    yield fs


@pytest.fixture
def fakefs_project_section(fs):
    fs.add_real_directory("tests/project_section", target_path="/", read_only=False)
    yield fs


@pytest.fixture
def package_init_template():
    return '''"""Test init file."""

__version__ = {version}
'''
