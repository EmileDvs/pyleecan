# Experimental pydantic model generated from Generator/ClassesRef/Optimization/OptiBayesAlg.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .opti_solver import OptiSolver


class OptiBayesAlg(OptiSolver):
    """Bayesian algorithm class

    Attributes
    ----------
    nb_iter : int
        Number of iterations
        Default: 15; Minimum: 1
    nb_start : int
        Number of starting points
        Default: 300; Minimum: 1
    criterion : str
        Point selection criteria
        Default: "PI"
    kernel : int
        Type of kernel
        Default: 0; Minimum: 0; Maximum: 0
    """

    nb_iter: int = Field(default=15, ge=1)
    """Number of iterations"""
    nb_start: int = Field(default=300, ge=1)
    """Number of starting points"""
    criterion: str = "PI"
    """Point selection criteria"""
    kernel: int = Field(default=0, ge=0, le=0)
    """Type of kernel"""

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
