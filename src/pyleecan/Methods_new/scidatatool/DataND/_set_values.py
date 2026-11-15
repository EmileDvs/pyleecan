import numpy as np

from ....classes_common.check import check_dimensions, check_var


def _set_values(self, value):
    """setter of values"""
    if type(value) is int and value == -1:
        value = np.array([])
    elif type(value) is list:
        try:
            value = np.array(value)
        except:
            pass
    check_var("values", value, "ndarray")

    # Check dimensions
    if value is not None:
        value = np.squeeze(value)
    value = check_dimensions(value, self.axes)
    self._values = value
