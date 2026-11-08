# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiSolver.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .opti_problem import OptiProblem
from .xoutput import XOutput


@dataclass(eq=False)
class OptiSolver(PyleecanClass):
    """Optimization solver class

    Attributes
    ----------
    problem : OptiProblem or None
        Problem to solve
        Default: None
    xoutput : XOutput or None
        Optimization results containing every output
        Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.OptiSolver"
    is_keep_all_output : bool
        Boolean to keep every output
        Default: False
    """

    problem: OptiProblem | None = None
    """Problem to solve"""
    xoutput: XOutput | None = None
    """Optimization results containing every output"""
    logger_name: str = "Pyleecan.OptiSolver"
    """Name of the logger to use"""
    is_keep_all_output: bool = False
    """Boolean to keep every output"""
