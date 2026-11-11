# Experimental dataclass generated from Generator/ClassesRef/Simulation/ParamExplorer.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from ntpath import basename
from typing import Any, Callable

from ..definitions import PYTHON_DEFAULT_ENCODING
from ..Functions_new.path_tools import abs_file_path
from ._error import CheckTypeError
from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class ParamExplorer(PyleecanClass):
    """Abstract class for the multi-simulation

    Attributes
    ----------
    name : str or None
        Parameter name
        Default: None
    symbol : str or None
        Parameter symbol
        Default: None
    unit : str or None
        Parameter unit
        Default: None
    setter : function or None
        Function that takes a Simulation and a value in argument and modifiers the simulation
        Default: None
    getter : function or None
        Function to return the reference value (simulation as argument)
        Default: None
    """

    name: str | None = None
    """Parameter name"""
    symbol: str | None = None
    """Parameter symbol"""
    unit: str | None = None
    """Parameter unit"""
    setter: Callable[..., Any] | None = None
    """Function that takes a Simulation and a value in argument and modifiers the simulation"""
    getter: Callable[..., Any] | None = None
    """Function to return the reference value (simulation as argument)"""

    # Inlined from Methods.Simulation.ParamExplorer._set_getter
    def _set_getter(self, value):
        """setter of getter"""
        # Create the function if getter is defined as a string (e.g. simu.machine.rotor.slot.W0)
        if isinstance(value, str) and value[:4] == "simu":
            value_split = value.split(".")
            value = (
                "lambda simu: getattr(eval('"
                + ".".join(value_split[:-1])
                + "'), '"
                + value_split[-1]
                + "')"
            )
        if value is None:
            self._getter_str = None
            self._getter_func = None
        elif isinstance(value, str) and "lambda" in value:
            self._getter_str = value
            self._getter_func = eval(value)
        elif isinstance(value, str) and value[-3:] == ".py":
            if "<" in value and ">" in value:
                # path like "<PARAM_DIR>/setter_rotor.py"
                self._getter_str = value
                value = abs_file_path(value)
            else:  # Direct path
                self._getter_str = value
            f = open(value, "r", encoding=PYTHON_DEFAULT_ENCODING)
            exec(f.read(), globals())
            f.close()
            self._getter_func = eval(basename(value[:-3]))
        elif callable(value):
            self._getter_str = None
            self._getter_func = value
        else:
            raise CheckTypeError(
                "For property getter Expected function or str (path to python file or lambda), got: "
                + str(type(value))
            )

    # Inlined from Methods.Simulation.ParamExplorer._set_setter
    def _set_setter(self, value):
        """setter of setter"""
        # Create the function if setter is defined as a string (e.g. simu.machine.rotor.slot.W0)
        if isinstance(value, str) and value[:4] == "simu":
            value_split = value.split(".")
            value = (
                "lambda simu, val: setattr(eval('"
                + ".".join(value_split[:-1])
                + "'), '"
                + value_split[-1]
                + "', val"
                + ")"
            )
        if value is None:
            self._setter_str = None
            self._setter_func = None
        elif isinstance(value, str) and "lambda" in value:
            self._setter_str = value
            self._setter_func = eval(value)
        elif isinstance(value, str) and value[-3:] == ".py":
            if "<" in value and ">" in value:
                # path like "<PARAM_DIR>/setter_rotor.py"
                self._setter_str = value
                value = abs_file_path(value)
            else:  # Direct path
                self._setter_str = value
            f = open(value, "r", encoding=PYTHON_DEFAULT_ENCODING)
            exec(f.read(), globals())
            f.close()
            self._setter_func = eval(basename(value[:-3]))
        elif callable(value):
            self._setter_str = None
            self._setter_func = value
        else:
            raise CheckTypeError(
                "For property setter Expected function or str (path to python file or lambda), got: "
                + str(type(value))
            )

    # Inlined from Methods.Simulation.ParamExplorer.get_desc
    def get_desc(self, simu=None, is_print=False):
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
