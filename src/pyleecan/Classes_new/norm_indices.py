# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Norm_indices.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .normalization import Normalization


@dataclass(eq=False)
class NormIndices(Normalization):
    """Return indices instead of axis values

    Attributes
    ----------
    """

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
