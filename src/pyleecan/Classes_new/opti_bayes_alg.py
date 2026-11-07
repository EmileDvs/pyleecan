# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiBayesAlg.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .opti_solver import OptiSolver


@dataclass(eq=False)
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

    nb_iter: int = 15
    """Number of iterations"""
    nb_start: int = 300
    """Number of starting points"""
    criterion: str = "PI"
    """Point selection criteria"""
    kernel: int = 0
    """Type of kernel"""
