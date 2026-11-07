# Experimental dataclass generated from Generator/ClassesRef/Import/ImportMatrixVal.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .import_matrix import ImportMatrix


@dataclass(eq=False)
class ImportMatrixVal(ImportMatrix):
    """Import directly the value from the object

    Attributes
    ----------
    value : ndarray or None
        The matrix to return
        Default: None
    """

    value: np.ndarray | None = None
    """The matrix to return"""

    # Inlined from Methods.Import.ImportMatrixVal.get_data
    def get_data(self):
        """Return the object's matrix

        Parameters
        ----------
        self : ImportMatrixVal
            An ImportMatrixVal object

        Returns
        -------
        matrix: ndarray
            The object's matrix

        """

        return self.edit_matrix(self.value)
