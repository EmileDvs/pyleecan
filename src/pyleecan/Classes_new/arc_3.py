# Experimental dataclass generated from Generator/ClassesRef/Geometry/Arc3.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .arc import Arc
from .arc_1 import Arc1
from .arc_2 import Arc2
from .machine import ARC_NPOINT_D


@dataclass(eq=False)
class Arc3(Arc):
    """Half circle define by two points

    Attributes
    ----------
    begin : complex
        begin point of the arc
        Default: 0
    end : complex
        end of the arc
        Default: 0
    is_trigo_direction : bool
        Rotation direction of the arc
        Default: True
    """

    begin: complex = 0
    """begin point of the arc"""
    end: complex = 0
    """end of the arc"""
    is_trigo_direction: bool = True
    """Rotation direction of the arc"""

    # Inlined from Methods.Geometry.Arc3.check
    def check(self):
        """assert that the arc is correct (begin != end)

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        None

        Raises
        ------
        PointArc3Error
            The beginning point and the ending point of an Arc3
            can't be the same

        """

        if self.begin == self.end or (abs(self.begin) == 0 and abs(self.end) == 0):
            raise PointArc3Error(
                "The beginning point and the ending point of an Arc3 can't be the same"
            )

    # Inlined from Methods.Geometry.Arc3.comp_length
    def comp_length(self):
        """Compute the length of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        length: float
            length of the arc
        """

        self.check()

        R = self.comp_radius()

        # Half circle
        return float(np.pi * R)

    # Inlined from Methods.Geometry.Arc3.comp_radius
    def comp_radius(self):
        """Compute the radius of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        radius: float
            radius of the arc

        """

        self.check()

        z1 = self.begin
        z2 = self.end

        return np.abs(z1 - z2) / 2.0  # Radius of the arc

    # Inlined from Methods.Geometry.Arc3.discretize
    def discretize(self, nb_point=ARC_NPOINT_D):
        """Return the discretize version of the Arc.
        Begin and end are always return

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        nb_point : int
            Number of points to add to discretize the arc (Default value = ARC_NPOINT_D)

        Returns
        -------
        list_point: list
            list of complex coordinate of the points

        Raises
        ------
        NbPointArc1DError
            nb_point must be an integer >=0
        """

        # Check that the Arc is correct
        self.check()
        if not isinstance(nb_point, int):
            raise NbPointArc3DError("discretize : nb_point must be an integer")
        if nb_point < 0:
            raise NbPointArc3DError("nb_point must be >=0")

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.get_center()
        R = self.comp_radius()

        # Generation of the point by rotation
        if self.is_trigo_direction:  # Top
            t = np.linspace(0, np.pi, nb_point + 2)
        else:  # Bottom
            t = np.linspace(0, -np.pi, nb_point + 2)
        list_point = R * np.exp(1j * t)

        # Geometric transformation : return to the main axis
        list_point = list_point * np.exp(1j * np.angle(z1 - zc)) + zc

        return list_point

    # Inlined from Methods.Geometry.Arc3.get_angle
    def get_angle(self, is_deg=False):
        """Return the angle of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        is_deg: bool
            True to convert to degree

        Returns
        -------
        angle: float
            Angle of the arc
        """

        if self.is_trigo_direction:
            sign = 1
        else:
            sign = -1

        if is_deg:
            return sign * 180
        else:
            return sign * np.pi

    # Inlined from Methods.Geometry.Arc3.get_begin
    def get_begin(self):
        """Return the begin point of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        begin: complex
            Begin point of the Arc3
        """

        return self.begin

    # Inlined from Methods.Geometry.Arc3.get_center
    def get_center(self):
        """Return the center of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        Zc: complex
            Complex coordinates of the center of the Arc3
        """

        self.check()

        # the center is on the bisection of [begin, end]
        z1 = self.begin
        z2 = self.end

        Zc = (z1 + z2) / 2.0

        # Return (0,0) if the point is too close from 0
        if np.abs(Zc) < 1e-6:
            Zc = 0

        return Zc

    # Inlined from Methods.Geometry.Arc3.get_end
    def get_end(self):
        """Return the end point of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        end: complex
            Complex coordinates of the end point of the Arc3
        """

        return self.end

    # Inlined from Methods.Geometry.Arc3.get_middle
    def get_middle(self):
        """Return the point at the middle of the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        Zmid: complex
            Complex coordinates of the middle of the Arc3
        """

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.get_center()
        R = self.comp_radius()

        # Generation of the point by rotation
        if self.is_trigo_direction:  # Top
            Zmid = R * np.exp(1j * np.pi / 2.0)
        else:  # Bottom
            Zmid = R * np.exp(-1j * np.pi / 2.0)

        # Geometric transformation : return to the main axis
        Zmid = Zmid * np.exp(1j * np.angle(z1 - zc)) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(Zmid) < 1e-6:
            Zmid = 0

        return Zmid

    # Inlined from Methods.Geometry.Arc3.reverse
    def reverse(self):
        """Reverse the begin and end point of the Line

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Returns
        -------
        """

        end = self.end
        self.end = self.begin
        self.begin = end
        self.is_trigo_direction = not self.is_trigo_direction

    # Inlined from Methods.Geometry.Arc3.rotate
    def rotate(self, angle):
        """Rotation of the Arc3 of angle

        Parameters
        ----------
        self : Arc3
            An Arc3 Object

        angle : float
            the angle of rotation [rad]


        Returns
        -------
        None
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise AngleRotationArc3Error("The angle must be a float or int ")

        # check if Arc3 is correct"
        self.check()

        # Modification from the rotation  of the object
        self.begin = self.begin * np.exp(1j * angle)
        self.end = self.end * np.exp(1j * angle)

    # Inlined from Methods.Geometry.Arc3.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the begin/end

        Parameters
        ----------
        self : Arc3
            An Arc3 Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        self.begin = self.begin * scale_factor
        self.end = self.end * scale_factor

    # Inlined from Methods.Geometry.Arc3.split_half
    def split_half(self, is_begin=True):
        """Cut the line in half (modify the object Arc3 => Arc2)

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        is_begin : bool
            True to keep the part begin=>middle, False for the part middle=>end

        Returns
        -------
        """

        if self.is_trigo_direction:
            sign = 1
        else:
            sign = -1

        if is_begin:
            arc = Arc2(
                begin=self.begin, center=self.get_center(), angle=sign * np.pi / 2
            )
        else:
            arc = Arc2(
                begin=self.get_middle(),
                center=self.get_center(),
                angle=sign * np.pi / 2,
            )
        # Change the object type from Arc3 => Arc2
        self.__class__ = Arc2
        self.__dict__.update(arc.__dict__)

    # Inlined from Methods.Geometry.Arc3.split_point
    def split_point(self, Z1, is_begin=True):
        """Cut the Arc according to a point on the arc

        Parameters
        ----------
        self : Arc3
            An Arc3 object
        Z1 : complex
            Cutting point on the line
        is_begin : bool
            True to keep the part begin=>Z1, False for the part Z1=>end

        Returns
        -------
        """

        # Check if the point is on the circle
        Zc = self.get_center()
        R = self.comp_radius()
        if abs(np.abs(Z1 - Zc) - R) > 1e-6:
            raise Exception("Point is not on the line")

        if is_begin:
            arc = Arc1(
                begin=self.begin,
                end=Z1,
                radius=R,
                is_trigo_direction=self.is_trigo_direction,
            )
        else:
            arc = Arc1(
                begin=Z1,
                end=self.end,
                radius=R,
                is_trigo_direction=self.is_trigo_direction,
            )
        # Correct radius sign if needed
        if arc.get_angle() > np.pi:
            arc.radius *= -1

        # Change the object type from Arc3 => Arc1
        self.__class__ = Arc1
        self.__dict__.update(arc.__dict__)

    # Inlined from Methods.Geometry.Arc3.translate
    def translate(self, Zt):
        """Translate the Arc3 object with

        Parameters
        ----------
        self : Arc3
            An Arc3 object

        Zt : complex
            Complex value for translation


        Returns
        -------
        None

        """
        if (
            not isinstance(Zt, complex)
            and not isinstance(Zt, int)
            and not isinstance(Zt, float)
        ):
            raise PointTranslateArc3Error(
                "The point must be a complex number or int or float"
            )

        # check if the Arc3 is correct
        self.check()

        # Modification from the translation of Arc3
        self.begin = self.begin + Zt
        self.end = self.end + Zt

    class PointArc3Error(Exception):
        """ """

    class NbPointArc3DError(Exception):
        """ """

    class AngleRotationArc3Error(Exception):
        """ """

    class PointTranslateArc3Error(Exception):
        """ """


PointArc3Error = Arc3.PointArc3Error
NbPointArc3DError = Arc3.NbPointArc3DError
AngleRotationArc3Error = Arc3.AngleRotationArc3Error
PointTranslateArc3Error = Arc3.PointTranslateArc3Error
