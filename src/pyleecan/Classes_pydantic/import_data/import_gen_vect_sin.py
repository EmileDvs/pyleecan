# Experimental pydantic model generated from Generator/ClassesRef/Import/ImportGenVectSin.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

import numpy as np
from pydantic import Field

from .import_matrix import ImportMatrix


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

    f: float = Field(default=100, ge=0, json_schema_extra={"unit": "Hz"})
    """Frequency of the sinus to generate"""
    A: float = 1
    """Amplitude of the sinus to generate"""
    Phi: float = Field(default=0, ge=-6.29, le=6.29)
    """Phase of the sinus to generate"""
    N: int = Field(default=1024, ge=0)
    """Length of the vector to generate"""
    Tf: float = Field(default=1, ge=0, json_schema_extra={"unit": "s"})
    """End time of the sinus generation"""

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Import.ImportGenVectSin.get_data
    def get_data(self) -> np.ndarray:
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
