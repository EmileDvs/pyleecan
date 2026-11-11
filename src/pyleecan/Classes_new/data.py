# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Data.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ._check import check_var
from ._pyleecan_class import PyleecanClass
from ._pyleecan_class import (
    construct_experimental_class as _construct_experimental_class,
)
from ._pyleecan_class import import_experimental_class as _import_experimental_class
from .normalization import Normalization


@dataclass(eq=False)
class Data(PyleecanClass):
    """Abstract class for all kinds of data

    Attributes
    ----------
    symbol : str or None
        Symbol of the variable (in latex syntax)
        Default: None
    name : str or None
        Name of the physical quantity (to be used in plots)
        Default: None
    unit : str or None
        Unit of the physical quantity (to be used in plots)
        Default: None
    normalizations : {Normalization}
        Normalizations available for the field and its axes
        Default: {}
    """

    symbol: str | None = None
    """Symbol of the variable (in latex syntax)"""
    name: str | None = None
    """Name of the physical quantity (to be used in plots)"""
    unit: str | None = None
    """Unit of the physical quantity (to be used in plots)"""
    normalizations: dict[str, Normalization] = field(default_factory=dict)
    """Normalizations available for the field and its axes"""

    # Inlined from Methods.SciDataTool.Data._set_normalizations
    def _set_normalizations(self, value):
        """setter of normalizations"""
        if type(value) is dict:
            for key, obj in value.items():
                if type(obj) is dict:
                    class_obj = _import_experimental_class(
                        "pyleecan.Classes", obj.get("__class__"), "normalizations"
                    )
                    value[key] = _construct_experimental_class(class_obj, obj)
                elif isinstance(
                    obj, (float, int, np.int32, np.int64, np.float32, np.float64)
                ):
                    NormRef = _import_experimental_class(
                        "pyleecan.Classes", "NormRef", "normalizations"
                    )
                    value[key] = NormRef(ref=obj)
                elif isinstance(obj, (np.ndarray, list)):
                    NormVector = _import_experimental_class(
                        "pyleecan.Classes", "NormVector", "normalizations"
                    )
                    value[key] = NormVector(vector=np.asarray(obj))
        if type(value) is int and value == -1:
            value = {}
        check_var("normalizations", value, "{Normalization}")
        self._normalizations = value
