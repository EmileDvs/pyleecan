# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Norm_ref.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .normalization import Normalization

if TYPE_CHECKING:
    import numpy as np


@dataclass(eq=False)
class NormRef(Normalization):
    """Normalization with a reference value (values/ref)

    Attributes
    ----------
    ref : float
        reference value
        Default: 1
    """

    ref: float = 1
    """reference value"""

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.Norm_ref.normalize
    def normalize(
        self,
        values: np.ndarray,
    ):
        """Normalizes axis values
        Parameters
        ----------
        self: Norm_ref
            a Norm_ref object
        values: ndarray
            axis values
        Returns
        -------
        Vector of axis values
        """
        return values / self.ref
