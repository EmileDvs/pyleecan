# Experimental pydantic model generated from Generator/ClassesRef/Elmer/Elmer.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from .._pyleecan_model import PyleecanModel


class Elmer(PyleecanModel):
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
