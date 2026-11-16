from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_real_point(self, element_coordinate: np.ndarray, ref_pt: np.ndarray, nb_ref_pt: int = 1) -> np.ndarray | None:
    """Return the coordinates in the element of a point in the reference element.

    Parameters
    ----------
    self : RefTriangle3
         an RefElement object
    element_coordinate : ndarray
        coordinates of the element
    ref_pt : ndarray
        ref point(s)
    nb_ref_pt : int
        nb of ref points

    Returns
    -------
    real_points : ndarray
        points coordinate

    """
    # TODO
    return None
