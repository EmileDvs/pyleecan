from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def is_inside(self, element_coordinate: np.ndarray, point: np.ndarray, normal_t: np.ndarray | None = None) -> bool | None:
    """Check if a point is inside the element defined by its coordinates.

    Parameters
    ----------
    self : RefTriangle3
        an RefTriangle3 object
    element_coordinate : ndarray
        coordinates of the element
    point : ndarray
        coordinates of the checked point
    normal_t : ndarray
        (optional) element normal vector

    Returns
    -------
    is_inside: bool
        true if the point is inside the element

    """
    # TODO
    return None
