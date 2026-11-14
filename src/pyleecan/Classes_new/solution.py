# Experimental dataclass generated from Generator/ClassesRef/Mesh/Solution.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Solution(PyleecanClass):
    """Abstract class for solution related classes.

    Attributes
    ----------
    type_element : str
        Type of element (Point, Segment2, Triangle3, etc.)
        Default: "triangle"
    label : str or None
        Label to identify the solution
        Default: None
    dimension : int
        Dimension of the physical problem
        Default: 2; Minimum: 1; Maximum: 3
    unit : str or None
        Unit of the solution
        Default: None
    """

    type_element: str = "triangle"
    """Type of element (Point, Segment2, Triangle3, etc.)"""
    label: str | None = None
    """Label to identify the solution"""
    dimension: int = field(default=2, metadata={"min": 1, "max": 3})
    """Dimension of the physical problem"""
    unit: str | None = None
    """Unit of the solution"""

    _package: ClassVar[str] = "Mesh"
    """Name of the package of the legacy class module"""
