# Experimental dataclass generated from Generator/ClassesRef/Material/ModelBH_exponential.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

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

    Bs: float | None = field(default=None, metadata={"unit": "T"})
    """BH curve parameter"""
    mu_a: float | None = None
    """Saturation permeability parameter"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
