# Experimental dataclass generated from Generator/ClassesRef/Post/Post.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Post(PyleecanClass):
    """Abstract class for postprocessing

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Post"
    """Name of the package of the legacy class module"""
