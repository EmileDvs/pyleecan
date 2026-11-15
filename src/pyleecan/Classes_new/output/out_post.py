# Experimental dataclass generated from Generator/ClassesRef/Output/OutPost.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

from .._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class OutPost(PyleecanClass):
    """Gather the parameters for the post-processings

    Attributes
    ----------
    legend_name : str
        Name to use in the legend in case of comparison
        Default: ""
    line_color : str
        Color to use in case of comparison
        Default: ""
    """

    legend_name: str = ""
    """Name to use in the legend in case of comparison"""
    line_color: str = ""
    """Color to use in case of comparison"""

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""
