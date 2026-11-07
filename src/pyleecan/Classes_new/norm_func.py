# Experimental dataclass generated from Generator/ClassesRef/SciDataTool/Norm_func.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Any, Callable

from .normalization import Normalization


@dataclass(eq=False)
class NormFunc(Normalization):
    """Function normalization (lambda x: function(axis))

    Attributes
    ----------
    function : function or None
        function to apply
        Default: None
    """

    function: Callable[..., Any] | None = None
    """function to apply"""

    # Inlined from Methods.SciDataTool.Norm_func.normalize
    def normalize(
        self,
        values,
    ):
        """Normalizes axis values
        Parameters
        ----------
        self: Norm_func
            a Norm_func object
        values: ndarray
            axis values
        Returns
        -------
        Vector of axis values
        """
        return self.function(values)
