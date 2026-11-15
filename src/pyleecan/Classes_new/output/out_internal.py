# Experimental dataclass generated from Generator/ClassesRef/Output/OutInternal.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class OutInternal(PyleecanClass):
    """Abstract class whose childs enable to store outputs related to a specific model

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""
