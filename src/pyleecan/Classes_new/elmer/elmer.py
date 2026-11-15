# Experimental dataclass generated from Generator/ClassesRef/Elmer/Elmer.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Elmer(PyleecanClass):
    """Abstract parent class for all Elmer related convienence classes

    Attributes
    ----------
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Elmer"
    """

    WHITESPACE: ClassVar[str] = " "
    INDENT: ClassVar[str] = 2 * WHITESPACE
    COMMENT: ClassVar[str] = "! "
    NEWLINE: ClassVar[str] = "\n"
    END: ClassVar[str] = "End"

    logger_name: str = "Pyleecan.Elmer"
    """Name of the logger to use"""

    _package: ClassVar[str] = "Elmer"
    """Name of the package of the legacy class module"""
