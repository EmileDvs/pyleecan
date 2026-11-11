# Experimental dataclass generated from Generator/ClassesRef/Geometry/SurfRing.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ..definitions import config_dict
from ..Functions_new.init_fig import init_fig
from ._import import import_class
from .surface import Surface


@dataclass(eq=False)
class SurfRing(Surface):
    """SurfRing is a surface between two closed surfaces (lamination surfaces for instance)

    Attributes
    ----------
    out_surf : Surface or None
        Outter surface
        Default: Surface()
    in_surf : Surface or None
        Inner surface
        Default: Surface()
    """

    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]
    out_surf: Surface | None = field(
        default_factory=lambda: import_class("Surface")(),
        metadata={"default_class": "Surface"},
    )
    """Outter surface"""
    in_surf: Surface | None = field(
        default_factory=lambda: import_class("Surface")(),
        metadata={"default_class": "Surface"},
    )
    """Inner surface"""

    # Inlined from Methods.Geometry.SurfRing.check
    # -*- coding: utf-8 -*-
    def check(self):
        """assert the Surface is correct

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Returns
        -------
        None
        """
        self.out_surf.check()
        self.in_surf.check()

    # Inlined from Methods.Geometry.SurfRing.comp_length
    # -*- coding: utf-8 -*-
    def comp_length(self):
        """Compute the length of the SurfRing object (length of both surfaces)

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Returns
        -------
        length: float
            Length of the surface [m]


        """
        return self.out_surf.comp_length() + self.in_surf.comp_length()

    # Inlined from Methods.Geometry.SurfRing.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        point_list = []
        out_lines = self.out_surf.get_lines()
        in_lines = self.in_surf.get_lines()
        # Compute the ref point as the barycenter of half the lines
        for line in out_lines[: len(out_lines) / 2]:
            point_list.append(line.get_middle())
        for line in in_lines[: len(in_lines) / 2]:
            point_list.append(line.get_middle())
        point_ref = np.sum(np.array(point_list)) / len(point_list)

        if is_set:
            self.point_ref = point_ref
        return point_ref

    # Inlined from Methods.Geometry.SurfRing.comp_surface
    def comp_surface(self):
        """Compute the SurfRing surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Returns
        -------
        surf: float
            The SurfRing surface [m**2]

        """

        Sout = self.out_surf.comp_surface()
        Sin = self.in_surf.comp_surface()

        assert Sout > Sin

        return Sout - Sin

    # Inlined from Methods.Geometry.SurfRing.discretize
    # -*-- coding: utf-8 -*
    def discretize(self, Npoint=-1):
        """Returns the discretize version of the SurfRing

        Parameters
        ----------
        self: SurfRing
            A SurfRing object
        Npoint : int
            Number of point on each line (Default value = -1 => use the line default discretization)

        Returns
        -------
        point_list : list
            List of complex coordinates
        """
        # check if the SurfRing is correct
        self.check()
        # getting lines that delimit the SurfLine

        point_list = self.out_surf.discretize(Npoint=Npoint)
        point_list.extend(self.in_surf.discretize(Npoint=Npoint))
        return point_list

    # Inlined from Methods.Geometry.SurfRing.get_lines
    # -*- coding: utf-8 -*-
    def get_lines(self):
        """The list returned contains all the Line of the SurRing

        Parameters
        ----------
        self : SurfRing
            A SurfRing object


        Returns
        -------
        line_list : list
            list of lines delimiting the surface

        """
        line_list = []
        line_list.extend(self.out_surf.get_lines())
        line_list.extend(self.in_surf.get_lines())
        return line_list

    # Inlined from Methods.Geometry.SurfRing.get_patches
    def get_patches(
        self, color=None, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the PolarArc Patch to be display in matplotlib

        Parameters
        ----------
        self : SurfLine
            a SurfLine object
        color :
            the color of the patch (Default value = PATCH_COLOR)
        edgecolor :
            the edge color of the patch (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

        Returns
        -------
        patch_list : list of matplotlib.patches.Polygon
            List of patches corresponding to the surface

        """
        patch_list = self.out_surf.get_patches(
            color=color,
            edgecolor=edgecolor,
            is_edge_only=is_edge_only,
            linestyle=linestyle,
        )
        # No color for inner surface
        patch_list.extend(
            self.in_surf.get_patches(
                is_edge_only=is_edge_only, edgecolor=edgecolor, linestyle=linestyle
            )
        )
        return patch_list

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # Inlined from Methods.Geometry.SurfRing.plot_lines
    def plot_lines(self, fig=None, ax=None):
        """Plot the SurfRing-Contour in a matplotlib fig
        (For plotting unclosed contour, for Polygon use plot method from Surface object)

        Parameters
        ----------
        self : SurfRing
            A SurfRing object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
        ax.set_xlabel("[m]")
        ax.set_ylabel("[m]")

        points = self.out_surf.discretize(10)
        for idx in range(len(points) - 1):
            z1 = points[idx]
            z2 = points[idx + 1]
            x1 = np.real(z1)
            y1 = np.imag(z1)
            x2 = np.real(z2)
            y2 = np.imag(z2)
            ax.plot([x1, x2], [y1, y2], "k")

        points = self.in_surf.discretize(10)
        for idx in range(len(points) - 1):
            z1 = points[idx]
            z2 = points[idx + 1]
            x1 = np.real(z1)
            y1 = np.imag(z1)
            x2 = np.real(z2)
            y2 = np.imag(z2)
            ax.plot([x1, x2], [y1, y2], "k")

        # Axis Setup
        ax.axis("equal")

        fig.show()
        return fig, ax

    # Inlined from Methods.Geometry.SurfRing.rotate
    def rotate(self, angle):
        """Rotate the surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None
        """
        if angle == 0:
            return  # Nothing to do
        # Check if the Surface is correct
        self.check()
        # rotation of every line in the Surface
        self.out_surf.rotate(angle)
        self.in_surf.rotate(angle)
        if self.point_ref is not None:
            self.point_ref = self.point_ref * np.exp(1j * angle)

    # Inlined from Methods.Geometry.SurfRing.translate
    def translate(self, Zt):
        """Translate the surface

        Parameters
        ----------
        self : SurfRing
            A SurfRing object

        Zt : complex
            Complex value for translation

        Returns
        -------
        None
        """
        if Zt == 0:
            return  # Nothing to do
        # Check if the Surface is correct
        self.check()

        self.out_surf.translate(Zt)
        self.in_surf.translate(Zt)

        if self.point_ref is not None:
            self.point_ref += Zt
