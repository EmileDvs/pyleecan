"""Functions given by their source (legacy function properties).

A legacy function property accepts a callable, or a string: the source of a
lambda (``"lambda out: out.elec.OP.N0"``) or the path to a python file
defining a function named like the file. The string is kept to save the
function (``as_dict``). Used by the legacy layers of both class
implementations.
"""

from collections.abc import Callable
from os.path import basename, isfile
from types import NoneType, UnionType
from typing import Union, get_args, get_origin

import numpy as np


class SourceFunction:
    """Callable built from its source (lambda code or path to a .py file).

    Parameters
    ----------
    source : str
        Source of a lambda, or path to a python file defining a function with
        the name of the file

    Raises
    ------
    ValueError
        If source is neither a lambda nor the path to a python file
    """

    def __init__(self, source):
        path = resolve_wildcard_path(source) if source.endswith(".py") else source
        if "lambda" in source:
            # Names usable in the lambda, as in the legacy setters' modules
            function = eval(source, {"np": np, "sqrt": np.sqrt, "pi": np.pi})
        elif isfile(path) and path.endswith(".py"):
            namespace = {}
            with open(path, encoding="utf-8") as source_file:
                exec(source_file.read(), namespace)
            function = namespace[basename(path)[:-3]]
        else:
            raise ValueError(
                f"Expected a lambda or the path to a python file, got: {source!r}"
            )
        self.source = source
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __eq__(self, other):
        return isinstance(other, SourceFunction) and other.source == self.source

    def __hash__(self):
        return hash(self.source)

    def __repr__(self):
        return f"SourceFunction({self.source!r})"

    def __reduce__(self):  # pickle and deepcopy through the source
        return (SourceFunction, (self.source,))


def resolve_wildcard_path(path):
    """Path with its "<NAME_DIR>/" prefix replaced by pyleecan.definitions.NAME_DIR.

    Like ``utils.path_tools.abs_file_path`` (``"<PARAM_DIR>/setter_rotor.py"``),
    without its existence check; a path without wildcard is returned as is.
    """
    import re

    path = path.replace("\\", "/")
    match = re.match(r"<([A-Za-z0-9_]+)>/(.*)", path)
    if match is None:
        return path
    from .. import definitions

    root = getattr(definitions, match.group(1), None)
    if root is None:
        return path
    return f"{str(root).replace(chr(92), '/').rstrip('/')}/{match.group(2)}"


def legacy_function_source(value, kind):
    """Source of a legacy function property given as "simu.<path>".

    ParamExplorer.getter, ParamExplorer.setter and DataKeeper.keeper accept a
    path in the simulation (``"simu.machine.rotor.slot.W0"``): the legacy
    setters turned it into a lambda reading ("getter") or writing ("setter")
    that attribute. Other values are returned unchanged (callable, lambda
    source, path to a python file, None).
    """
    if not (isinstance(value, str) and value[:4] == "simu"):
        return value
    *owner, attribute = value.split(".")
    owner = ".".join(owner)
    if kind == "getter":
        return f"lambda simu: getattr(eval('{owner}'), '{attribute}')"
    return f"lambda simu, val: setattr(eval('{owner}'), '{attribute}', val)"


def is_function_annotation(annotation):
    """True if annotation is Callable (or Callable | None)."""
    if annotation is Callable or get_origin(annotation) is Callable:
        return True
    if get_origin(annotation) in (Union, UnionType):
        return any(
            is_function_annotation(option)
            for option in get_args(annotation)
            if option is not NoneType
        )
    return False
