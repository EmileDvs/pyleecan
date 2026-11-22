# Experimental dataclass generated from Generator/ClassesRef/Simulation/DataKeeper.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar

from ...classes_common.functions import legacy_function_source
from .._legacy_class import LegacyClass


@dataclass(eq=False)
class DataKeeper(LegacyClass):
    """Class for defining data to keep on a multi-simulation

    Attributes
    ----------
    name : str
        Data name
        Default: ""
    symbol : str
        Data symbol
        Default: ""
    unit : str
        Data unit
        Default: ""
    keeper : function or None
        Function that takes an Output in argument and return a value
        Default: None
    error_keeper : function or None
        Function that takes a Simulation in argument and returns a value, this attribute enables to handle errors and to put NaN values in the result matrices
        Default: None
    result : [] or None
        List containing datakeeper results for each simulation
        Default: []
    result_ref : Any or None
        Result for the reference simulation
        Default: None
    physic : str or None
        Physic of the tracked quantity
        Default: None
    """

    name: str = ""
    """Data name"""
    symbol: str = ""
    """Data symbol"""
    unit: str = ""
    """Data unit"""
    keeper: Callable[..., Any] | None = None
    """Function that takes an Output in argument and return a value"""
    error_keeper: Callable[..., Any] | None = None
    """Function that takes a Simulation in argument and returns a value, this attribute enables to handle errors and to put NaN values in the result matrices"""
    result: list[Any] = field(default_factory=list)
    """List containing datakeeper results for each simulation"""
    result_ref: Any = None
    """Result for the reference simulation"""
    physic: str | None = None
    """Physic of the tracked quantity"""

    _custom_setters: ClassVar[tuple[str, ...]] = ("keeper",)
    """Fields set by a legacy custom setter (_set_<field>)"""
    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.DataKeeper._set_keeper
    def _set_keeper(self, value) -> None:
        """setter of keeper

        A callable, the source of a lambda (numpy usable as np, sqrt and pi), the
        path to a python file (with a wildcard: "<PARAM_DIR>/keeper.py") or a path
        in the simulation ("simu.machine.rotor.slot.W0", as the legacy setter).
        The field keeps the function with its source (SourceFunction, saved by
        its source).

        Parameters
        ----------
        self : DataKeeper
            A DataKeeper object
        value : callable or str or None
            Function extracting the kept data from an output
        """
        self.keeper = legacy_function_source(value, "setter")
