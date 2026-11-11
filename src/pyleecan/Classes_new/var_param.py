# Experimental dataclass generated from Generator/ClassesRef/Simulation/VarParam.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

from .param_explorer import ParamExplorer
from .var_simu import VarSimu


@dataclass(eq=False)
class VarParam(VarSimu):
    """Handle multisimulation by varying parameters

    Attributes
    ----------
    paramexplorer_list : [ParamExplorer] or None
        List containing ParamSetter to define every simulation
        Default: []
    """

    NAME: ClassVar = "Parameter Sweep"
    paramexplorer_list: list[ParamExplorer] | None = field(default_factory=list)
    """List containing ParamSetter to define every simulation"""
