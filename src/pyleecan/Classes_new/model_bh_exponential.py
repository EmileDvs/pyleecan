# Experimental dataclass generated from Generator/ClassesRef/Material/ModelBH_exponential.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass


@dataclass(eq=False)
class ModelBH_exponential(PyleecanClass):
    """Abstract class for BH curve model

    Attributes
    ----------
    Bs : float or None
        BH curve parameter
        Unit: T; Default: None
    mu_a : float or None
        Saturation permeability parameter
        Default: None
    """

    Bs: float | None = None
    """BH curve parameter"""
    mu_a: float | None = None
    """Saturation permeability parameter"""

    def __post_init__(self):
        super().__post_init__()
