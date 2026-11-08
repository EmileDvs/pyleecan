# Experimental dataclass generated from Generator/ClassesRef/Simulation/DataKeeper.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from ntpath import basename
from typing import Any, Callable

from ..definitions import PYTHON_DEFAULT_ENCODING
from ..Functions.path_tools import abs_file_path
from ._check import CheckTypeError
from ._pyleecan_class import PyleecanClass
from .opti_problem import OptiProblem
from .output import Output
from .var_simu import VarSimu


@dataclass(eq=False)
class DataKeeper(PyleecanClass):
    """Class for defining data to keep on a multi-simulation

    Attributes
    ----------
    name : str or None
        Data name
        Default: None
    symbol : str or None
        Data symbol
        Default: None
    unit : str or None
        Data unit
        Default: None
    keeper : function or None
        Function that takes an Output in argument and return a value
        Default: None
    error_keeper : function or None
        Function that takes a Simulation in argument and returns a value, this attribute enables to handle errors and to put NaN values in the result matrices
        Default: None
    result : [] or None
        List containing datakeeper results for each simulation
        Default: None
    result_ref : Any or None
        Result for the reference simulation
        Default: None
    physic : str or None
        Physic of the tracked quantity
        Default: None
    """

    name: str | None = None
    """Data name"""
    symbol: str | None = None
    """Data symbol"""
    unit: str | None = None
    """Data unit"""
    keeper: Callable[..., Any] | None = None
    """Function that takes an Output in argument and return a value"""
    error_keeper: Callable[..., Any] | None = None
    """Function that takes a Simulation in argument and returns a value, this attribute enables to handle errors and to put NaN values in the result matrices"""
    result: list[Any] | None = field(default_factory=list)
    """List containing datakeeper results for each simulation"""
    result_ref: Any = None
    """Result for the reference simulation"""
    physic: str | None = None
    """Physic of the tracked quantity"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                OptiProblem,
                Output,
                VarSimu,
            ),
        ):
            raise TypeError(
                "DataKeeper parent must be an instance of OptiProblem or Output or VarSimu, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Simulation.DataKeeper._set_keeper
    def _set_keeper(self, value):
        """setter of keeper"""
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
            self._keeper_str = None
            self._keeper_func = None
        elif isinstance(value, str) and "lambda" in value:
            self._keeper_str = value
            self._keeper_func = eval(value)
        elif isinstance(value, str) and value[-3:] == ".py":
            if "<" in value and ">" in value:
                # path like "<PARAM_DIR>/keeper_rotor.py"
                self._keeper_str = value
                value = abs_file_path(value)
            else:  # Direct path
                self._keeper_str = value
            f = open(value, "r", encoding=PYTHON_DEFAULT_ENCODING)
            exec(f.read(), globals())
            f.close()
            self._keeper_func = eval(basename(value[:-3]))
        elif callable(value):
            self._keeper_str = None
            self._keeper_func = value
        else:
            raise CheckTypeError(
                "For property keeper Expected function or str (path to python file or lambda), got: "
                + str(type(value))
            )
