# Experimental dataclass generated from Generator/ClassesRef/Geometry/Trapeze.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np
from matplotlib.patches import Polygon

from ..definitions import config_dict
from .segment import Segment
from .surface import Surface


@dataclass(eq=False)
class Trapeze(Surface):
    """Trapeze defined by  the center of symmetry(point_ref), the label, the polar angle, the height and the big and small weight

    Attributes
    ----------
    height : float
        the height of the Trapeze
        Unit: m; Default: 1; Minimum: 0
    W2 : float
        the big base of Trapeze
        Unit: m; Default: 1; Minimum: 0
    W1 : float
        the small base of the Trapeze
        Unit: m; Default: 1; Minimum: 0
    """

    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]
    height: float = 1
    """the height of the Trapeze"""
    W2: float = 1
    """the big base of Trapeze"""
    W1: float = 1
    """the small base of the Trapeze"""

    # Inlined from Methods.Geometry.Trapeze.check
    def check(self):
        """Check if the Trapeze object is correct

        Parameters
        ----------
        self : Trapeze
            a Trapeze Object


        Returns
        -------
        None

        Raises
        ------
        TrapezeError
            the W1 base of Trapeze must be greater than 0
        TrapezeError
            the W2 base of Trapeze must be greater than 0

        """
        if self.W1 <= 0:
            raise self.TrapezeError("the W1 base of Trapeze must be greater than 0")

        if self.W2 <= 0:
            raise self.TrapezeError("the W2 base of Trapeze must be greater than 0")

    # Inlined from Methods.Geometry.Trapeze.comp_length
    # -*-- coding: utf-8 -*
    def comp_length(self):
        """Returns the length of the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object


        Returns
        -------
        length: float
            Length of the surface [m]

        """
        # check if the Trapeze is correct
        self.check()
        lines = self.get_lines()
        length = 0
        for line in lines:
            length += line.comp_length()
        return length

    # Inlined from Methods.Geometry.Trapeze.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : Trapeze
            A Trapeze object
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

    # Inlined from Methods.Geometry.Trapeze.comp_surface
    def comp_surface(self):
        """Compute the Trapeze surface

        Parameters
        ----------
        self : Trapeze
            A Trapeze object

        Returns
        -------
        surf: float
            The Trapeze surface [m**2]

        """

        return self.height * (self.W2 + self.W1) / 2

    # Inlined from Methods.Geometry.Trapeze.discretize
    # -*-- coding: utf-8 -*
    def discretize(self):
        """It returns the discretize version of the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object

        Returns
        -------
        point_list : list
            list of complex coordinate of the points
        """

        # check if the Trapeze is correct
        self.check()
        # getting lines that delimit the Trapeze
        lines = self.get_lines()
        point_list = []
        for line in lines:
            point_list.extend(line.discretize())
            point_list.pop()
        return point_list

    # Inlined from Methods.Geometry.Trapeze.get_lines
    def get_lines(self):
        """Returns the Lines that delimit the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object


        Returns
        -------
        line_list : list
            list of 4 segments

        """
        # Check if the Trapeze is correct
        self.check()
        Z_ref = self.point_ref
        H = self.height
        W1 = self.W1
        W2 = self.W2

        # The 4 points of the Trapeze object
        Z1 = (complex(-H / 2, W1 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref
        Z2 = (complex(-H / 2, -W1 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref
        Z3 = (complex(H / 2, -W2 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref
        Z4 = (complex(H / 2, W2 / 2) * np.exp(1j * (np.angle(Z_ref)))) + Z_ref

        # The lines that delimit the Trapeze
        line1 = Segment(Z1, Z2)
        line2 = Segment(Z2, Z3)
        line3 = Segment(Z3, Z4)
        line4 = Segment(Z4, Z1)

        return [line1, line2, line3, line4]

    # Inlined from Methods.Geometry.Trapeze.get_patches
    def get_patches(
        self, color=None, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the Trapeze Patch to be display in matplotlib

        Parameters
        ----------
        self : Trapeze
            a Trapeze object

        color :
            the color of the patch (Default value = PATCH_COLOR)
        edgecolor :
            the color of the patch's edges (Default value = PATCH_EDGE)
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

        # check if the Trapeze is correct*
        self.check()

        line_list = self.get_lines()
        Z_list = []
        # For each Line discretize
        for line in line_list:
            Z_list.extend(list(line.discretize()))

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
                closed=True,
                facecolor=color,
                edgecolor=edgecolor,
                linestyle=linestyle,
            )
        ]

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # Inlined from Methods.Geometry.Trapeze.rotate
    def rotate(self, angle):
        """Rotate the surface

        Parameters
        ----------
        self : Trapeze
            a Trapeze Object

        angle : float
            angle for rotation [rad]


        Returns
        -------
        None
        """
        if angle == 0:
            return  # Nothing to do
        # check if the Trapeze is correct
        self.check()
        self.point_ref = self.point_ref * np.exp(1j * angle)

    # Inlined from Methods.Geometry.Trapeze.translate
    def translate(self, Zt):
        """Translate the Trapeze

        Parameters
        ----------
        self : Trapeze
            a Trapeze object

        Zt : complex
            Complex value for translation

        Returns
        -------
        None
        """
        if Zt == 0:
            return  # Nothing to do
        # check if the Trapeze is correct
        self.check()
        self.point_ref += Zt

    class TrapezeError(Exception):
        """ """
