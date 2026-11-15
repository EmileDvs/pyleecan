# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Data.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np

from .._check import check_var
from .._import import import_class
from .._pyleecan_class import PyleecanClass
from .normalization import Normalization


@dataclass(eq=False)
class Data(PyleecanClass):
    """Abstract class for all kinds of data

    Attributes
    ----------
    symbol : str
        Symbol of the variable (in latex syntax)
        Default: ""
    name : str
        Name of the physical quantity (to be used in plots)
        Default: ""
    unit : str
        Unit of the physical quantity (to be used in plots)
        Default: ""
    normalizations : {Normalization}
        Normalizations available for the field and its axes
        Default: {}
    """

    symbol: str = ""
    """Symbol of the variable (in latex syntax)"""
    name: str = ""
    """Name of the physical quantity (to be used in plots)"""
    unit: str = ""
    """Unit of the physical quantity (to be used in plots)"""
    normalizations: dict[str, Normalization] = field(default_factory=dict)
    """Normalizations available for the field and its axes"""

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.Data._set_normalizations
    def _set_normalizations(self, value):
        """setter of normalizations"""
        if type(value) is dict:
            for key, obj in value.items():
                if type(obj) is dict:
                    class_obj = import_class(obj.get("__class__"), "normalizations")
                    value[key] = class_obj.from_dict(obj)
                elif isinstance(
                    obj, (float, int, np.int32, np.int64, np.float32, np.float64)
                ):
                    from .norm_ref import NormRef

                    value[key] = NormRef(ref=obj)
                elif isinstance(obj, (np.ndarray, list)):
                    from .norm_vector import NormVector

                    value[key] = NormVector(vector=np.asarray(obj))
        if type(value) is int and value == -1:
            value = {}
        check_var("normalizations", value, "{Normalization}")
        self._normalizations = value
