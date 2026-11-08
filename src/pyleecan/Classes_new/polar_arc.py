# Experimental dataclass generated from Generator/ClassesRef/Geometry/PolarArc.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np
from matplotlib.patches import Polygon

from ..definitions import config_dict
from .arc_1 import Arc1
from .segment import Segment
from .surface import Surface


@dataclass(eq=False)
class PolarArc(Surface):
    """PolarArc defined by  the center of object(point_ref), the label, the angle and the height

    Attributes
    ----------
    angle : float
        Polar angle
        Default: 1; Minimum: 0
    height : float
        The Heigth of the PolarAngle
        Unit: m; Default: 1; Minimum: 0
    """

    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]
    angle: float = 1
    """Polar angle"""
    height: float = 1
    """The Heigth of the PolarAngle"""

    # Inlined from Methods.Geometry.PolarArc.check
    def check(self):
        """check if the PolarArc object is correct

        Parameters
        ----------
        self : PolarArc
            a PolarArc Object

        Returns
        -------
        None

        Raises
        ------
        AnglePolarArcError
            The angle of a polar arc must be different to 0

        """
        if self.angle == 0:
            raise self.AnglePolarArcError(
                "The angle of a polar arc must be different to 0"
            )

    # Inlined from Methods.Geometry.PolarArc.comp_length
    # -*-- coding: utf-8 -*
    def comp_length(self):
        """Returns the length of the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc object


        Returns
        -------
        length : float
            length of the PolarArc [m]
        """
        # check if the PolarArc is correct
        self.check()

        lines = self.get_lines()
        length = 0
        for line in lines:
            length += line.comp_length()
        return length

    # Inlined from Methods.Geometry.PolarArc.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : PolarArc
            A PolarArc object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        point_ref = self.point_ref
        if is_set:
            self.point_ref = point_ref
        return point_ref

    # Inlined from Methods.Geometry.PolarArc.comp_surface
    def comp_surface(self):
        """Compute the PolarArc surface

        Parameters
        ----------
        self : PolarArc
            A PolarArc object

        Returns
        -------
        surf: float
            The PolarArc surface [m**2]

        """

        Rint = abs(self.point_ref) - self.height / 2
        Rext = Rint + self.height

        return (np.pi * Rext**2 - np.pi * Rint**2) * (self.angle / (2 * np.pi))

    # Inlined from Methods.Geometry.PolarArc.discretize
    # -*-- coding: utf-8 -*
    def discretize(self, nb_point):
        """Returns the discretize version of the PolarArc

        Parameters
        ----------
        nb_point : int
            number of points wanted per line

        Returns
        -------
        point_list : list
            List of complex coordinate of the points

        """
        # check if the PolarArc is correct
        self.check()

        if not isinstance(nb_point, int):
            raise self.NbPointPolarArcError(
                "Discretize : the nb_point must be an integer"
            )
        if nb_point < 0:
            raise self.NbPointPolarArcError("Discretize: nb_point must be >= 0")

        # getting lines that delimit the PolarArc
        lines = self.get_lines()
        point_list = []
        for line in lines:
            point_list.extend(line.discretize(nb_point))
            # The begin of the next line is the end of the current one
            point_list.pop()
        return point_list

    # Inlined from Methods.Geometry.PolarArc.get_lines
    def get_lines(self):
        """return the list of lines that delimits the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc object

        Returns
        -------
        line_list: list
            List of line need to draw the slot (2 Segment + 2 Arc1)
        """
        # check if the PolarArc is correct
        self.check()

        Z_ref = self.point_ref
        center = Z_ref * np.exp(-1j * np.angle(Z_ref))
        H = self.height
        A = self.angle
        # the points of the PolarArc
        Z2 = (center - (H / 2)) * np.exp(1j * (-(A / 2))) * np.exp(1j * np.angle(Z_ref))
        Z3 = (center + (H / 2)) * np.exp(1j * (-(A / 2))) * np.exp(1j * np.angle(Z_ref))
        Z4 = (center + (H / 2)) * np.exp(1j * (A / 2)) * np.exp(1j * np.angle(Z_ref))
        Z1 = (center - (H / 2)) * np.exp(1j * (A / 2)) * np.exp(1j * np.angle(Z_ref))

        # Lines that delimit the PolarArc
        line1 = Arc1(Z1, Z2, -abs(Z1), is_trigo_direction=False)
        line2 = Segment(Z2, Z3)
        line3 = Arc1(Z3, Z4, abs(Z3))
        line4 = Segment(Z4, Z1)

        return [line1, line2, line3, line4]

    # Inlined from Methods.Geometry.PolarArc.get_patches
    def get_patches(
        self, color=None, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the PolarArc Patch to be display in matplotlib
        Parameters
        ----------
        self : PolarArc
            a PolarArc object
        color :
            The color of the patch (Default value = PATCH_COLOR)
        edgecolor :
            The color of the edgecolor (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

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

        # check if the PolarArc is correct
        self.check()

        line_list = self.get_lines()
        Z_list = []
        # For each  Line discretize
        for line in line_list:
            Z_list.extend(line.discretize())

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
                point_list, facecolor=color, edgecolor=edgecolor, linestyle=linestyle
            )
        ]

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # Inlined from Methods.Geometry.PolarArc.rotate
    def rotate(self, angle):
        """Do the rotation of the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc
        angle : float
            the angle for rotation [rad]

        Returns
        -------
        None
        """
        if angle == 0:
            return  # Nothing to do
        # check if the PolarArc is correct
        self.check()
        self.point_ref = self.point_ref * np.exp(1j * angle)

    # Inlined from Methods.Geometry.PolarArc.translate
    def translate(self, Zt):
        """Do the translation of the PolarArc

        Parameters
        ----------
        self : PolarArc
            a PolarArc object

        Zt : complex
            Complex value for translation

        Returns
        -------
        None
        """
        if Zt == 0:
            return  # Nothing to do
        # check if the PolarArc is correct
        self.check()
        self.point_ref += Zt

    class AnglePolarArcError(Exception):
        """ """

    class NbPointPolarArcError(Exception):
        """ """
