# Experimental pydantic model generated from Generator/ClassesRef/Simulation/VarParam.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .param_explorer import ParamExplorer
from .var_simu import VarSimu


class VarParam(VarSimu):
    """Handle multisimulation by varying parameters

    Attributes
    ----------
    paramexplorer_list : [ParamExplorer] or None
        List containing ParamSetter to define every simulation
        Default: []
    """

    NAME: ClassVar = "Parameter Sweep"

    paramexplorer_list: list[ParamExplorer] = Field(default_factory=list)
    """List containing ParamSetter to define every simulation"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""
