# Experimental pydantic model generated from Generator/ClassesRef/Import/ImportMatlab.csv
"""Generated experimental pydantic model; do not edit by hand."""

import os
from typing import ClassVar

import numpy as np
from scipy.io import loadmat

from ...classes_common.errors import PyleecanImportError as ImportError
from .import_matrix import ImportMatrix


class ImportMatlab(ImportMatrix):
    """Import the data from a mat file

    Attributes
    ----------
    file_path : str
        Path of the file to load
        Default: ""
    var_name : str
        Name of the variable to load
        Default: ""
    """

    file_path: str = ""
    """Path of the file to load"""
    var_name: str = ""
    """Name of the variable to load"""

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""

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
            raise self.MatFileError(
                "ERROR: The mat file doesn't exist " + self.file_path
            )

        data_dict = loadmat(self.file_path)
        if self.var_name not in data_dict:
            raise self.MatFileError(
                "ERROR: The variable "
                + self.var_name
                + " is not available in the file "
                + self.file_path
            )

        return np.squeeze(data_dict[self.var_name])

    class MatFileError(ImportError):
        """Raised when the file_path is wrong or the variable is missing"""
