# Experimental pydantic model generated from Generator/ClassesRef/Output/OutPost.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from .._legacy_model import LegacyModel


class OutPost(LegacyModel):
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
