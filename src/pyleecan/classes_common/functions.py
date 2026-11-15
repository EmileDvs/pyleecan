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
        if "lambda" in source:
            function = eval(source, {"np": np})
        elif isfile(source) and source.endswith(".py"):
            namespace = {}
            with open(source, encoding="utf-8") as source_file:
                exec(source_file.read(), namespace)
            function = namespace[basename(source)[:-3]]
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
