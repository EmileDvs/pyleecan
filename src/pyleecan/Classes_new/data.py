# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Data.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions.Load.retrocompatibility import (
    construct_experimental_class as _construct_experimental_class,
)
from ..Functions.Load.retrocompatibility import (
    import_experimental_class as _import_experimental_class,
)
from ._check import check_var
from ._pyleecan_class import PyleecanClass
from .normalization import Normalization
from .out_elec import OutElec
from .out_force import OutForce
from .out_geo import OutGeo
from .out_loss import OutLoss
from .out_mag import OutMag
from .out_struct import OutStruct


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
    normalizations: dict[str, Normalization] = {}
    """Normalizations available for the field and its axes"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Data,
                OutElec,
                OutForce,
                OutGeo,
                OutLoss,
                OutMag,
                OutStruct,
            ),
        ):
            raise TypeError(
                "Data parent must be an instance of Data or OutElec or OutForce or OutGeo or OutLoss or OutMag or OutStruct, or None; "
                + f"got {type(parent).__name__}"
            )

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
