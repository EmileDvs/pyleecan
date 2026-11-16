# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Norm_affine.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, ClassVar

from .normalization import Normalization

if TYPE_CHECKING:
    import numpy as np


@dataclass(eq=False)
class NormAffine(Normalization):
    """Affine function normalization (slope x axis + offset)

    Attributes
    ----------
    slope : float
        slope of the axis function
        Default: 1
    offset : float
        offset of the axis function
        Default: 0
    """

    slope: float = 1
    """slope of the axis function"""
    offset: float = 0
    """offset of the axis function"""

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.Norm_affine.normalize
    def normalize(
        self,
        values: np.ndarray,
    ):
        """Normalizes axis values
        Parameters
        ----------
        self: Norm_affine
            a Norm_affine object
        values: ndarray
            axis values
        Returns
        -------
        Vector of axis values
        """
        return values * self.slope + self.offset
