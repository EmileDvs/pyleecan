# Experimental pydantic model generated from Generator/ClassesRef/Material/ModelBH_arctangent.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from pydantic import Field

from .model_bh import ModelBH


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

    k: float | None = Field(default=None, json_schema_extra={"unit": "T"})
    """BH curve parameter"""
    mu_a: float | None = None
    """Saturation permeability parameter"""

    _package: ClassVar[str] = "Material"
    """Name of the package of the legacy class module"""
