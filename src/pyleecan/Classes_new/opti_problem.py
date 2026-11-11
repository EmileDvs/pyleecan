# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiProblem.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any, Callable

from ._pyleecan_class import PyleecanClass
from .data_keeper import DataKeeper
from .opti_constraint import OptiConstraint
from .opti_design_var import OptiDesignVar
from .opti_objective import OptiObjective
from .simulation import Simulation


@dataclass(eq=False)
class OptiProblem(PyleecanClass):
    """Multi-objectives optimization problem with some constraints

    Attributes
    ----------
    simu : Simulation or None
        Default simulation
        Default: Simulation()
    design_var : [OptiDesignVar] or None
        List of design variables
        Default: None
    obj_func : [OptiObjective] or None
        List of objective functions
        Default: None
    eval_func : function or None
        Function to evaluate before computing obj function and constraints
        Default: None
    constraint : [OptiConstraint] or None
        List containing the constraints
        Default: None
    preprocessing : function or None
        Function to execute a preprocessing on the simulation right before it is run.
        Default: None
    datakeeper_list : [DataKeeper] or None
        List of DataKeepers to run on every output
        Default: None
    """

    simu: Simulation | None = field(
        default_factory=lambda: Simulation(), metadata={"default_class": "Simulation"}
    )
    """Default simulation"""
    design_var: list[OptiDesignVar] | None = None
    """List of design variables"""
    obj_func: list[OptiObjective] | None = None
    """List of objective functions"""
    eval_func: Callable[..., Any] | None = None
    """Function to evaluate before computing obj function and constraints"""
    constraint: list[OptiConstraint] | None = None
    """List containing the constraints """
    preprocessing: Callable[..., Any] | None = None
    """Function to execute a preprocessing on the simulation right before it is run."""
    datakeeper_list: list[DataKeeper] | None = None
    """List of DataKeepers to run on every output"""
