# Experimental pydantic model generated from Generator/ClassesRef/SciDataTool/Normalization.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from .._pyleecan_model import PyleecanModel


class Normalization(PyleecanModel):
    """Abstract class for normalizations

    Attributes
    ----------
    unit : str
        Normalization must be applied on axis values in this unit
        Default: "SI"
    """

    unit: str = "SI"
    """Normalization must be applied on axis values in this unit"""

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""
