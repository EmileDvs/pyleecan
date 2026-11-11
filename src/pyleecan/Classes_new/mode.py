# Experimental dataclass generated from Generator/ClassesRef/Simulation/Mode.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions_new.Structural.conversions import cart2pol, pol2cart
from .solution_mat import SolutionMat


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

    nat_freq: float | None = None
    """Natural frequency of the mode"""
    order_circ: int | None = None
    """Circumferential order"""
    order_long: int | None = None
    """Longitudinal order"""

    # Inlined from Methods.Simulation.Mode.get_shape_pol
    def get_shape_pol(self):
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

    # Inlined from Methods.Simulation.Mode.get_shape_xyz
    def get_shape_xyz(self):
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

        if self.shape_xyz is not None and self.shape_xyz.size != 0:
            return self.shape_xyz
        else:
            shape_pol = self.shape_pol
            points = self.parent.mesh.get_points()
            return pol2cart(shape_pol, points)

    # Inlined from Methods.Simulation.Mode.plot
    def plot(self, i):
        """Return the pyvista mesh object.

        Parameters
        ----------
        self : Mode
            a Mode object
        i : int
            index of the mode to plot

        Returns
        -------
        mesh : pyvista.core.pointset.StructuredGrid
            a pyvista StructuredGrid object
        """

        radial_shape = self.get_shape_pol()[:, 0]
        clim = [np.min(radial_shape), np.max(radial_shape)]
        self.parent.mesh.plot_contour(
            radial_shape, field_name="Radial displacement", clim=clim
        )

    # Inlined from Methods.Simulation.Mode.plot_animated
    def plot_animated(self, i):
        """Return the pyvista mesh object.

        Parameters
        ----------
        self : Mode
            a Mode object
        i : int
            index of the mode to plot

        Returns
        -------
        mesh : pyvista.core.pointset.StructuredGrid
            a pyvista StructuredGrid object
        """

        radial_shape = self.get_shape_pol()[:, 0]
        shape_xyz = self.get_shape_xyz()
        clim = [np.min(radial_shape), np.max(radial_shape)]
        self.parent.mesh.plot_deformation_animated(
            shape_xyz,
            radial_shape,
            factor=0.05,
            field_name="Radial displacement",
            clim=clim,
        )
