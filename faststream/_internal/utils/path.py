import re
from collections.abc import Callable
from re import Pattern

from faststream.exceptions import SetupError

PARAM_REGEX = re.compile(r"{([a-zA-Z0-9_]+|tail\+)}")
TAIL_PARAM = "tail+"


def compile_path(
    path: str,
    replace_symbol: str,
    tail_symbol: str = "",
    patch_regex: Callable[[str], str] = lambda x: x,
) -> tuple[Pattern[str] | None, str]:
    path_regex = "^.*?"
    original_path = ""

    idx = 0
    params = set()
    duplicated_params = set()
    for match in PARAM_REGEX.finditer(path):
        p = param_name = match.groups("str")[0]
        after_match, repl_symbol = "[^.]", replace_symbol
        if param_name == TAIL_PARAM and tail_symbol:
            after_match = "."
            repl_symbol = tail_symbol

        path_regex += re.escape(path[idx : match.start()])
        path_regex += f"(?P<{param_name.replace('+', '')}>{after_match}+)"

        original_path += path[idx : match.start()]
        original_path += repl_symbol

        if param_name in params:
            duplicated_params.add(param_name)
        else:
            params.add(param_name)

        idx = match.end()

    if duplicated_params:
        names = ", ".join(sorted(duplicated_params))
        ending = "s" if len(duplicated_params) > 1 else ""
        msg = f"Duplicated param name{ending} {names} at path {path}"
        raise SetupError(msg)

    if idx == 0:
        regex = None
    else:
        path_regex += re.escape(path[idx:]) + "$"
        regex = re.compile(patch_regex(path_regex))

    original_path += path[idx:]
    return regex, original_path
