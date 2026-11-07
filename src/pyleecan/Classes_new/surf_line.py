# Experimental dataclass generated from Generator/ClassesRef/Geometry/SurfLine.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np
from matplotlib.patches import Polygon

from ..definitions import config_dict
from ..Functions.Geometry.comp_surface_num import comp_surface_num
from ..Functions.init_fig import init_fig
from .line import Line
from .surface import Surface


@dataclass(eq=False)
class SurfLine(Surface):
    """SurfLine defined by list of lines that delimit it, label and point reference.

    Attributes
    ----------
    line_list : [Line]
        List of Lines
        Default: []
    """

    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]
    line_list: list[Line] = []
    """List of Lines """

    # Inlined from Methods.Geometry.SurfLine.check
    # -*- coding: utf-8 -*-
    def check(self):
        """assert the Surface is correct

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

        Returns
        -------
        None
        """
        if self.line_list != []:
            for line in self.line_list:
                line.check()

    # Inlined from Methods.Geometry.SurfLine.comp_length
    # -*- coding: utf-8 -*-
    def comp_length(self):
        """Compute the length of the SurfLine object

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

        Returns
        -------
        length: float
            Length of the surface [m]


        """
        # check if the SurfLine is correct
        self.check()
        length = 0
        for line in self.line_list:
            length += line.comp_length()

        return length

    # Inlined from Methods.Geometry.SurfLine.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        middle_array = np.array([line.get_middle() for line in self.get_lines()])
        point_ref = np.sum(middle_array) / middle_array.size

        # Use another method if the point is not is the surface
        if not self.is_inside(Z=point_ref, if_online=False):
            middle_array_abs = abs(middle_array)
            # Find "min abs" middle
            mid_id = np.argmin(middle_array_abs)
            Zmid = middle_array[mid_id]
            H = np.max(middle_array_abs) - np.min(middle_array_abs)

            point_ref = (abs(Zmid) + H / 100) * np.exp(1j * np.angle(Zmid))

        if is_set:
            self.point_ref = point_ref
        return point_ref

    # Inlined from Methods.Geometry.SurfLine.comp_surface
    def comp_surface(self, Ndisc=200):
        """Compute the SurfLine surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object
        Ndisc : int
            Number of point to discretize the lines

        Returns
        -------
        surf: float
            The SurfLine surface [m**2]

        """

        # Discretize the surface with lots of points to compute the surface numerically
        point_list = self.discretize(Ndisc)

        return comp_surface_num(point_list)

    # Inlined from Methods.Geometry.SurfLine.discretize
    # -*-- coding: utf-8 -*
    def discretize(self, Npoint=-1):
        """Returns the discretize version of the SurfLine

        Parameters
        ----------
        self: SurfLine
            A SurfLine object
        Npoint : int
            Number of point on each line (Default value = -1 => use the line default discretization)

        Returns
        -------
        point_list : list
            List of complex coordinates
        """
        # check if the SurfLine is correct
        self.check()
        # getting lines that delimit the SurfLine
        lines = self.get_lines()
        if lines[0].get_begin() == lines[-1].get_end():
            closed = True
        else:
            closed = False

        point_list = []
        for line in lines:
            if Npoint == -1:
                point_list.extend(line.discretize())
            else:
                point_list.extend(line.discretize(Npoint))
            if line != lines[-1]:
                point_list.pop()
            else:
                if closed:  # if the SurfLine is closed
                    point_list.pop()
        return point_list

    # Inlined from Methods.Geometry.SurfLine.get_lines
    # -*- coding: utf-8 -*-
    def get_lines(self):
        """The list returned contains all the Line of the SurfLine

        Parameters
        ----------
        self : SurfLine
            A SurfLine object


        Returns
        -------
        line_list : list
            list of lines delimiting the surface

        """
        # Check if the surface is correct
        self.check()
        return self.line_list

    # Inlined from Methods.Geometry.SurfLine.get_patches
    def get_patches(
        self,
        color=None,
        edgecolor=None,
        is_edge_only=False,
        linestyle=None,
        hatch=None,
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
        hatch : str
            Set the hatching pattern: {'/', '\', '|', '-', '+', 'x', 'o', 'O', '.', '*'}

        Returns
        -------
        patch_list : list of matplotlib.patches.Polygon
            List of patches corresponding to the surface

        """

        # Set default color
        if edgecolor is None and not is_edge_only:
            edgecolor = self.PATCH_EDGE
        elif edgecolor is None and is_edge_only:
            edgecolor = self.PATCH_EDGE_ALPHA
        if is_edge_only:
            color = self.PATCH_COLOR_ALPHA
        if "--" in edgecolor:
            edgecolor = edgecolor.replace("-", "")
            linestyle = "--"

        # check if the SurfLine is correct
        self.check()
        line_list = self.get_lines()

        if len(line_list) == 0:
            return Polygon([], facecolor=color, edgecolor=edgecolor, hatch=hatch)

        Z_list = []
        # For each Line discretize
        for line in line_list:
            Z_list += list(line.discretize())

        # abscissa coordinate
        Zr_list = []
        # ordinate coordinate
        Zi_list = []

        for ii in range(len(Z_list)):
            Zr_list.append(Z_list[ii].real)
            Zi_list.append(Z_list[ii].imag)
        point_list = list(zip(Zr_list, Zi_list))
        return [
            Polygon(
                point_list,
                facecolor=color,
                edgecolor=edgecolor,
                linestyle=linestyle,
                hatch=hatch,
            )
        ]

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # Inlined from Methods.Geometry.SurfLine.plot_lines
    def plot_lines(self, fig=None, ax=None, is_show_fig=True):
        """Plot the SurfLine-Contour in a matplotlib fig
        (For plotting unclosed contour, for Polygon use plot method from Surface object)

        Parameters
        ----------
        self : SurfLine
            A SurfLine object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_show_fig : bool
            To call show at the end of the method

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

        for line in self.line_list:
            line.plot(fig=fig, ax=ax)

        # Axis Setup
        ax.axis("equal")

        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Geometry.SurfLine.rotate
    def rotate(self, angle):
        """Rotate the surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

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
        for line in self.line_list:
            line.rotate(angle)
        if self.point_ref is not None:
            self.point_ref = self.point_ref * np.exp(1j * angle)

    # Inlined from Methods.Geometry.SurfLine.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the lines

        Parameters
        ----------
        self : SurfLine
            A SurfLine Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        for line in self.line_list:
            line.scale(scale_factor)
        self.point_ref = self.point_ref * scale_factor

    # Inlined from Methods.Geometry.SurfLine.translate
    def translate(self, Zt):
        """Translate the surface

        Parameters
        ----------
        self : SurfLine
            A SurfLine object

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

        # Translation  of every line in the Surface
        for line in self.line_list:
            line.translate(Zt)

        if self.point_ref is not None:
            self.point_ref += Zt
