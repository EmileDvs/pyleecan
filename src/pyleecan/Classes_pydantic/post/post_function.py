# Experimental pydantic model generated from Generator/ClassesRef/Post/PostFunction.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, Callable, ClassVar

from .post import Post


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

    _package: ClassVar[str] = "Post"
    """Name of the package of the legacy class module"""
