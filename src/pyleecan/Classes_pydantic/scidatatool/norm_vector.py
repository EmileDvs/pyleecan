# Experimental pydantic model generated from Generator/ClassesRef/SciDataTool/Norm_vector.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...classes_common.errors import NormError
from .._pyleecan_model import NDArray
from .normalization import Normalization

if TYPE_CHECKING:
    pass


class NormVector(Normalization):
    """Normalization by a given vector

    Attributes
    ----------
    vector : ndarray or None
        vector to replace axis values
        Default: None
    """

    vector: NDArray | None = None
    """vector to replace axis values"""

    _package: ClassVar[str] = "SciDataTool"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.SciDataTool.Norm_vector.normalize
    def normalize(
        self,
        values: np.ndarray,
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
