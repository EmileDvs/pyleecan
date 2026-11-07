# Experimental dataclass generated from Generator/ClassesRef/Loss/LossModel.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

from ._pyleecan_class import PyleecanClass
from .loss import Loss


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

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Loss,)):
            raise TypeError(
                "LossModel parent must be an instance of Loss, or None; "
                + f"got {type(parent).__name__}"
            )
