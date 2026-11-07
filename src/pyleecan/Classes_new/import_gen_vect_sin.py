# Experimental dataclass generated from Generator/ClassesRef/Import/ImportGenVectSin.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .import_matrix import ImportMatrix


@dataclass(eq=False)
class ImportGenVectSin(ImportMatrix):
    """To generate a Sinus vector

    Attributes
    ----------
    f : float
        Frequency of the sinus to generate
        Unit: Hz; Default: 100; Minimum: 0
    A : float
        Amplitude of the sinus to generate
        Default: 1
    Phi : float
        Phase of the sinus to generate
        Default: 0; Minimum: -6.29; Maximum: 6.29
    N : int
        Length of the vector to generate
        Default: 1024; Minimum: 0
    Tf : float
        End time of the sinus generation
        Unit: s; Default: 1; Minimum: 0
    """

    f: float = 100
    """Frequency of the sinus to generate"""
    A: float = 1
    """Amplitude of the sinus to generate"""
    Phi: float = 0
    """Phase of the sinus to generate"""
    N: int = 1024
    """Length of the vector to generate"""
    Tf: float = 1
    """End time of the sinus generation"""

    # Inlined from Methods.Import.ImportGenVectSin.get_data
    def get_data(self):
        """Generate the sinus vector

        Parameters
        ----------
        self : ImportGenVectSin
            An ImportGenVectSin object

        Returns
        -------
        vect: ndarray
            The generated sinus vector

        """

        time = np.linspace(start=0, stop=self.Tf, num=self.N, endpoint=False)

        vect = self.A * np.sin(2 * np.pi * self.f * time + self.Phi)
        return self.edit_matrix(vect)
