# Experimental dataclass generated from Generator/ClassesRef/Output/LUTslip.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .lut import LUT


@dataclass(eq=False)
class LUTslip(LUT):
    """Look Up Table class for u0/slip OP matrix

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""
