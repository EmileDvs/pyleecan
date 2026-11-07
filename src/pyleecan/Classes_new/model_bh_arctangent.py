# Experimental dataclass generated from Generator/ClassesRef/Material/ModelBH_arctangent.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from .model_bh import ModelBH


@dataclass(eq=False)
class ModelBH_arctangent(ModelBH):
    """Abstract class for BH curve model

    Attributes
    ----------
    k : float or None
        BH curve parameter
        Unit: T; Default: None
    mu_a : float or None
        Saturation permeability parameter
        Default: None
    """

    k: float | None = None
    """BH curve parameter"""
    mu_a: float | None = None
    """Saturation permeability parameter"""
