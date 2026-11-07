# Experimental dataclass generated from Generator/ClassesRef/Import/ImportMatlab.csv
"""Generated experimental dataclass; do not edit by hand."""

import os
from dataclasses import dataclass

import numpy as np
from scipy.io import loadmat

from .import_matrix import ImportMatrix


@dataclass(eq=False)
class ImportMatlab(ImportMatrix):
    """Import the data from a mat file

    Attributes
    ----------
    file_path : str or None
        Path of the file to load
        Default: None
    var_name : str or None
        Name of the variable to load
        Default: None
    """

    file_path: str | None = None
    """Path of the file to load"""
    var_name: str | None = None
    """Name of the variable to load"""

    # Inlined from Methods.Import.ImportMatlab.get_data
    def get_data(self):
        """Return the value from the .mat file

        Parameters
        ----------
        self : ImportMatlab
            An ImportMatlab object

        Returns
        -------
        value : ?
            Loaded data
        """

        if self.file_path[-4:] != ".mat":
            self.file_path += ".mat"
        if not os.path.isfile(self.file_path):
            raise MatFileError("ERROR: The mat file doesn't exist " + self.file_path)

        data_dict = loadmat(self.file_path)
        if self.var_name not in data_dict:
            raise MatFileError(
                "ERROR: The variable "
                + self.var_name
                + " is not available in the file "
                + self.file_path
            )

        return np.squeeze(data_dict[self.var_name])

    class ImportError(Exception):
        """Raised when the data import or generation is not possible"""

    class MatFileError(ImportError):
        """Raised when the file_path is wrong or the variable is missing"""


ImportError = ImportMatlab.ImportError
MatFileError = ImportMatlab.MatFileError
