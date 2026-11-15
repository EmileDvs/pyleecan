# Experimental pydantic model generated from Generator/ClassesRef/Loss/LossModel.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, ClassVar

from .._legacy_model import LegacyModel


class LossModel(LegacyModel):
    """Abstract Loss Model Class

    Attributes
    ----------
    name : str
        Name of the loss simulation (has to be unique)
        Default: ""
    group : str
        Group in which the loss will be computed
        Default: ""
    is_show_fig : bool
        True to show the plot of the curve fitting
        Default: False
    coeff_dict : dict or None
        dict of coefficients to compute losses with respect to frequency
        Default: None
    """

    name: str = ""
    """Name of the loss simulation (has to be unique)"""
    group: str = ""
    """Group in which the loss will be computed"""
    is_show_fig: bool = False
    """True to show the plot of the curve fitting"""
    coeff_dict: dict[str, Any] | None = None
    """dict of coefficients to compute losses with respect to frequency"""

    _package: ClassVar[str] = "Loss"
    """Name of the package of the legacy class module"""
