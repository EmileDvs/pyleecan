# Experimental dataclass generated from Generator/ClassesRef/Import/ImportGenMatrixSin.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ._error import PyleecanImportError as ImportError
from .import_gen_vect_sin import ImportGenVectSin
from .import_matrix import ImportMatrix


@dataclass(eq=False)
class ImportGenMatrixSin(ImportMatrix):
    """To generate a Sinus matrix

    Attributes
    ----------
    sin_list : [ImportGenVectSin] or None
        List of sinus vector to generate the matrix lines
        Default: []
    """

    sin_list: list[ImportGenVectSin] | None = field(default_factory=list)
    """List of sinus vector to generate the matrix lines"""

    # Inlined from Methods.Import.ImportGenMatrixSin.get_data
    def get_data(self):
        """Generate the sinus matrix

        Parameters
        ----------
        self : ImportGenMatrixSin
            An ImportGenMatrixSin object

        Returns
        -------
        matrix: ndarray
            The generated sinus matrix

        """

        if len(self.sin_list) == 0:
            raise self.GenSinEmptyError("ERROR: The sinus list is empty")

        N = self.sin_list[0].N
        is_T = self.sin_list[0].is_transpose

        for ii in range(1, len(self.sin_list)):
            if self.sin_list[ii].N != N:
                raise self.GenSinDimError(
                    "ERROR: Dimension mismatch between ImportGenVectSin 0 (N="
                    + str(N)
                    + ") and ImportGenVectSin "
                    + str(ii)
                    + " (N="
                    + str(self.sin_list[ii].N)
                    + ")"
                )
            if self.sin_list[ii].is_transpose != is_T:
                raise self.GenSinTransposeError(
                    "ERROR: is_transpose mismatch between ImportGenVectSin 0 ("
                    + str(is_T)
                    + ") and ImportGenVectSin "
                    + str(ii)
                    + " ("
                    + str(self.sin_list[ii].is_transpose)
                    + ")"
                )
        if is_T:  # Conctenate the columns
            matrix = np.column_stack([sin_obj.get_data() for sin_obj in self.sin_list])
        else:  # Concatenate the lines
            matrix = np.vstack([sin_obj.get_data() for sin_obj in self.sin_list])
        return self.edit_matrix(matrix)

    # Inlined from Methods.Import.ImportGenMatrixSin.init_vector
    def init_vector(self, f, A, Phi, N, Tf):
        """Create the sin_list according to the input list

        Parameters
        ----------
        self : ImportGenMatrixSin
            An ImportGenMatrixSin object
        f: list
            list of frequency for the sinus
        A: list
            list of amplitude for the sinus
        Phi: list
            list of phase for the sinus
        N: int
            Number of point (same for all the sinus)
        Tf: float
            End time (same for all the sinus)
        """

        if len(f) != len(A):
            raise self.InitSinMatDimError("ERROR: f and A have different dimensions")
        if len(f) != len(Phi):
            raise self.InitSinMatDimError("ERROR: f and Phi have different dimensions")

        self.sin_list = []
        for ii in range(len(f)):
            self.sin_list.append(
                ImportGenVectSin(f=f[ii], A=A[ii], Phi=Phi[ii], N=N, Tf=Tf)
            )

    class GenSinDimError(ImportError):
        """Raised when the ImportGenVectSin of the sin_list has different size (N)"""

    class GenSinEmptyError(ImportError):
        """Raised when the sin_list is empty"""

    class GenSinTransposeError(ImportError):
        """Raised when the ImportGenVectSin of the sin_list has different is_transpose"""

    class InitSinMatDimError(ImportError):
        """Raised when the init_vector is called with wrong arguments"""
