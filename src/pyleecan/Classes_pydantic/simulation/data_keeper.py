# Experimental pydantic model generated from Generator/ClassesRef/Simulation/DataKeeper.csv
"""Generated experimental pydantic model; do not edit by hand."""

from ntpath import basename
from typing import Any, Callable, ClassVar

from pydantic import Field

from ...classes_common.errors import CheckTypeError
from ...definitions import PYTHON_DEFAULT_ENCODING
from ...Functions_new.path_tools import abs_file_path
from .._legacy_model import LegacyModel


class DataKeeper(LegacyModel):
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
    result: list[Any] | None = Field(default_factory=list)
    """List containing datakeeper results for each simulation"""
    result_ref: Any = None
    """Result for the reference simulation"""
    physic: str | None = None
    """Physic of the tracked quantity"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

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
