# Experimental pydantic model generated from Generator/ClassesRef/Optimization/OptiDesignVar.csv
"""Generated experimental pydantic model; do not edit by hand."""

from copy import deepcopy
from functools import partial
from typing import Any, Callable, ClassVar

from pydantic import Field

from ..simulation.param_explorer import ParamExplorer


class OptiDesignVar(ParamExplorer):
    """Abstract class for OptiDesignVar (Optimization)

    Attributes
    ----------
    space : list
        Space of the variable
        Default: [0, 1]
    get_value : function or None
        Function of the space to initiate the variable
        Default: None
    """

    space: list[Any] = Field(default_factory=partial(deepcopy, [0, 1]))
    """Space of the variable"""
    get_value: Callable[..., Any] | None = None
    """Function of the space to initiate the variable"""

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
