from ....classes_common.parents import container_or_parent
from ....Functions_new.SciDataTool.conversions import cart2pol_points as cart2pol
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from ....Classes_new.mesh.mesh_solution import MeshSolution


def get_shape_pol(self, meshsol: MeshSolution | None = None) -> np.ndarray:
    """Return the mode shape in cartesian coordinates.

    Parameters
    ----------
    self : Mode
        a Mode object
    meshsol : MeshSolution, optional
        Mesh solution holding the mode (default: the parent)

    Returns
    -------
    shape : ndarray
        ndarray of the shape (Nnodes*Ndof)
    """
    meshsol = container_or_parent(self, meshsol, "meshsol")

    if self.shape_pol is not None and self.shape_pol.size != 0:
        return self.shape_pol
    else:
        shape_xyz = self.shape_xyz
        points = meshsol.mesh.get_points()
        return cart2pol(shape_xyz, points)
