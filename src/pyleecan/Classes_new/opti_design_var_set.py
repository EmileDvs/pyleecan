# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiDesignVarSet.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .opti_design_var import OptiDesignVar


@dataclass(eq=False)
class OptiDesignVarSet(OptiDesignVar):
    """Optimization

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
