# Experimental dataclass generated from Generator/ClassesRef/Post/PostFunction.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Any, Callable

from .post import Post


@dataclass(eq=False)
class PostFunction(Post):
    """Post-processing from a user-defined function

    Attributes
    ----------
    run : function or None
        Post-processing that takes an output in argument
        Default: None
    """

    run: Callable[..., Any] | None = None
    """Post-processing that takes an output in argument"""
