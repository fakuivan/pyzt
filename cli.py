from subprocess import run
import json
from typing import Union, cast

# MyPy doesn't support recursive type definitions
JSONType = Union[  # type: ignore[misc]
    None,
    bool,
    int,
    float,
    str,
    dict[str, "JSONType"],  # type: ignore[misc]
    list["JSONType"],  # type: ignore[misc]
]


def zerotier_cli_j(option: str, *args: str) -> JSONType:
    command = ("zerotier-cli", "-j", option) + args
    res = run(command, capture_output=True, text=True, check=True)
    return cast(JSONType, json.loads(res.stdout))
