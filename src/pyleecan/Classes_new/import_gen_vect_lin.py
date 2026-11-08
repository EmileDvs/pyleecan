# Experimental dataclass generated from Generator/ClassesRef/Import/ImportGenVectLin.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._error import PyleecanImportError as ImportError
from .import_matrix import ImportMatrix


@dataclass(eq=False)
class ImportGenVectLin(ImportMatrix):
    """To generate a Linspace vector

    Attributes
    ----------
    start : float
        Begin point of the linspace
        Default: 0
    stop : float
        End point of the linspace
        Default: 1
    num : float
        Number of value in the linspace
        Default: 100
    endpoint : bool
        If True, stop is the last sample. Otherwise, it is not included
        Default: True
    """

    start: float = 0
    """Begin point of the linspace"""
    stop: float = 1
    """End point of the linspace"""
    num: float = 100
    """Number of value in the linspace"""
    endpoint: bool = True
    """If True, stop is the last sample. Otherwise, it is not included"""

    # Inlined from Methods.Import.ImportGenVectLin.check
    def check(self):
        """Check that the object is correctly set"""
        if self.start is None:
            raise ImportError("Start must not be None")
        if self.stop is None:
            raise ImportError("Stop must not be None")
        if self.num is None:
            raise ImportError("Num must not be None")
        if self.stop <= self.start:
            raise ImportError("You must have start < stop")
        if self.endpoint is None:
            self.endpoint = True

    # Inlined from Methods.Import.ImportGenVectLin.comp_step
    def comp_step(self):
        """Compute the Step between two points of the linspace"""

        self.check()
        data = self.get_data()
        return data[1] - data[0]

    # Inlined from Methods.Import.ImportGenVectLin.get_data
    def get_data(self):
        """Generate the linspace vector

        Parameters
        ----------
        self : ImportGenVectLin
            An ImportGenVectLin object

        Returns
        -------
        vect: ndarray
            The generated linspace vector

        """

        vect = np.linspace(
            start=self.start, stop=self.stop, num=int(self.num), endpoint=self.endpoint
        )

        return self.edit_matrix(vect)
