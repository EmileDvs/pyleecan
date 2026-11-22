from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.mesh.mesh_solution import MeshSolution


def plot_animated(self, i: int, meshsol: MeshSolution | None = None) -> None:
    """Return the pyvista mesh object.

    Parameters
    ----------
    self : Mode
        a Mode object
    i : int
        index of the mode to plot
    meshsol : MeshSolution, optional
        Mesh solution holding the mode (default: the parent)

    Returns
    -------
    mesh : pyvista.core.pointset.StructuredGrid
        a pyvista StructuredGrid object
    """
    meshsol = container_or_parent(self, meshsol, "meshsol")

    radial_shape = self.get_shape_pol(meshsol=meshsol)[:, 0]
    shape_xyz = self.get_shape_xyz(meshsol=meshsol)
    clim = [np.min(radial_shape), np.max(radial_shape)]
    meshsol.mesh.plot_deformation_animated(
        shape_xyz,
        radial_shape,
        factor=0.05,
        field_name="Radial displacement",
        clim=clim,
    )
