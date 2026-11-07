# Experimental dataclass generated from Generator/ClassesRef/Elmer/Elmer.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class Elmer(PyleecanClass):
    """Abstract parent class for all Elmer related convienence classes

    Attributes
    ----------
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Elmer"
    """

    logger_name: str = "Pyleecan.Elmer"
    """Name of the logger to use"""

    def __post_init__(self):
        super().__post_init__()
