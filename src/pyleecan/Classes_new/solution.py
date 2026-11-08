# Experimental dataclass generated from Generator/ClassesRef/Mesh/Solution.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

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
    dimension: int = 2
    """Dimension of the physical problem"""
    unit: str | None = None
    """Unit of the solution"""
