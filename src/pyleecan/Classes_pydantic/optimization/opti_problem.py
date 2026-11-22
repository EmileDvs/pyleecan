# Experimental pydantic model generated from Generator/ClassesRef/Optimization/OptiProblem.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, Callable, ClassVar

from pydantic import Field

from .._legacy_model import LegacyModel
from ..simulation.data_keeper import DataKeeper
from ..simulation.simulation import Simulation
from .opti_constraint import OptiConstraint
from .opti_design_var import OptiDesignVar
from .opti_objective import OptiObjective


class OptiProblem(LegacyModel):
    """Multi-objectives optimization problem with some constraints

    Attributes
    ----------
    simu : Simulation or None
        Default simulation
        Default: Simulation()
    design_var : [OptiDesignVar] or None
        List of design variables
        Default: []
    obj_func : [OptiObjective] or None
        List of objective functions
        Default: []
    eval_func : function or None
        Function to evaluate before computing obj function and constraints
        Default: None
    constraint : [OptiConstraint] or None
        List containing the constraints
        Default: []
    preprocessing : function or None
        Function to execute a preprocessing on the simulation right before it is run.
        Default: None
    datakeeper_list : [DataKeeper] or None
        List of DataKeepers to run on every output
        Default: []
    """

    simu: Simulation = Field(default_factory=lambda: Simulation())
    """Default simulation"""
    design_var: list[OptiDesignVar] = Field(default_factory=list)
    """List of design variables"""
    obj_func: list[OptiObjective] = Field(default_factory=list)
    """List of objective functions"""
    eval_func: Callable[..., Any] | None = None
    """Function to evaluate before computing obj function and constraints"""
    constraint: list[OptiConstraint] = Field(default_factory=list)
    """List containing the constraints """
    preprocessing: Callable[..., Any] | None = None
    """Function to execute a preprocessing on the simulation right before it is run."""
    datakeeper_list: list[DataKeeper] = Field(default_factory=list)
    """List of DataKeepers to run on every output"""

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
