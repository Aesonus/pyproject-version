"""Module for tools that are used in the project."""

import io
import pathlib
import re
import tokenize


def change_file_version(path: pathlib.Path, new_version: str) -> None:
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
