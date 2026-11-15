# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Normalization.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Normalization(PyleecanClass):
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
