# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModel.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class LossModel(PyleecanClass):
    """Abstract Loss Model Class

    Attributes
    ----------
    name : str or None
        Name of the loss simulation (has to be unique)
        Default: None
    group : str or None
        Group in which the loss will be computed
        Default: None
    is_show_fig : bool
        True to show the plot of the curve fitting
        Default: False
    coeff_dict : dict or None
        dict of coefficients to compute losses with respect to frequency
        Default: {}
    """

    name: str | None = None
    """Name of the loss simulation (has to be unique)"""
    group: str | None = None
    """Group in which the loss will be computed"""
    is_show_fig: bool = False
    """True to show the plot of the curve fitting"""
    coeff_dict: dict[str, Any] | None = field(default_factory=dict)
    """dict of coefficients to compute losses with respect to frequency"""
