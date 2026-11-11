# Experimental dataclass generated from Generator/ClassesRef/Geometry/Circle.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from matplotlib.patches import Circle

from ..definitions import config_dict
from .arc_3 import Arc3
from .surface import Surface


@dataclass(eq=False)
class Circle(Surface):
    """Circle define by  the center of circle(point_ref), the label and the radius

    Attributes
    ----------
    radius : float
        Radius of the circle
        Default: 1; Minimum: 0
    center : complex
        center of the Circle
        Default: 0
    prop_dict : dict or None
        Property dict to apply on the lines
        Default: {}
    """

    PATCH_EDGE = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE"]
    PATCH_COLOR = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR"]
    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    PATCH_EDGE_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_EDGE_ALPHA"]
    radius: float = 1
    """Radius of the circle"""
    center: complex = 0
    """center of the Circle"""
    prop_dict: dict[str, Any] | None = field(default_factory=dict)
    """Property dict to apply on the lines"""

    # Inlined from Methods.Geometry.Circle.check
    def check(self):
        """assert the Circle is correct (the radius > 0)

        Parameters
        ----------
        self : Circle
            A Circle object

        Returns
        -------
        None

        Raises
        ------
        RadiusCircleError
            The radius of a circle must be >=  0

        """
        if self.radius < 0:
            raise self.RadiusCircleError("The radius of a circle must be >= 0")

    # Inlined from Methods.Geometry.Circle.comp_length
    def comp_length(self):
        """Compute the length of the circle

        Parameters
        ----------
        self : Circle
            A Circle object

        Returns
        -------
        length : float
            the length of the circle [m]

        """
        # Check if the circle is correct
        self.check()

        length = self.radius * 2 * np.pi

        return length

    # Inlined from Methods.Geometry.Circle.comp_point_ref
    def comp_point_ref(self, is_set=False):
        """Compute the point ref of the Surface

        Parameters
        ----------
        self : Circle
            A Circle object
        is_set: bool
            True to update the point_ref property

        Returns
        -------
        point_ref : complex
            the reference point of the surface
        """

        point_ref = self.center
        if is_set:
            self.point_ref = point_ref
        return point_ref

    # Inlined from Methods.Geometry.Circle.comp_surface
    def comp_surface(self):
        """Compute the circle surface

        Parameters
        ----------
        self : Circle
            A Circle object

        Returns
        -------
        surf: float
            The circle surface [m**2]

        """

        return np.pi * self.radius**2

    # Inlined from Methods.Geometry.Circle.discretize
    def discretize(self):
        """Return the discretize version of the Circle.

        Parameters
        ----------
        self : Circle
            A Circle Object

        nb_point : int
            Number of point on the circle

        Returns
        -------
        point_list : list
            List of complex coordinate of the points

        """

        # check if the Circle is correct
        self.check()

        # getting Arc which delimit the Circle
        lines = self.get_lines()
        point_list = []
        for line in lines:
            point_list.extend(line.discretize())
            point_list.pop()
        return point_list

    # Inlined from Methods.Geometry.Circle.get_lines
    def get_lines(self):
        """Get the lines needed to draw the surface (2 Arc3)

        Parameters
        ----------
        self : Circle
            A circle Object

        Returns
        -------
        line_list: list
            Two arcs to draw the circle

        """
        # check if the circle is correct
        self.check()
        begin = self.center + self.radius
        end = self.center - self.radius
        # first half-circle
        line1 = Arc3(
            begin=begin, end=end, is_trigo_direction=True, prop_dict=self.prop_dict
        )
        # second half-circle
        line2 = Arc3(
            begin=end, end=begin, is_trigo_direction=True, prop_dict=self.prop_dict
        )
        return [line1, line2]

    # Inlined from Methods.Geometry.Circle.get_patches
    def get_patches(
        self, color=None, edgecolor=None, is_edge_only=False, linestyle=None
    ):
        """Returns the Circle Patch to be display in matplotlib

        Parameters
        ----------
        self : Circle
            a Circle object
        color :
            the color of the Patch (Default value = PATCH_COLOR)
        edgecolor :
            edgecolor of the Patch (Default value = PATCH_EDGE)
        is_edge_only: bool
            To set the transparancy of the face color to 0 and 1 for the edge color
        linestyle : str
            Line style of the edge {'-', '--', '-.', ':', '', (offset, on-off-seq), ...}

        Returns
        -------
        patch_list : list of matplotlib.patches.Circle
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

        # check if the Circle is correct
        self.check()
        # the coordinates of the center of the circle
        Zr = self.center.real
        Zi = self.center.imag

        return [
            Circle(
                xy=(Zr, Zi),
                radius=self.radius,
                facecolor=color,
                edgecolor=edgecolor,
                linestyle=linestyle,
            )
        ]

    get_patches.__defaults__ = (
        get_patches.__defaults__[:0] + (PATCH_COLOR,) + get_patches.__defaults__[1:]
    )

    # Inlined from Methods.Geometry.Circle.rotate
    def rotate(self, angle):
        """Rotation of the Circle of angle

        Parameters
        ----------
        self : Circle
            An Circle Object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None

        Raises
        -------
        AngleRotationCircleError
            The angle must be a float or int
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise self.AngleRotationCircleError("The angle must be a float or int ")

        if angle == 0:
            return  # Nothing to do
        # check if Circle is correct"
        self.check()

        # Modification of the object from the rotation
        self.center = self.center * np.exp(1j * angle)
        if self.point_ref is not None:
            self.point_ref = self.point_ref * np.exp(1j * angle)

    # Inlined from Methods.Geometry.Circle.translate
    def translate(self, Zt):
        """Translate the Circle object

        Parameters
        ----------
        self : Circle
            An Circle object

        Zt : complex
            Complex value for translation


        Returns
        -------
        None

        Raises
        -------
        PointTranslateCircleError
            The point must be a complex number or int or float

        """
        if (
            not isinstance(Zt, complex)
            and not isinstance(Zt, int)
            and not isinstance(Zt, float)
        ):
            raise self.PointTranslateCircleError(
                "The point must be a complex number or int or float"
            )

        if Zt == 0:
            return  # Nothing to do

        # check if the Circle is correct
        self.check()

        # Modification from the translation of Circle
        if self.point_ref is not None:
            self.point_ref = self.point_ref + Zt
        self.center = self.center + Zt

    class AngleRotationCircleError(Exception):
        """ """

    class PointTranslateCircleError(Exception):
        """ """

    class RadiusCircleError(Exception):
        """ """
