# Experimental dataclass generated from Generator/ClassesRef/Output/OutPost.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class OutPost(PyleecanClass):
    """Gather the parameters for the post-processings

    Attributes
    ----------
    legend_name : str or None
        Name to use in the legend in case of comparison
        Default: None
    line_color : str or None
        Color to use in case of comparison
        Default: None
    """

    legend_name: str | None = None
    """Name to use in the legend in case of comparison"""
    line_color: str | None = None
    """Color to use in case of comparison"""
