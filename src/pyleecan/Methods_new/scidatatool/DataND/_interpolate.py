from ....Functions_new.SciDataTool.interpolations import get_interpolation, get_interpolation_step
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def _interpolate(self, values: np.ndarray, axes_list: list) -> np.ndarray:
    """Returns the values of the field interpolated over the axes values.
    Parameters
    ----------
    self: Data
        a Data object
    values: ndarray
        array of the field
    axes_list: list
        a list of RequestedAxis objects
    Returns
    -------
    values: ndarray
        values of the field
    """

    # Interpolate over axis values
    for axis_requested in axes_list:
        if axis_requested.input_data is not None:
            if axis_requested.is_step:
                values = get_interpolation_step(
                    values,
                    axis_requested.values,
                    axis_requested.input_data,
                    axis_requested.index,
                )
            else:
                values = get_interpolation(
                    values,
                    axis_requested.values,
                    axis_requested.input_data,
                    axis_requested.index,
                )
            # Store new axis data into axis_requested.values
            axis_requested.values = axis_requested.input_data
    return values
