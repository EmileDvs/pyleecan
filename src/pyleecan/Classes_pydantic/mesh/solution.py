# Experimental pydantic model generated from Generator/ClassesRef/Mesh/Solution.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel


class Solution(LegacyModel):
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
    unit : str
        Unit of the solution
        Default: ""
    """

    type_element: str = "triangle"
    """Type of element (Point, Segment2, Triangle3, etc.)"""
    label: str | None = None
    """Label to identify the solution"""
    dimension: int = Field(default=2, ge=1, le=3)
    """Dimension of the physical problem"""
    unit: str = ""
    """Unit of the solution"""

    _package: ClassVar[str] = "Mesh"
    """Name of the package of the legacy class module"""
