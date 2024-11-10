# Pyproject Version

A tool to manage the version of your Python project.

(Note: This is a work in progress and currently only supports Poetry based projects.)

## Installation

```bash
pip install pyproject-version
```

## Usage

By default, this tool will only change the version in the `pyproject.toml` file located in the current directory. If you want to change the version in a different directory, use the `--project-root` option.

To sync the version in the `pyproject.toml` file with the version in the `__init__.py` file of the project, add the following to the `pyproject.toml` file:

```toml
[tool.pyproject-version]
files = ["my_project/__init__.py"]
```

### Version Bump

```bash
pyproject-version bump [OPTIONS] {major|minor|patch|prerelease|build}
```

**Options:**

+ `-r`, `--project-root` `DIRECTORY`

    The root of the Python project.
+ `-t`, `--token` `TEXT`

    The token to use for pre-release and build versions.
+ `--dry-run`

    Print the new version without updating.


### Version Set

```bash
pyproject-version set-version [OPTIONS] NEW_VERSION
```

`NEW_VERSION` is the new version to set. It will be validated by the [`semver`](https://pypi.org/project/semver/) library.

**Options:**

+ `-r`, `--project-root` `DIRECTORY`

    The root of the Python project.
+ `--dry-run`

    Print the new version without updating.


## License

MIT License, see [LICENSE](LICENSE) for more information.