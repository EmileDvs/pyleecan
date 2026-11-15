# Experimental pydantic model generated from Generator/ClassesRef/SciDataTool/Norm_indices.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

import numpy as np

from .normalization import Normalization


class NormIndices(Normalization):
    """Return indices instead of axis values

    Attributes
    ----------
    """

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.Norm_indices.normalize
    def normalize(
        self,
        values,
    ):
        """Normalizes axis values
        Parameters
        ----------
        self: Norm_indices
            a Norm_indices object
        values: ndarray
            axis values
        Returns
        -------
        Vector of axis values
        """
        return np.array([i for i in range(len(values))])
