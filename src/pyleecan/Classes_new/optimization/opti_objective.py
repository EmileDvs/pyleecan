# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiObjective.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from ..simulation.data_keeper import DataKeeper


@dataclass(eq=False)
class OptiObjective(DataKeeper):
    """Class to distinguish normal DataKeeper from optimization objectives

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
