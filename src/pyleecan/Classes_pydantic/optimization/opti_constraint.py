# Experimental pydantic model generated from Generator/ClassesRef/Optimization/OptiConstraint.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from ..simulation.data_keeper import DataKeeper


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
