# Experimental dataclass generated from Generator/ClassesRef/Simulation/Mode.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

import numpy as np

from ...classes_common.parents import container_or_parent
from ...Functions_new.SciDataTool.conversions import cart2pol_points as cart2pol
from ...Functions_new.SciDataTool.conversions import pol2cart_points as pol2cart
from ..mesh.solution_mat import SolutionMat

if TYPE_CHECKING:
    from ..mesh.mesh_solution import MeshSolution


@dataclass(eq=False)
class Mode(SolutionMat):
    """Structural module: Mode object

    Attributes
    ----------
    nat_freq : float or None
        Natural frequency of the mode
        Unit: Hz; Default: None
    order_circ : int or None
        Circumferential order
        Default: None; Minimum: 0
    order_long : int or None
        Longitudinal order
        Default: None; Minimum: 0
    """

    nat_freq: float | None = field(default=None, metadata={"unit": "Hz"})
    """Natural frequency of the mode"""
    order_circ: int | None = field(default=None, metadata={"min": 0})
    """Circumferential order"""
    order_long: int | None = field(default=None, metadata={"min": 0})
    """Longitudinal order"""

    _package: ClassVar[str] = "Simulation"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Simulation.Mode.get_shape_pol
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

    # Inlined from Methods.Simulation.Mode.get_shape_xyz
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

    # Inlined from Methods.Simulation.Mode.plot
    def plot(self, i: int, meshsol: MeshSolution | None = None) -> None:
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
        clim = [np.min(radial_shape), np.max(radial_shape)]
        meshsol.mesh.plot_contour(
            radial_shape, field_name="Radial displacement", clim=clim
        )

    # Inlined from Methods.Simulation.Mode.plot_animated
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
