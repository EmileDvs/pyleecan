# Experimental dataclass generated from Generator/ClassesRef/Import/ImportMatrix.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .import_ import Import


@dataclass(eq=False)
class ImportMatrix(Import):
    """Abstract class to Import/Generate 1D or D matrix

    Attributes
    ----------
    is_transpose : bool
        True to transpose the Imported/Generated matrix
        Default: False
    """

    is_transpose: bool = False
    """True to transpose the Imported/Generated matrix"""

    # Inlined from Methods.Import.ImportMatrix.edit_matrix
    def edit_matrix(self, matrix):
        """To apply transformation on the matrix

        Parameters
        ----------
        self : ImportMatrix
            An ImportMatrix object
        matrix: ndarray
            The matrix to edit

        Returns
        -------
        matrix: ndarray
            The edited matrix

        """

        if self.is_transpose:
            return np.transpose(matrix)
        return matrix
