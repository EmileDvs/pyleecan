from ....classes_common.parents import container_or_parent
from ....Functions_new.SciDataTool.conversions import pol2cart_points as pol2cart
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from ....Classes_new.mesh.mesh_solution import MeshSolution


def get_shape_xyz(self, meshsol: MeshSolution | None = None) -> np.ndarray:
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

    if self.shape_xyz is not None and self.shape_xyz.size != 0:
        return self.shape_xyz
    else:
        shape_pol = self.shape_pol
        points = meshsol.mesh.get_points()
        return pol2cart(shape_pol, points)
