from scipy.io import loadmat
from . import MatFileError
import os
import numpy as np


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
