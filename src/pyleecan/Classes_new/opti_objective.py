# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiObjective.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .data_keeper import DataKeeper


@dataclass(eq=False)
class OptiObjective(DataKeeper):
    """Class to distinguish normal DataKeeper from optimization objectives

    Attributes
    ----------
    """
