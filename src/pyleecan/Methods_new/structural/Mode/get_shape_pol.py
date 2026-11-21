from ....Functions_new.SciDataTool.conversions import cart2pol_points as cart2pol
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


def get_shape_pol(self) -> np.ndarray:
    """Return the mode shape in cartesian coordinates.

    Parameters
    ----------
    self : Mode
        a Mode object

    Returns
    -------
    shape : ndarray
        ndarray of the shape (Nnodes*Ndof)
    """

    if self.shape_pol is not None and self.shape_pol.size != 0:
        return self.shape_pol
    else:
        shape_xyz = self.shape_xyz
        points = self.parent.mesh.get_points()
        return cart2pol(shape_xyz, points)
