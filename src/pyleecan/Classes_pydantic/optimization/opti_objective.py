# Experimental pydantic model generated from Generator/ClassesRef/Optimization/OptiObjective.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from ..simulation.data_keeper import DataKeeper


class OptiObjective(DataKeeper):
    """Class to distinguish normal DataKeeper from optimization objectives

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
