# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiDesignVar.csv
"""Generated experimental dataclass; do not edit by hand."""

from copy import deepcopy
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable

from .param_explorer import ParamExplorer


@dataclass(eq=False)
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

    space: list[Any] = field(default_factory=partial(deepcopy, [0, 1]))
    """Space of the variable"""
    get_value: Callable[..., Any] | None = None
    """Function of the space to initiate the variable"""
