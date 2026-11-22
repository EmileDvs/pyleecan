# Experimental dataclass generated from Generator/ClassesRef/Simulation/ParamExplorer.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, ClassVar

from ...classes_common.functions import legacy_function_source
from .._legacy_class import LegacyClass

if TYPE_CHECKING:
    from .simulation import Simulation


@dataclass(eq=False)
class ParamExplorer(LegacyClass):
    """Abstract class for the multi-simulation

    Attributes
    ----------
    name : str
        Parameter name
        Default: ""
    symbol : str
        Parameter symbol
        Default: ""
    unit : str
        Parameter unit
        Default: ""
    setter : function or None
        Function that takes a Simulation and a value in argument and modifiers the simulation
        Default: None
    getter : function or None
        Function to return the reference value (simulation as argument)
        Default: None
    """

    name: str = ""
    """Parameter name"""
    symbol: str = ""
    """Parameter symbol"""
    unit: str = ""
    """Parameter unit"""
    setter: Callable[..., Any] | None = None
    """Function that takes a Simulation and a value in argument and modifiers the simulation"""
    getter: Callable[..., Any] | None = None
    """Function to return the reference value (simulation as argument)"""

    _custom_setters: ClassVar[tuple[str, ...]] = ("getter", "setter")
    """Fields set by a legacy custom setter (_set_<field>)"""
    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.ParamExplorer._set_getter
    def _set_getter(self, value) -> None:
        """setter of getter

        A callable, the source of a lambda, the path to a python file (with a
        wildcard: "<PARAM_DIR>/getter_rotor.py") or a path in the simulation
        ("simu.machine.rotor.slot.W0": the lambda reading it). The field keeps the
        function with its source (SourceFunction, saved by its source).

        Parameters
        ----------
        self : ParamExplorer
            A ParamExplorer object
        value : callable or str or None
            Getter of the parameter
        """
        self.getter = legacy_function_source(value, "getter")

    # Inlined from Methods.Simulation.ParamExplorer._set_setter
    def _set_setter(self, value) -> None:
        """setter of setter

        A callable, the source of a lambda, the path to a python file (with a
        wildcard: "<PARAM_DIR>/setter_rotor.py") or a path in the simulation
        ("simu.machine.rotor.slot.W0": the lambda setting it). The field keeps the
        function with its source (SourceFunction, saved by its source).

        Parameters
        ----------
        self : ParamExplorer
            A ParamExplorer object
        value : callable or str or None
            Setter of the parameter
        """
        self.setter = legacy_function_source(value, "setter")

    # Inlined from Methods.Simulation.ParamExplorer.get_desc
    def get_desc(self, simu: Simulation | None = None, is_print: bool = False) -> str:
        """Generate a string description of the ParamExplorer

        Parameters
        ----------
        self : ParamExplorer
            A ParamExplorer object
        simu : Simulation
            Optional simulation object to add reference value
        is_print : bool
            True to call print on desc

        Returns
        -------
        desc: str
            Description (for instance "W0: N values from 0.001 to 0.01 (ref=0.0015) [m]")
        """

        desc = ""
        desc += self.symbol + ": "
        N = self.get_N()
        desc += str(N) + " value"
        if N > 1:
            desc += "s"

        min_value = self.get_min()
        max_value = self.get_max()
        if min_value is not None and max_value is not None and N > 1:
            desc += (
                " from " + format(min_value, ".4g") + " to " + format(max_value, ".4g")
            )
        if self.getter is not None and simu is not None:
            ref = self.getter(simu)
            desc += " (ref=" + format(ref, ".4g") + ")"
        if self.unit is not None:
            desc += " [" + self.unit + "]"

        if is_print:
            print(desc)
        return desc
