# Experimental pydantic model generated from Generator/ClassesRef/SciDataTool/Norm_ref.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

from .normalization import Normalization


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
        values,
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
