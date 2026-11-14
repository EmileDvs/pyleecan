# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiConstraint.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .data_keeper import DataKeeper


@dataclass(eq=False)
class OptiConstraint(DataKeeper):
    """Constraint of the optimization problem

    Attributes
    ----------
    type_const : str
        Type of comparison ( "==", "<=", ">=", "<",">")
        Default: "<="
    value : float
        Value to compare
        Default: 0
    """

    type_const: str = "<="
    """Type of comparison ( "==", "<=", ">=", "<",">")"""
    value: float = 0
    """Value to compare"""

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
