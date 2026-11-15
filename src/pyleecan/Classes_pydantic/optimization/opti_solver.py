# Experimental pydantic model generated from Generator/ClassesRef/Optimization/OptiSolver.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from ..output.xoutput import XOutput
from .opti_problem import OptiProblem


class OptiSolver(LegacyModel):
    """Optimization solver class

    Attributes
    ----------
    problem : OptiProblem or None
        Problem to solve
        Default: OptiProblem()
    xoutput : XOutput or None
        Optimization results containing every output
        Default: XOutput()
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.OptiSolver"
    is_keep_all_output : bool
        Boolean to keep every output
        Default: False
    """

    problem: OptiProblem | None = Field(default_factory=lambda: OptiProblem())
    """Problem to solve"""
    xoutput: XOutput | None = Field(default_factory=lambda: XOutput())
    """Optimization results containing every output"""
    logger_name: str = "Pyleecan.OptiSolver"
    """Name of the logger to use"""
    is_keep_all_output: bool = False
    """Boolean to keep every output"""

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
