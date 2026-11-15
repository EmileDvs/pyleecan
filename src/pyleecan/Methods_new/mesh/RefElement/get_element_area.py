# -*- coding: utf-8 -*-
import numpy as np


def get_element_area(self, element_coordinate: np.ndarray) -> np.ndarray:
    """Return the area of the elements.

    Parameters
    ----------
    self : RefElement
    element_coordinate : list or array
        the elements coordinates

    Returns
    -------
    area: array
        area of the elements
    """

    raise NotImplementedError(
        f"{type(self).__name__}.get_element_area is not implemented."
    )
