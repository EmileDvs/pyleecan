# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Norm_vector.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from ...classes_common.errors import NormError
from .normalization import Normalization


@dataclass(eq=False)
class NormVector(Normalization):
    """Normalization by a given vector

    Attributes
    ----------
    vector : ndarray or None
        vector to replace axis values
        Default: None
    """

    vector: np.ndarray | None = None
    """vector to replace axis values"""

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.Norm_vector.normalize
    def normalize(
        self,
        values,
    ):
        """Normalizes axis values
        Parameters
        ----------
        self: Norm_vector
            a Norm_vector object
        values: ndarray
            axis values
        Returns
        -------
        Vector of axis values
        """
        if len(values) != len(self.vector):
            raise NormError(
                "Normalization vector is not the same length as axis, cannot normalize"
            )
        else:
            return self.vector
