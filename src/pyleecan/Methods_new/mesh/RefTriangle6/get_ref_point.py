from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_ref_point(self, element_coordinate: np.ndarray, point: np.ndarray) -> np.ndarray | None:
    """Return the coordinate of the equivalent point in the ref element

    Parameters
    ----------
    self : RefTriangle3
        a RefTriangle3 object
    element_coordinate : ndarray
        coordinates of the element
    point : ndarray
        coordinates of a point

        Returns
    -------
    pt1_ref : ndarray
        coordinates of the ref point
    """
    # TODO
    return None
